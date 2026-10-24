"use client";
import { FormEvent, useState } from "react";

type SecurityProfile = { mfa_required?: boolean; mfa_enrolled?: boolean };
type Api = <T>(path: string, body?: object) => Promise<T>;

export default function MfaPanel<T extends SecurityProfile>({
  api,
  ar,
  profile,
  onReady,
  onClose,
}: {
  api: Api;
  ar: boolean;
  profile: T;
  onReady: (profile: T) => void;
  onClose: () => void;
}) {
  const t = (en: string, arabic: string) => (ar ? arabic : en);
  const [secret, setSecret] = useState("");
  const [code, setCode] = useState("");
  const [kind, setKind] = useState("totp");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [complete, setComplete] = useState<{
    profile: T;
    recovery_codes: string[];
  } | null>(null);
  const [saved, setSaved] = useState(false);
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setMessage("");
    try {
      await action();
    } catch (error) {
      const value = error instanceof Error ? error.message : "";
      setMessage(
        value === "verification_rate_limited"
          ? t(
              "Too many attempts. Wait five minutes before trying again.",
              "محاولات كثيرة. انتظر خمس دقائق قبل المحاولة مجدداً.",
            )
          : value === "invalid_mfa_verification"
            ? t(
                "Check the code. Each authenticator code can be used once; wait for the next code if needed.",
                "تحقق من الرمز. يُستخدم كل رمز مرة واحدة؛ انتظر الرمز التالي عند الحاجة.",
              )
            : value === "reauthentication_required"
              ? t(
                  "Verify a fresh authenticator or recovery code before changing your setup.",
                  "تحقق برمز حديث من التطبيق أو رمز استرداد قبل تغيير الإعداد.",
                )
              : t(
                  "Unable to complete verification. Sign in again if your session expired.",
                  "تعذر إكمال التحقق. سجّل الدخول مجدداً إذا انتهت الجلسة.",
                ),
      );
    } finally {
      setBusy(false);
    }
  }
  function begin() {
    void run(async () => {
      const data = await api<{ secret: string }>("auth/mfa/begin", {});
      setSecret(data.secret);
      setCode("");
      setKind("totp");
    });
  }
  function verify(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      const data = await api<{ profile: T; recovery_codes?: string[] }>(
        secret ? "auth/mfa/confirm" : "auth/mfa/verify",
        { code: code.trim(), kind: secret ? "totp" : kind },
      );
      setCode("");
      setSecret("");
      if (data.recovery_codes) {
        setComplete({
          profile: data.profile,
          recovery_codes: data.recovery_codes,
        });
      } else {
        onReady(data.profile);
      }
    });
  }
  return (
    <section className="panel">
      <h2>{t("Protect your account", "حماية حسابك")}</h2>
      <p>
        {t(
          "Privileged access requires a second factor. Keep recovery codes somewhere only you can access.",
          "تتطلب الصلاحيات الحساسة عاملاً ثانياً. احتفظ برموز الاسترداد في مكان آمن خاص بك.",
        )}
      </p>
      {message && <p role="alert">{message}</p>}
      {complete ? (
        <>
          <h3>{t("Save your recovery codes", "احفظ رموز الاسترداد")}</h3>
          <p>
            {t(
              "Each code works once. These codes remain on this screen until you continue.",
              "يعمل كل رمز مرة واحدة. تبقى الرموز على هذه الشاشة حتى تختار المتابعة.",
            )}
          </p>
          <ul dir="ltr">
            {complete.recovery_codes.map((value) => (
              <li key={value}>
                <code>{value}</code>
              </li>
            ))}
          </ul>
          <label>
            <input
              type="checkbox"
              checked={saved}
              onChange={(event) => setSaved(event.target.checked)}
            />
            {t("I saved these codes securely", "حفظت هذه الرموز بأمان")}
          </label>
          <button
            className="primary"
            disabled={!saved}
            onClick={() => onReady(complete.profile)}
          >
            {t("Continue to workspace", "متابعة إلى مساحة العمل")}
          </button>
        </>
      ) : (
        <>
          {secret && (
            <>
              <h3>
                {t(
                  "Add Nursery to your authenticator",
                  "أضف الحضانة إلى تطبيق المصادقة",
                )}
              </h3>
              <p>
                {t(
                  "Choose a time-based account in your authenticator and enter this setup key. Then enter its six-digit code.",
                  "اختر حساباً يعتمد على الوقت في تطبيق المصادقة وأدخل مفتاح الإعداد هذا، ثم أدخل الرمز المكون من ستة أرقام.",
                )}
              </p>
              <label>
                {t("Setup key", "مفتاح الإعداد")}
                <input readOnly dir="ltr" value={secret} autoComplete="off" />
              </label>
            </>
          )}
          {(profile.mfa_enrolled || secret) && (
            <form onSubmit={verify} className="workspace-correction">
              {!secret && (
                <label>
                  {t("Verification method", "طريقة التحقق")}
                  <select
                    aria-label={t("Verification method", "طريقة التحقق")}
                    value={kind}
                    onChange={(event) => setKind(event.target.value)}
                  >
                    <option value="totp">
                      {t("Authenticator code", "رمز تطبيق المصادقة")}
                    </option>
                    <option value="recovery">
                      {t("Recovery code", "رمز استرداد")}
                    </option>
                  </select>
                </label>
              )}
              <label>
                {t("Verification code", "رمز التحقق")}
                <input
                  required
                  value={code}
                  maxLength={80}
                  autoComplete="one-time-code"
                  inputMode={kind === "totp" ? "numeric" : "text"}
                  dir="ltr"
                  onChange={(event) => setCode(event.target.value)}
                />
              </label>
              <button className="primary" disabled={busy}>
                {t("Verify code", "تحقق من الرمز")}
              </button>
            </form>
          )}
          {!secret && (!profile.mfa_enrolled || !profile.mfa_required) && (
            <button disabled={busy} onClick={begin}>
              {profile.mfa_enrolled
                ? t("Replace authenticator", "استبدال تطبيق المصادقة")
                : t("Set up authenticator", "إعداد تطبيق المصادقة")}
            </button>
          )}
        </>
      )}
      {!profile.mfa_required && !complete && (
        <button disabled={busy} onClick={onClose}>
          {t("Back to workspace", "العودة إلى مساحة العمل")}
        </button>
      )}
    </section>
  );
}
