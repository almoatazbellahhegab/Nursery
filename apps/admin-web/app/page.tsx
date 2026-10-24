"use client";
/** Connected workspace; authorization and filtering remain server-owned. */
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import BranchManager from "./branch-manager";

type Profile = {
  role: string;
  csrf_token: string;
  organization: { name: string };
  branches: { id: string; name: string; active: boolean; timezone: string }[];
};
type Employee = {
  id: string;
  display_name: string;
  active: boolean;
  version: number;
  open_branch_id: string | null;
  open_session_id: string | null;
};
type Event = {
  id: string;
  action: string;
  occurred_at: string;
  effective_at: string;
};
type History = {
  events: Event[];
  corrections: {
    id: string;
    original_at: string;
    corrected_at: string;
    reason: string;
  }[];
  truncated: boolean;
};
type Report = {
  timezone: string;
  items: {
    employee_id: string;
    display_name: string;
    seconds_present: number;
    data_truncated: boolean;
  }[];
};

function operationId() {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const text = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join(
    "",
  );
  return `${text.slice(0, 8)}-${text.slice(8, 12)}-${text.slice(12, 16)}-${text.slice(16, 20)}-${text.slice(20)}`;
}

export default function Workspace() {
  const sessionGeneration = useRef(0);
  const [ar, setAr] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [branch, setBranch] = useState("");
  const [rows, setRows] = useState<Employee[]>([]);
  const [selected, setSelected] = useState<Employee | null>(null);
  const [history, setHistory] = useState<History | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [day, setDay] = useState(() =>
    new Intl.DateTimeFormat("en-CA", { timeZone: "Africa/Cairo" }).format(
      new Date(),
    ),
  );
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [eventId, setEventId] = useState("");
  const [corrected, setCorrected] = useState("");
  const [reason, setReason] = useState("");
  const t = (en: string, arabic: string) => (ar ? arabic : en);
  const canUseStaff =
    !!profile &&
    ["administrator", "branch_manager", "teacher"].includes(profile.role);
  const canCorrect =
    !!profile && ["administrator", "branch_manager"].includes(profile.role);
  const readable = (value: string) =>
    new Intl.DateTimeFormat(ar ? "ar-EG" : "en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone:
        profile?.branches.find((item) => item.id === branch)?.timezone ??
        "Africa/Cairo",
    }).format(new Date(value));

  async function api<T>(path: string, body?: object): Promise<T> {
    const generation = sessionGeneration.current;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (body) {
      headers["X-CSRF-Token"] = profile?.csrf_token ?? "";
      headers["Idempotency-Key"] = operationId();
    }
    const response = await fetch(`/api/v1/${path}`, {
      method: body ? "POST" : "GET",
      headers,
      credentials: "same-origin",
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(15000),
    });
    if (generation !== sessionGeneration.current)
      throw new Error("session_changed");
    if (response.status === 401 && path !== "auth/login") {
      setProfile(null);
      setRows([]);
    }
    const data = response.status === 204 ? {} : await response.json();
    if (generation !== sessionGeneration.current)
      throw new Error("session_changed");
    if (!response.ok) throw new Error(data.code ?? "service_unavailable");
    return data as T;
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setMessage("");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      if (code === "session_changed") return;
      setMessage(
        code === "invalid_credentials"
          ? t("Check your email and password.", "تحقق من البريد وكلمة المرور.")
          : code === "staff_attendance_version_conflict"
            ? t(
                "The record changed. Refresh and try again.",
                "تغير السجل. حدّث البيانات وحاول مجدداً.",
              )
            : code === "staff_correction_denied"
              ? t(
                  "You cannot correct your own record or this employee.",
                  "لا يمكنك تصحيح سجلك أو سجل هذا الموظف.",
                )
              : t(
                  "The action could not be completed. Refresh and try again.",
                  "تعذر إتمام الإجراء. حدّث البيانات وحاول مجدداً.",
                ),
      );
    } finally {
      setBusy(false);
    }
  }
  async function load(): Promise<Employee[]> {
    const data = await api<{ items: Employee[] }>(
      `staff-attendance/employees?branch_id=${branch}`,
    );
    setRows(data.items);
    return data.items;
  }
  async function showHistory(employee: Employee) {
    setHistory(null);
    setSelected(employee);
    setEventId("");
    setCorrected("");
    setReason("");
    setHistory(
      await api<History>(
        `staff-attendance/history?branch_id=${branch}&employee_id=${employee.id}`,
      ),
    );
  }
  useEffect(() => {
    document.documentElement.lang = ar ? "ar" : "en";
    document.documentElement.dir = ar ? "rtl" : "ltr";
  }, [ar]);
  useEffect(() => {
    let active = true;
    const generation = sessionGeneration.current;
    fetch("/api/v1/auth/me", { credentials: "same-origin" })
      .then(async (response) => {
        if (response.ok && active) {
          const data: Profile = await response.json();
          if (!active || generation !== sessionGeneration.current) return;
          setProfile(data);
          setBranch(data.branches[0]?.id ?? "");
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    let active = true;
    if (canUseStaff && branch)
      fetch(`/api/v1/staff-attendance/employees?branch_id=${branch}`, {
        credentials: "same-origin",
      })
        .then(async (response) => {
          if (!response.ok) throw new Error("load_failed");
          const data: { items: Employee[] } = await response.json();
          if (active) setRows(data.items);
        })
        .catch(() => {
          if (active)
            setMessage("Unable to load attendance / تعذر تحميل الحضور");
        });
    return () => {
      active = false;
    };
  }, [canUseStaff, branch]);
  function signIn(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      sessionGeneration.current++;
      const data = await api<Profile>("auth/login", { email, password });
      setPassword("");
      setProfile(data);
      setBranch(data.branches[0]?.id ?? "");
    });
  }
  function change(employee: Employee) {
    void run(async () => {
      await api("staff-attendance/transitions", {
        employee_id: employee.id,
        branch_id: branch,
        action: employee.open_session_id ? "check_out" : "check_in",
        expected_version: employee.version,
      });
      const updated = await load();
      if (selected?.id === employee.id)
        await showHistory(
          updated.find((item) => item.id === employee.id) ?? employee,
        );
      setMessage(t("Attendance saved.", "تم حفظ الحضور."));
    });
  }
  function saveCorrection(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    void run(async () => {
      await api("staff-attendance/corrections", {
        employee_id: selected.id,
        branch_id: branch,
        event_id: eventId,
        expected_version: selected.version,
        corrected_at: new Date(corrected).toISOString(),
        reason,
      });
      const updated = await load();
      await showHistory(
        updated.find((item) => item.id === selected.id) ?? selected,
      );
      setMessage(
        t(
          "Correction saved; the original is retained.",
          "حُفظ التصحيح مع الاحتفاظ بالأصل.",
        ),
      );
    });
  }
  return (
    <main className="workspace">
      <header className="workspace-header">
        <Link className="workspace-brand" href="/">
          🌿 {t("Nursery", "الحضانة")}
        </Link>
        <div>
          <button onClick={() => setAr(!ar)}>
            {ar ? "English" : "العربية"}
          </button>
          {profile && (
            <button
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  sessionGeneration.current++;
                  await api("auth/logout", {});
                  setProfile(null);
                  setRows([]);
                  setHistory(null);
                  setSelected(null);
                  setReport(null);
                })
              }
            >
              {t("Sign out", "تسجيل الخروج")}
            </button>
          )}
        </div>
      </header>
      {message && (
        <div className="workspace-message" role="status">
          {message}
        </div>
      )}
      {!profile ? (
        <section className="workspace-login">
          <span className="eyebrow">
            {t("YOUR NURSERY WORKSPACE", "مساحة عمل الحضانة")}
          </span>
          <h1>{t("Welcome back.", "مرحباً بعودتك.")}</h1>
          <p>
            {t(
              "Sign in to your organization's workspace.",
              "سجّل الدخول إلى مساحة عمل مؤسستك.",
            )}
          </p>
          <form onSubmit={signIn}>
            <label>
              {t("Email", "البريد الإلكتروني")}
              <input
                type="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                dir="ltr"
              />
            </label>
            <label>
              {t("Password", "كلمة المرور")}
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>
            <button className="primary" disabled={busy}>
              {busy ? t("Signing in…", "جارٍ الدخول…") : t("Sign in", "دخول")}
            </button>
          </form>
          <Link href="/demo">
            {t(
              "Explore the fictional presentation demo",
              "استكشف العرض التجريبي الخيالي",
            )}
          </Link>
        </section>
      ) : (
        <>
          <section className="workspace-heading">
            <div>
              <span className="eyebrow">{profile.organization.name}</span>
              <h1>{t("Staff attendance", "حضور الموظفين")}</h1>
              <p>
                {t(
                  "A clear record of who's here, with every change accounted for.",
                  "سجل واضح للحضور مع توثيق كل تغيير.",
                )}
              </p>
            </div>
            <label>
              {t("Branch", "الفرع")}
              <select
                aria-label={t("Branch", "الفرع")}
                value={branch}
                disabled={busy}
                onChange={(e) => {
                  setBranch(e.target.value);
                  setSelected(null);
                  setHistory(null);
                  setReport(null);
                }}
              >
                {profile.branches.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                    {!b.active ? t(" · inactive", " · غير نشط") : ""}
                  </option>
                ))}
              </select>
            </label>
          </section>
          {profile.role === "administrator" && (
            <BranchManager
              api={api}
              ar={ar}
              onChanged={async () => {
                const current = await api<Profile>("auth/me");
                setProfile(current);
                if (!current.branches.some((item) => item.id === branch))
                  setBranch(current.branches[0]?.id ?? "");
              }}
            />
          )}
          {!canUseStaff ? (
            <section className="panel">
              <h2>
                {t(
                  "This account does not have staff workspace access.",
                  "لا يملك هذا الحساب صلاحية مساحة الموظفين.",
                )}
              </h2>
            </section>
          ) : (
            <>
              <section className="workspace-toolbar">
                <label>
                  {t("Find an employee", "ابحث عن موظف")}
                  <input
                    type="search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </label>
                <button
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      const updated = await load();
                      if (selected)
                        await showHistory(
                          updated.find((item) => item.id === selected.id) ??
                            selected,
                        );
                    })
                  }
                >
                  {t("Refresh", "تحديث")}
                </button>
                <label>
                  {t("Report date", "تاريخ التقرير")}
                  <input
                    type="date"
                    value={day}
                    onChange={(e) => setDay(e.target.value)}
                  />
                </label>
                <button
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      setReport(
                        await api<Report>(
                          `staff-attendance/daily?branch_id=${branch}&day=${day}`,
                        ),
                      );
                    })
                  }
                >
                  {t("Daily report", "التقرير اليومي")}
                </button>
              </section>
              <section
                className="workspace-roster"
                aria-label={t("Employee roster", "قائمة الموظفين")}
              >
                {rows
                  .filter((e) =>
                    e.display_name.toLowerCase().includes(search.toLowerCase()),
                  )
                  .map((employee) => (
                    <article className="panel" key={employee.id}>
                      <div className="workspace-person">
                        <span
                          className={`workspace-dot ${employee.open_session_id ? "present" : ""}`}
                        />
                        <h2>{employee.display_name}</h2>
                      </div>
                      <p>
                        {employee.open_session_id
                          ? employee.open_branch_id === branch
                            ? t("Present", "حاضر")
                            : t("Present at another branch", "حاضر بفرع آخر")
                          : t("Not checked in", "لم يسجل الحضور")}
                      </p>
                      <div className="workspace-actions">
                        <button
                          className="primary"
                          disabled={
                            busy ||
                            !profile.branches.find((item) => item.id === branch)
                              ?.active ||
                            !employee.active ||
                            (!!employee.open_session_id &&
                              employee.open_branch_id !== branch)
                          }
                          onClick={() => change(employee)}
                        >
                          {employee.open_session_id
                            ? t("Check out", "تسجيل الانصراف")
                            : t("Check in", "تسجيل الحضور")}
                        </button>
                        <button
                          disabled={busy}
                          onClick={() => void run(() => showHistory(employee))}
                        >
                          {t("History", "السجل")}
                        </button>
                      </div>
                    </article>
                  ))}
              </section>
              {rows.length === 0 && (
                <p>
                  {t(
                    "No assigned employees in this branch.",
                    "لا يوجد موظفون مسندون لهذا الفرع.",
                  )}
                </p>
              )}
              {selected && history && (
                <section className="panel workspace-history">
                  <h2>
                    {selected.display_name} · {t("History", "السجل")}
                  </h2>
                  {history.events.length === 0 && (
                    <p>
                      {t("No attendance recorded yet.", "لم يُسجل حضور بعد.")}
                    </p>
                  )}
                  <ol>
                    {history.events.map((event) => (
                      <li key={event.id}>
                        <strong>
                          {event.action === "check_in"
                            ? t("Check in", "حضور")
                            : t("Check out", "انصراف")}
                        </strong>{" "}
                        · {readable(event.effective_at)}
                        {event.effective_at !== event.occurred_at && (
                          <span> · {t("Corrected", "مصحح")}</span>
                        )}
                      </li>
                    ))}
                  </ol>
                  {history.truncated && (
                    <p>
                      {t(
                        "Showing a partial history window.",
                        "يُعرض نطاق جزئي للسجل.",
                      )}
                    </p>
                  )}
                  {canCorrect && history.events.length > 0 && (
                    <form
                      className="workspace-correction"
                      onSubmit={saveCorrection}
                    >
                      <h3>{t("Correct a time", "تصحيح وقت")}</h3>
                      <label>
                        {t("Record", "السجل")}
                        <select
                          aria-label={t("Record", "السجل")}
                          required
                          value={eventId}
                          onChange={(e) => setEventId(e.target.value)}
                        >
                          <option value="">
                            {t("Select a record", "اختر سجلاً")}
                          </option>
                          {history.events.map((event) => (
                            <option key={event.id} value={event.id}>
                              {event.action} · {readable(event.effective_at)}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label>
                        {t(
                          "Correct time (your device timezone)",
                          "الوقت الصحيح (بتوقيت جهازك)",
                        )}
                        <input
                          type="datetime-local"
                          step="1"
                          required
                          value={corrected}
                          onChange={(e) => setCorrected(e.target.value)}
                        />
                      </label>
                      <label>
                        {t("Reason", "السبب")}
                        <input
                          required
                          minLength={3}
                          maxLength={500}
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                        />
                      </label>
                      <button disabled={busy} className="primary">
                        {t("Save correction", "حفظ التصحيح")}
                      </button>
                    </form>
                  )}
                  <h3>{t("Correction history", "سجل التصحيحات")}</h3>
                  {history.corrections.map((c) => (
                    <p key={c.id}>
                      {readable(c.original_at)} → {readable(c.corrected_at)} ·{" "}
                      {c.reason}
                    </p>
                  ))}
                </section>
              )}
              {report && (
                <section className="panel">
                  <h2>
                    {t("Daily presence", "الحضور اليومي")} · {day}
                  </h2>
                  <p>{report.timezone}</p>
                  {report.items.map((item) => (
                    <p key={item.employee_id}>
                      <strong>{item.display_name}</strong> ·{" "}
                      {Math.floor(item.seconds_present / 60)}{" "}
                      {t("minutes", "دقيقة")}
                      {item.data_truncated &&
                        ` · ${t("Partial data", "بيانات جزئية")}`}
                    </p>
                  ))}
                </section>
              )}
            </>
          )}
        </>
      )}
    </main>
  );
}
