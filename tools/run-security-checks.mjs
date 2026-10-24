/** Targeted real MFA/security integration plus all API coding checks. */
import {runApiChecks} from './api-checks.mjs';
runApiChecks({
  feature:'FEAT-003',sprint:'S01',slug:'account-security',requireNoSkips:true,
  pytestSelection:['tests/test_runtime_mfa.py','tests/test_runtime_staff.py::test_staff_api_016_deferred_commit_failure_is_not_reported_as_http_success'],
  sourceAcceptanceCases:'MFA and commit-boundary integration only; complete provider/account-recovery source acceptance and UAT remain pending',
  mappings:[{cases:['SECURITY-MFA','SECURITY-COMMIT'],coverage:'Real encrypted enrollment, self-RLS, current session/scope, TOTP replay, one-use recovery race, persistent throttling, revocation and immediate/deferred audit rollback'}],
});
