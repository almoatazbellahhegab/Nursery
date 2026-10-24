"""Reset only the dedicated fictional MFA browser account in owned nursery_dev.

Does not reset the development database, ordinary review accounts or audit.
Generated password remains in an ignored local file, never standard output.
"""

import json
import secrets
from pathlib import Path

import psycopg

from nursery_api.runtime.bootstrap import identifier
from nursery_api.runtime.security import password_hash

ROOT = Path(__file__).resolve().parents[1]
EMAIL = "security@garden.example.test"
user = identifier(EMAIL)
org = identifier("garden")
runtime = json.loads((ROOT / ".tools/database-runtime.json").read_text())
file = ROOT / ".tools/security-accounts.json"
accounts = json.loads(file.read_text()) if file.exists() else {}
password = accounts.setdefault(EMAIL, secrets.token_urlsafe(24))
with psycopg.connect(runtime["dev_owner_url"]) as connection:
    if connection.execute("SELECT current_database()").fetchone() != ("nursery_dev",):
        raise RuntimeError("Refusing to modify anything except the owned nursery_dev fixture")
    organization = connection.execute("SELECT name FROM app.organizations WHERE id=%s", (org,)).fetchone()
    if organization is None or "fictional" not in organization[0]:
        raise RuntimeError("Dedicated fictional organization is required")
    existing = connection.execute("SELECT id FROM app.users WHERE email=%s", (EMAIL,)).fetchone()
    if existing is not None and existing != (user,):
        raise RuntimeError("Refusing to replace a different identity")
    connection.execute(
        "INSERT INTO app.users(id,email,password_hash) VALUES(%s,%s,%s) ON CONFLICT(id) "
        "DO UPDATE SET password_hash=excluded.password_hash,active=true", (user,EMAIL,password_hash(password)),
    )
    connection.execute("INSERT INTO app.memberships VALUES(%s,%s,'administrator',true) "
        "ON CONFLICT(organization_id,user_id) DO UPDATE SET role='administrator',active=true",(org,user))
    connection.execute("INSERT INTO app.branch_memberships VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",(org,user,identifier("gardenmaadi")))
    connection.execute("UPDATE app.sessions SET revoked=true WHERE user_id=%s",(user,))
    for table in ("auth_receipts","mfa_recovery_codes","mfa_enrollments"):
        connection.execute(f"DELETE FROM app.{table} WHERE user_id=%s",(user,))
file.write_text(json.dumps(accounts,indent=2))
print("Dedicated fictional security account prepared; generated credentials remain ignored.")
