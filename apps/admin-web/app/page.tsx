"use client";

/** FEAT-036 shell experiment. Navigation never establishes authorization. */
import { useEffect, useState } from "react";
import { arabic, english } from "./messages";

export default function Page() {
  const [locale, setLocale] = useState<"en" | "ar">("en");
  const [tab, setTab] = useState<"overview" | "classrooms">("overview");
  const messages = locale === "ar" ? arabic : english;
  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
    document.title = messages.brand;
  }, [locale, messages.brand]);
  return (
    <main>
      <header>
        <strong>{messages.brand}</strong>
        <button onClick={() => setLocale(locale === "en" ? "ar" : "en")}>
          {messages.language}
        </button>
      </header>
      <p>{messages.preview}</p>
      <h1>{messages.heading}</h1>
      <p>{messages.description}</p>
      <nav aria-label={messages.navigation}>
        {(["overview", "classrooms"] as const).map((key) => (
          <button
            key={key}
            aria-current={tab === key ? "page" : undefined}
            onClick={() => setTab(key)}
          >
            {messages[key]}
          </button>
        ))}
      </nav>
      <section aria-label={messages[tab]}>
        <h2>{messages[tab]}</h2>
        <p>{messages.empty}</p>
      </section>
    </main>
  );
}
