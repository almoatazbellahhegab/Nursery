"use client";
import { FormEvent, useState } from "react";

type Branch = {
  id: string;
  name: string;
  timezone: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  capacity: number | null;
  operating_status: string;
  active: boolean;
  version: number;
};
type Member = { user_id: string; email: string; role: string };
type Page<T> = { items: T[]; next_cursor: string | null };
type Api = <T>(path: string, body?: object) => Promise<T>;
const initial = {
  name: "",
  timezone: "Africa/Cairo",
  contact_email: "",
  contact_phone: "",
  address: "",
  capacity: null as number | null,
  operating_status: "open",
  active: true,
};

export default function BranchManager({
  api,
  ar,
  onChanged,
}: {
  api: Api;
  ar: boolean;
  onChanged: () => Promise<void>;
}) {
  const t = (en: string, arabic: string) => (ar ? arabic : en);
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<Branch[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [memberCursor, setMemberCursor] = useState<string | null>(null);
  const [member, setMember] = useState("");
  const [assigned, setAssigned] = useState<string[]>([]);
  const [assignmentCursor, setAssignmentCursor] = useState<string | null>(null);
  const [selected, setSelected] = useState<Branch | null>(null);
  const [form, setForm] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setMessage("");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      setMessage(
        code === "branch_version_conflict"
          ? t(
              "This branch changed. Reopen it before saving.",
              "تغير الفرع. أعد فتحه قبل الحفظ.",
            )
          : t(
              "Unable to save. Check the fields and refresh before retrying.",
              "تعذر الحفظ. تحقق من الحقول وحدّث البيانات قبل المحاولة.",
            ),
      );
    } finally {
      setBusy(false);
    }
  }
  async function load(next?: string) {
    const data = await api<Page<Branch>>(
      `branches${next ? `?cursor=${next}` : ""}`,
    );
    setItems((current) => (next ? [...current, ...data.items] : data.items));
    setCursor(data.next_cursor);
  }
  async function loadMembers(next?: string) {
    const data = await api<Page<Member>>(
      `branches/members${next ? `?cursor=${next}` : ""}`,
    );
    setMembers((current) => (next ? [...current, ...data.items] : data.items));
    setMemberCursor(data.next_cursor);
  }
  async function edit(item: Branch) {
    setSelected(item);
    setForm({ ...item });
    setMember("");
    const data = await api<Page<{ user_id: string }>>(
      `branches/${item.id}/members`,
    );
    setAssigned(data.items.map((row) => row.user_id));
    setAssignmentCursor(data.next_cursor);
  }
  function save(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      const {
        name,
        timezone,
        contact_email,
        contact_phone,
        address,
        capacity,
        operating_status,
        active,
      } = form;
      const body = {
        name,
        timezone,
        contact_email,
        contact_phone,
        address,
        capacity,
        operating_status,
        active,
      };
      const result = await api<Branch>(
        selected ? `branches/${selected.id}` : "branches",
        selected ? { ...body, expected_version: selected.version } : body,
      );
      await load();
      await edit(result);
      await onChanged();
      setMessage(t("Branch saved.", "تم حفظ الفرع."));
    });
  }
  function assign(value: boolean) {
    if (!selected || !member) return;
    void run(async () => {
      await api(`branches/${selected.id}/members`, {
        user_id: member,
        assigned: value,
        expected_version: selected.version,
      });
      await load();
      await edit(await api<Branch>(`branches/${selected.id}`));
      await onChanged();
      setMessage(
        t(
          "Assignment saved. Access uses the current assignment.",
          "تم حفظ التكليف وتحديث صلاحية الوصول.",
        ),
      );
    });
  }
  return (
    <section className="panel branch-manager">
      <button
        disabled={busy}
        onClick={() =>
          void run(async () => {
            if (!open) {
              await load();
              await loadMembers();
            }
            setOpen(!open);
          })
        }
      >
        {open
          ? t("Close branch settings", "إغلاق إعدادات الفروع")
          : t("Manage branches", "إدارة الفروع")}
      </button>
      {open && (
        <>
          <h2>{t("Branches", "الفروع")}</h2>
          {message && <p role="status">{message}</p>}
          <div className="workspace-actions">
            {items.map((item) => (
              <button
                disabled={busy}
                key={item.id}
                onClick={() => void run(() => edit(item))}
              >
                {item.name}
                {!item.active ? t(" · inactive", " · غير نشط") : ""}
              </button>
            ))}
            {cursor && (
              <button
                disabled={busy}
                onClick={() => void run(() => load(cursor))}
              >
                {t("More branches", "المزيد من الفروع")}
              </button>
            )}
            <button
              disabled={busy}
              onClick={() => {
                setSelected(null);
                setForm(initial);
                setAssigned([]);
              }}
            >
              {t("New branch", "فرع جديد")}
            </button>
          </div>
          <h3>
            {selected
              ? t("Edit branch", "تعديل الفرع")
              : t("Create branch", "إنشاء فرع")}
          </h3>
          <form onSubmit={save} className="workspace-correction">
            <label>
              {t("Branch name", "اسم الفرع")}
              <input
                required
                maxLength={160}
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </label>
            <label>
              {t("Timezone", "المنطقة الزمنية")}
              <input
                required
                dir="ltr"
                value={form.timezone}
                onChange={(e) => setForm({ ...form, timezone: e.target.value })}
              />
            </label>
            <label>
              {t("Branch email", "بريد الفرع")}
              <input
                type="email"
                dir="ltr"
                maxLength={254}
                value={form.contact_email}
                onChange={(e) =>
                  setForm({ ...form, contact_email: e.target.value })
                }
              />
            </label>
            <label>
              {t("Branch phone", "هاتف الفرع")}
              <input
                type="tel"
                dir="ltr"
                maxLength={40}
                value={form.contact_phone}
                onChange={(e) =>
                  setForm({ ...form, contact_phone: e.target.value })
                }
              />
            </label>
            <label>
              {t("Address", "العنوان")}
              <input
                maxLength={500}
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
              />
            </label>
            <label>
              {t("Capacity context", "السعة الاسترشادية")}
              <input
                type="number"
                min={1}
                max={10000}
                value={form.capacity ?? ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    capacity: e.target.value ? Number(e.target.value) : null,
                  })
                }
              />
            </label>
            <p>
              {t(
                "Branch capacity is planning context. Classroom capacity is enforced during enrollment.",
                "سعة الفرع استرشادية للتخطيط. يتم التحقق من سعة الفصل عند التسجيل.",
              )}
            </p>
            <label>
              {t("Operating status", "حالة التشغيل")}
              <select
                aria-label={t("Operating status", "حالة التشغيل")}
                value={form.operating_status}
                onChange={(e) =>
                  setForm({ ...form, operating_status: e.target.value })
                }
              >
                <option value="open">{t("Open", "مفتوح")}</option>
                <option value="planned">{t("Planned", "مخطط")}</option>
                <option value="temporarily_closed">
                  {t("Temporarily closed", "مغلق مؤقتاً")}
                </option>
              </select>
            </label>
            <label className="workspace-checkbox">
              <input
                type="checkbox"
                checked={form.active}
                onChange={(e) => setForm({ ...form, active: e.target.checked })}
              />
              {t("Active for new records", "نشط للسجلات الجديدة")}
            </label>
            <button className="primary" disabled={busy}>
              {t("Save branch", "حفظ الفرع")}
            </button>
          </form>
          {selected && (
            <div className="workspace-correction">
              <h3>{t("Branch access", "صلاحيات الفرع")}</h3>
              <p>
                {t(
                  "Branch access does not replace classroom, child or employee assignments.",
                  "صلاحية الفرع لا تستبدل تكليفات الفصل أو الطفل أو الموظف.",
                )}
              </p>
              <ul>
                {assigned.map((id) => (
                  <li key={id}>
                    {members.find((m) => m.user_id === id)?.email ?? id}
                  </li>
                ))}
              </ul>
              {assignmentCursor && (
                <button
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      const page = await api<Page<{ user_id: string }>>(
                        `branches/${selected.id}/members?cursor=${assignmentCursor}`,
                      );
                      setAssigned((current) => [
                        ...current,
                        ...page.items.map((row) => row.user_id),
                      ]);
                      setAssignmentCursor(page.next_cursor);
                    })
                  }
                >
                  {t("More assignments", "المزيد من التكليفات")}
                </button>
              )}
              <label>
                {t("Organization member", "عضو المؤسسة")}
                <select
                  aria-label={t("Organization member", "عضو المؤسسة")}
                  value={member}
                  onChange={(e) => setMember(e.target.value)}
                >
                  <option value="">{t("Choose a member", "اختر عضواً")}</option>
                  {members.map((m) => (
                    <option key={m.user_id} value={m.user_id}>
                      {m.email} · {m.role}
                    </option>
                  ))}
                </select>
              </label>
              {memberCursor && (
                <button
                  disabled={busy}
                  onClick={() => void run(() => loadMembers(memberCursor))}
                >
                  {t("More members", "المزيد من الأعضاء")}
                </button>
              )}
              <div className="workspace-actions">
                <button
                  disabled={busy || !member || !selected.active}
                  onClick={() => assign(true)}
                >
                  {t("Assign branch", "إضافة للفرع")}
                </button>
                <button
                  disabled={busy || !member}
                  onClick={() => assign(false)}
                >
                  {t("Remove branch access", "إزالة صلاحية الفرع")}
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
