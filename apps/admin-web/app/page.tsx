"use client";
/** FEAT-041 fictional presentation demo. Mutations stay in this page. */
import { useEffect, useState } from "react";
import seed from "./demo-data.json";
type Tab =
  | "overview"
  | "classrooms"
  | "attendance"
  | "timeline"
  | "billing"
  | "admissions";
type Label = { en: string; ar: string };
const tabs: { id: Tab; en: string; ar: string }[] = [
  { id: "overview", en: "Overview", ar: "نظرة عامة" },
  { id: "classrooms", en: "Classrooms", ar: "الفصول" },
  { id: "attendance", en: "Attendance", ar: "الحضور" },
  { id: "timeline", en: "Daily care", ar: "الرعاية اليومية" },
  { id: "billing", en: "Fees & follow-up", ar: "الرسوم والمتابعة" },
  { id: "admissions", en: "Admissions", ar: "القبول" },
];
export default function Page() {
  const [locale, setLocale] = useState<"en" | "ar">("en");
  const [data, setData] = useState(() => structuredClone(seed));
  const [branchId, setBranch] = useState("B001");
  const [tab, setTab] = useState<Tab>("overview");
  const [selectedChild, setChild] = useState("C001");
  const [search, setSearch] = useState("");
  const [unpaidOnly, setUnpaid] = useState(true);
  const [reminders, setReminders] = useState<string[]>([]);
  const [previewInvoice, setPreview] = useState<string | null>(null);
  const [guide, setGuide] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");
  const t = (en: string, ar: string) => (locale === "ar" ? ar : en);
  const label = (v: Label) => v[locale];
  const money = (minor: number) =>
    new Intl.NumberFormat(locale === "ar" ? "ar-EG" : "en-EG", {
      style: "currency",
      currency: "EGP",
      maximumFractionDigits: 0,
    }).format(minor / 100);
  const children = data.children.filter((c) => c.branchId === branchId);
  const rooms = data.classrooms.filter((c) => c.branchId === branchId);
  const invoices = data.invoices.filter((c) => c.branchId === branchId);
  const leads = data.leads.filter((c) => c.branchId === branchId);
  const present = children.filter((c) => c.status === "present").length;
  const outstanding = invoices.reduce(
    (s, i) => s + i.amountMinor - i.paidMinor,
    0,
  );
  const child = children.find((c) => c.id === selectedChild) ?? children[0];
  const branch = data.branches.find((b) => b.id === branchId)!;
  const scenario = data.scenarios.find((s) => s.id === guide);
  const invoice = invoices.find((i) => i.id === previewInvoice);
  const status = (v: string) =>
    ({
      present: t("Here now", "حاضر الآن"),
      expected: t("Expected", "متوقع وصوله"),
      home: t("Went home", "غادر"),
      absent: t("Absent", "غائب"),
    })[v];
  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
    document.title =
      locale === "ar"
        ? "الحديقة الصغيرة | عرض تجريبي"
        : "Little Garden | Client demo";
  }, [locale]);
  function reset() {
    setData(structuredClone(seed));
    setReminders([]);
    setPreview(null);
    setGuide(null);
    setBranch("B001");
    setChild("C001");
    setSearch("");
    setTab("overview");
    setUnpaid(true);
    setFeedback(
      t(
        "Demo restored. You can repeat every story.",
        "أعيد ضبط العرض. يمكنك تكرار كل قصة.",
      ),
    );
  }
  function startStory(id: string, nextTab: Tab) {
    setBranch("B001");
    setChild("C001");
    setSearch("");
    setPreview(null);
    setFeedback("");
    setGuide(id);
    setTab(nextTab);
  }
  function attendance(id: string) {
    const target = data.children.find((c) => c.id === id)!;
    const arriving = target.status === "expected";
    setData((current) => ({
      ...current,
      children: current.children.map((c) =>
        c.id === id ? { ...c, status: arriving ? "present" : "home" } : c,
      ),
      events: [
        ...current.events,
        {
          id: "demo-" + current.events.length,
          childId: id,
          branchId,
          time: "11:35",
          kind: arriving ? "arrival" : "departure",
          detail: arriving
            ? {
                en: "Arrival recorded in the demo.",
                ar: "سُجل الوصول في العرض التجريبي.",
              }
            : {
                en: "Departure recorded in the demo.",
                ar: "سُجلت المغادرة في العرض التجريبي.",
              },
          staffId: data.staff.find((s) => s.classroomId === target.classroomId)!
            .id,
        },
      ],
    }));
    setFeedback(
      t(
        "Attendance and this child’s timeline updated in this demo.",
        "حُدّث الحضور والسجل اليومي للطفل في هذا العرض.",
      ),
    );
  }
  function careUpdate() {
    setData((current) => ({
      ...current,
      events: [
        ...current.events,
        {
          id: "demo-" + current.events.length,
          childId: child.id,
          branchId,
          time: "11:35",
          kind: "care",
          detail: {
            en: "Garden play · explored leaves and colours with friends.",
            ar: "اللعب في الحديقة · استكشف الأوراق والألوان مع الأصدقاء.",
          },
          staffId: data.staff.find((s) => s.classroomId === child.classroomId)!
            .id,
        },
      ],
    }));
    setFeedback(
      t(
        "Sample update added. See the latest entry below.",
        "أُضيف تحديث تجريبي. راجع آخر إدخال أدناه.",
      ),
    );
  }
  return (
    <main>
      <div className="demo-banner">
        <span>
          {t("CLIENT DEMO · FICTIONAL DATA", "عرض للعملاء · بيانات خيالية")}
        </span>
        <span>{t("24 October 2026 · Cairo", "٢٤ أكتوبر ٢٠٢٦ · القاهرة")}</span>
      </div>
      <header>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setTab("overview");
          }}
        >
          <span className="brand-mark" aria-hidden="true">
            ✿
          </span>
          <span>
            {label(data.organization.name)}
            <small>
              {t("A little care. A big difference.", "رعاية صغيرة. أثر كبير.")}
            </small>
          </span>
        </a>
        <div className="header-actions">
          <button onClick={reset}>{t("Reset demo", "إعادة ضبط العرض")}</button>
          <button
            onClick={() => {
              setFeedback("");
              setLocale(locale === "en" ? "ar" : "en");
            }}
          >
            {t("العربية", "English")}
          </button>
        </div>
      </header>
      <div className="context-bar">
        <label>
          {t("Explore a branch", "استكشف فرعاً")}
          <select
            aria-label={t("Branch", "الفرع")}
            value={branchId}
            onChange={(e) => {
              const id = e.target.value;
              setBranch(id);
              setGuide(null);
              setChild(data.children.find((c) => c.branchId === id)!.id);
              setSearch("");
              setPreview(null);
              setFeedback("");
            }}
          >
            {data.branches.map((b) => (
              <option key={b.id} value={b.id}>
                {label(b.name)}
              </option>
            ))}
          </select>
        </label>
        <p>
          {t(
            "A ready-to-present nursery day. Try the stories, explore the records, then reset.",
            "يوم حضانة جاهز للعرض. جرّب القصص واستكشف السجلات ثم أعد الضبط.",
          )}
        </p>
      </div>
      <nav aria-label={t("Main navigation", "التنقل الرئيسي")}>
        {tabs.map((item) => (
          <button
            key={item.id}
            aria-current={tab === item.id ? "page" : undefined}
            onClick={() => {
              setTab(item.id);
              setSearch("");
              setFeedback("");
            }}
          >
            {label(item)}
          </button>
        ))}
      </nav>
      <div role="status" className={feedback ? "feedback" : "status-empty"}>
        {feedback}
      </div>
      {scenario && (
        <aside className="guide">
          <div>
            <span className="eyebrow">{t("YOUR DEMO STORY", "قصة العرض")}</span>
            <h2>{label(scenario.title)}</h2>
            <p>{label(scenario.steps)}</p>
          </div>
          <button onClick={() => setGuide(null)}>
            {t("Close guide", "إغلاق الدليل")}
          </button>
        </aside>
      )}
      <section className="page-content">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              {label(branch.name)} · {t("DEMO SNAPSHOT", "لقطة تجريبية")}
            </p>
            <h1>{label(tabs.find((x) => x.id === tab)!)}</h1>
          </div>
          <span className="date-chip">
            {t("Saturday, 24 October", "السبت، ٢٤ أكتوبر")}
          </span>
        </div>
        {tab === "overview" && (
          <>
            <div className="hero">
              <div>
                <p className="eyebrow">
                  {t("MORE TIME FOR LITTLE MOMENTS", "وقت أطول للحظات الصغيرة")}
                </p>
                <h2>
                  {t(
                    "Your nursery day, all together.",
                    "يوم حضانتك، في مكان واحد.",
                  )}
                </h2>
                <p>
                  {t(
                    "See the classroom picture, keep families informed and give your team a clear next step.",
                    "تابع الفصول واطمئن الأسر وحدد الخطوة التالية لفريقك.",
                  )}
                </p>
                <button
                  className="primary"
                  onClick={() => {
                    startStory("morning", "attendance");
                  }}
                >
                  {t("Start the morning story", "ابدأ قصة الصباح")} →
                </button>
              </div>
              <div className="hero-note">
                <span className="large-number" dir="ltr">
                  {present}
                  <small> / {children.length}</small>
                </span>
                <p>{t("children here now", "طفلاً حاضراً الآن")}</p>
                <span>
                  {children.filter((c) => c.status === "expected").length}{" "}
                  {t("still expected", "متوقع وصولهم")}
                </span>
              </div>
            </div>
            <div className="metrics">
              <article>
                <span>{t("Here now", "حاضرون الآن")}</span>
                <strong data-testid="present-total" dir="ltr">
                  {present} / {children.length}
                </strong>
                <small>
                  {t(
                    "Attendance from this demo branch",
                    "من حضور الفرع التجريبي",
                  )}
                </small>
              </article>
              <article>
                <span>{t("Enrolled / capacity", "المسجلون / السعة")}</span>
                <strong dir="ltr">
                  {children.length} /{" "}
                  {rooms.reduce((s, r) => s + r.capacity, 0)}
                </strong>
                <small>
                  {rooms.length} {t("classrooms to explore", "فصول للاستكشاف")}
                </small>
              </article>
              <article>
                <span>{t("Outstanding tuition", "الرسوم المستحقة")}</span>
                <strong>{money(outstanding)}</strong>
                <small>
                  {invoices.filter((i) => i.paidMinor < i.amountMinor).length}{" "}
                  {t("invoices need follow-up", "فواتير تحتاج متابعة")}
                </small>
              </article>
              <article>
                <span>{t("Admissions inquiries", "استفسارات القبول")}</span>
                <strong>{leads.length}</strong>
                <small>
                  {t(
                    "Every family has an owner and next step",
                    "مسؤول وخطوة تالية لكل أسرة",
                  )}
                </small>
              </article>
            </div>
            <h2>
              {t("Four stories to show the value", "أربع قصص توضح القيمة")}
            </h2>
            <div className="scenario-grid">
              {data.scenarios.map((s, i) => (
                <article className="scenario-card" key={s.id}>
                  <span className="story-number">0{i + 1}</span>
                  <h3>{label(s.title)}</h3>
                  <p>{label(s.value)}</p>
                  <button
                    onClick={() => {
                      startStory(s.id, s.tab as Tab);
                    }}
                  >
                    {t("Try this story", "جرّب هذه القصة")} →
                  </button>
                </article>
              ))}
            </div>
            <div className="split">
              <article className="panel">
                <h2>{t("A team ready for the day", "فريق مستعد لليوم")}</h2>
                {rooms.map((r) => (
                  <div className="list-row" key={r.id}>
                    <div>
                      <strong>{label(r.name)}</strong>
                      <small>
                        {data.staff
                          .filter((s) => s.classroomId === r.id)
                          .map((s) => label(s.name))
                          .join(" · ")}
                      </small>
                    </div>
                    <span className="badge">
                      {
                        children.filter(
                          (c) =>
                            c.classroomId === r.id && c.status === "present",
                        ).length
                      }{" "}
                      {t("here", "حاضر")}
                    </span>
                  </div>
                ))}
              </article>
              <article className="panel">
                <h2>
                  {t("Keep families in the loop", "أبقِ الأسرة على اطلاع")}
                </h2>
                {data.notices
                  .filter((n) => n.branchId === branchId)
                  .map((n) => (
                    <div className="notice" key={n.id}>
                      <h3>{label(n.title)}</h3>
                      <p>{label(n.body)}</p>
                    </div>
                  ))}
              </article>
            </div>
          </>
        )}
        {tab === "classrooms" && (
          <div className="split">
            {rooms.map((r) => (
              <article className="panel" key={r.id}>
                <span className="eyebrow">
                  {t("AGES", "الأعمار")} <bdi dir="ltr">{r.ages}</bdi>
                </span>
                <h2>{label(r.name)}</h2>
                <p>
                  {t("Educators", "المعلمات")}:{" "}
                  {data.staff
                    .filter((s) => s.classroomId === r.id)
                    .map((s) => label(s.name))
                    .join(" · ")}
                </p>
                <p>
                  {children.filter((c) => c.classroomId === r.id).length} /{" "}
                  {r.capacity} {t("places occupied", "أماكن مشغولة")}
                </p>
                {children
                  .filter((c) => c.classroomId === r.id)
                  .map((c) => (
                    <div className="list-row" key={c.id}>
                      <button
                        className="text-button"
                        onClick={() => {
                          setChild(c.id);
                          setTab("timeline");
                        }}
                      >
                        {label(c.name)}
                      </button>
                      <span className={"badge " + c.status}>
                        {status(c.status)}
                      </span>
                    </div>
                  ))}
              </article>
            ))}
          </div>
        )}
        {tab === "attendance" && (
          <>
            <p>
              {t(
                "Keep arrival, departure and the child’s daily story together. These actions only change this demo session.",
                "اجمع الوصول والمغادرة وقصة الطفل اليومية. تغيّر الإجراءات هذه الجلسة التجريبية فقط.",
              )}
            </p>
            <label className="search-label">
              {t("Find a child", "ابحث عن طفل")}
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t("Search by name…", "ابحث بالاسم…")}
              />
            </label>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{t("Child", "الطفل")}</th>
                    <th>{t("Classroom", "الفصل")}</th>
                    <th>{t("Status", "الحالة")}</th>
                    <th>{t("Demo action", "إجراء تجريبي")}</th>
                  </tr>
                </thead>
                <tbody>
                  {children
                    .filter((c) =>
                      label(c.name)
                        .toLowerCase()
                        .includes(search.toLowerCase()),
                    )
                    .map((c) => (
                      <tr key={c.id}>
                        <td>
                          <strong>{label(c.name)}</strong>
                          <small>
                            {label(
                              data.guardians.find((g) => g.id === c.guardianId)!
                                .name,
                            )}
                          </small>
                        </td>
                        <td>
                          {label(
                            rooms.find((r) => r.id === c.classroomId)!.name,
                          )}
                        </td>
                        <td>
                          <span className={"badge " + c.status}>
                            {status(c.status)}
                          </span>
                        </td>
                        <td>
                          {["expected", "present"].includes(c.status) ? (
                            <button
                              onClick={() => attendance(c.id)}
                              aria-label={
                                (c.status === "expected"
                                  ? t("Check in", "تسجيل وصول")
                                  : t("Check out", "تسجيل مغادرة")) +
                                " " +
                                label(c.name)
                              }
                            >
                              {c.status === "expected"
                                ? t("Check in", "تسجيل وصول")
                                : t("Check out", "تسجيل مغادرة")}
                            </button>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            {!children.some((c) =>
              label(c.name).toLowerCase().includes(search.toLowerCase()),
            ) && (
              <p>
                {t(
                  "No matching children in this branch.",
                  "لا يوجد طفل مطابق في هذا الفرع.",
                )}
              </p>
            )}
          </>
        )}
        {tab === "timeline" && (
          <>
            <div className="toolbar">
              <label>
                {t("Child", "الطفل")}
                <select
                  value={child.id}
                  onChange={(e) => setChild(e.target.value)}
                >
                  {children.map((c) => (
                    <option key={c.id} value={c.id}>
                      {label(c.name)}
                    </option>
                  ))}
                </select>
              </label>
              <button className="primary" onClick={careUpdate}>
                {t("Add sample care update", "إضافة تحديث رعاية تجريبي")}
              </button>
            </div>
            <div className="split">
              <article className="panel">
                <h2>{label(child.name)}</h2>
                <p>
                  {label(rooms.find((r) => r.id === child.classroomId)!.name)} ·{" "}
                  {status(child.status)}
                </p>
                <h3>{t("Family preview", "معاينة الأسرة")}</h3>
                <p>
                  {t(
                    "A reassuring daily picture: arrival, meals, play and a personal update from the classroom team.",
                    "صورة مطمئنة لليوم: الوصول والوجبات واللعب وتحديث من فريق الفصل.",
                  )}
                </p>
                <p className="muted">
                  {t(
                    "Mobile opens the same starting dataset. Changes in this browser are local and do not sync to the phone.",
                    "يفتح الهاتف نفس البيانات الأولية. التغييرات في هذا المتصفح محلية ولا تتزامن مع الهاتف.",
                  )}
                </p>
              </article>
              <article className="panel">
                <h2>{t("Today’s story", "قصة اليوم")}</h2>
                {data.events
                  .filter((e) => e.childId === child.id)
                  .map((e) => (
                    <div className="timeline-item" key={e.id}>
                      <time>{e.time}</time>
                      <div>
                        <p>{label(e.detail)}</p>
                        <small>
                          {label(
                            data.staff.find((s) => s.id === e.staffId)!.name,
                          )}
                        </small>
                      </div>
                    </div>
                  ))}
                {!data.events.some((e) => e.childId === child.id) && (
                  <p>
                    {t(
                      "No updates yet. Add a sample to tell this child’s story.",
                      "لا توجد تحديثات بعد. أضف تحديثاً تجريبياً لبدء قصة الطفل.",
                    )}
                  </p>
                )}
              </article>
            </div>
          </>
        )}
        {tab === "billing" && (
          <>
            <div className="section-intro">
              <p>
                {t(
                  "A clear follow-up list for the office. All figures are fictional EGP amounts and excluded from real business reporting.",
                  "قائمة متابعة واضحة للإدارة. كل المبالغ خيالية بالجنيه المصري ولا تدخل في التقارير الحقيقية.",
                )}
              </p>
              <strong>
                {money(outstanding)} {t("outstanding", "مستحقة")}
              </strong>
            </div>
            <label className="check-label">
              <input
                type="checkbox"
                checked={unpaidOnly}
                onChange={(e) => setUnpaid(e.target.checked)}
              />
              {t("Outstanding invoices only", "الفواتير المستحقة فقط")}
            </label>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{t("Family / invoice", "الأسرة / الفاتورة")}</th>
                    <th>{t("Tuition", "الرسوم")}</th>
                    <th>{t("Paid", "المدفوع")}</th>
                    <th>{t("Balance", "المتبقي")}</th>
                    <th>{t("Follow-up", "المتابعة")}</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices
                    .filter((i) => !unpaidOnly || i.paidMinor < i.amountMinor)
                    .map((i) => (
                      <tr key={i.id}>
                        <td>
                          <strong>
                            {label(
                              children.find((c) => c.id === i.childId)!.name,
                            )}
                          </strong>
                          <small>
                            {i.id} · {label(i.period)}
                          </small>
                        </td>
                        <td>{money(i.amountMinor)}</td>
                        <td>{money(i.paidMinor)}</td>
                        <td>{money(i.amountMinor - i.paidMinor)}</td>
                        <td>
                          {i.paidMinor === i.amountMinor ? (
                            <span className="badge present">
                              {t("Paid", "مدفوع")}
                            </span>
                          ) : reminders.includes(i.id) ? (
                            <span className="badge">
                              {t("Previewed locally", "تمت المعاينة محلياً")}
                            </span>
                          ) : (
                            <button
                              onClick={() => setPreview(i.id)}
                              aria-label={
                                t("Preview reminder", "معاينة تذكير") +
                                " " +
                                i.id
                              }
                            >
                              {t("Preview reminder", "معاينة تذكير")}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            {invoice && (
              <aside
                className="guide"
                aria-label={t("Reminder preview", "معاينة التذكير")}
              >
                <div>
                  <h2>{t("Reminder preview", "معاينة التذكير")}</h2>
                  <p>
                    {t(
                      "Dear family, your October tuition balance is",
                      "عزيزي ولي الأمر، المبلغ المتبقي من رسوم أكتوبر هو",
                    )}{" "}
                    {money(invoice.amountMinor - invoice.paidMinor)}.{" "}
                    {t(
                      "Please contact the nursery office if you need help.",
                      "يرجى التواصل مع إدارة الحضانة إذا احتجت مساعدة.",
                    )}
                  </p>
                  <p className="muted">
                    {t(
                      "Demo preview only. No email, SMS or payment request will be sent.",
                      "معاينة تجريبية فقط. لن تُرسل رسائل أو طلبات دفع.",
                    )}
                  </p>
                  <button
                    className="primary"
                    onClick={() => {
                      setReminders((current) => [...current, invoice.id]);
                      setPreview(null);
                      setFeedback(
                        t(
                          "Follow-up preview recorded locally. Nothing was sent.",
                          "سُجلت المعاينة محلياً. لم يُرسل شيء.",
                        ),
                      );
                    }}
                  >
                    {t("Record demo follow-up", "تسجيل متابعة تجريبية")}
                  </button>{" "}
                  <button onClick={() => setPreview(null)}>
                    {t("Close", "إغلاق")}
                  </button>
                </div>
              </aside>
            )}
          </>
        )}
        {tab === "admissions" && (
          <>
            <p>
              {t(
                "Every interested family has a next step. Sample visits are presentation scenarios; they do not enroll children or send invitations.",
                "لكل أسرة مهتمة خطوة تالية. الزيارات سيناريوهات عرض ولا تسجّل أطفالاً ولا ترسل دعوات.",
              )}
            </p>
            <div className="scenario-grid">
              {leads.map((lead) => (
                <article className="panel" key={lead.id}>
                  <span className="badge">
                    {
                      {
                        inquiry: t("New inquiry", "استفسار جديد"),
                        visit: t("Visit arranged", "زيارة محددة"),
                        application: t("Application", "طلب التحاق"),
                        waitlist: t("Waiting list", "قائمة الانتظار"),
                      }[lead.stage]
                    }
                  </span>
                  <h2>{label(lead.name)}</h2>
                  <p>
                    {label(lead.source)} · {t("Age group", "الفئة العمرية")}{" "}
                    <bdi dir="ltr">{lead.ageGroup}</bdi>
                  </p>
                  <small>
                    {t("Owner", "المسؤول")}:{" "}
                    {label(data.staff.find((s) => s.id === lead.ownerId)!.name)}
                  </small>
                  <p>
                    <strong>{t("Next step", "الخطوة التالية")}</strong>
                    <br />
                    {label(lead.nextStep)}
                  </p>
                  {lead.visitScheduled ? (
                    <p className="badge present">
                      {t(
                        "Demo visit · 27 Oct, 10:00",
                        "زيارة تجريبية · ٢٧ أكتوبر، ١٠ صباحاً",
                      )}
                    </p>
                  ) : (
                    <button
                      onClick={() => {
                        setData((current) => ({
                          ...current,
                          leads: current.leads.map((l) =>
                            l.id === lead.id
                              ? {
                                  ...l,
                                  visitScheduled: true,
                                  nextStep: {
                                    en: "Welcome the family · 27 October at 10:00",
                                    ar: "استقبال الأسرة · ٢٧ أكتوبر الساعة ١٠ صباحاً",
                                  },
                                }
                              : l,
                          ),
                        }));
                        setFeedback(
                          t(
                            "Sample visit scheduled locally. No invitation was sent.",
                            "حُددت زيارة تجريبية محلياً. لم تُرسل دعوة.",
                          ),
                        );
                      }}
                      aria-label={
                        t("Schedule sample visit", "تحديد زيارة تجريبية") +
                        " " +
                        label(lead.name)
                      }
                    >
                      {t("Schedule sample visit", "تحديد زيارة تجريبية")}
                    </button>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
      </section>
      <footer>
        <strong>
          {t(
            "Fictional nursery. Real conversations about value.",
            "حضانة خيالية. حوار واقعي عن القيمة.",
          )}
        </strong>
        <p>
          {t(
            "Demo actions stay in this page and reset on reload. No live messages, payments, child records or access controls are connected. Branch selection is a presentation filter.",
            "تبقى الإجراءات في هذه الصفحة وتُعاد عند تحميلها. لا توجد رسائل أو مدفوعات أو سجلات حقيقية متصلة. اختيار الفرع مرشح للعرض.",
          )}
        </p>
      </footer>
    </main>
  );
}
