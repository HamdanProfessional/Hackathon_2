/**
 * Language Switcher Component
 * Supports English and Urdu with RTL support
 */

"use client";

import { useState, useEffect } from "react";
import { Globe, Check } from "lucide-react";
import { useRouter, usePathname } from "next/navigation";

// Types
type Locale = "en" | "ur";

interface LocaleOption {
  code: Locale;
  name: string;
  nativeName: string;
  direction: "ltr" | "rtl";
}

const locales: LocaleOption[] = [
  { code: "en", name: "English", nativeName: "English", direction: "ltr" },
  { code: "ur", name: "Urdu", nativeName: "اردو", direction: "rtl" },
];

// Translation messages
const messages: Record<Locale, Record<string, string>> = {
  en: {
    switchLanguage: "Switch Language",
    current: "Current",
  },
  ur: {
    switchLanguage: "زبان تبدیل کریں",
    current: "موجودہ",
  },
};

export default function LanguageSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [locale, setLocale] = useState<Locale>("en");
  const [direction, setDirection] = useState<"ltr" | "rtl">("ltr");

  // Detect and set locale on mount
  useEffect(() => {
    const stored = localStorage.getItem("todo-locale") as Locale | null;
    const browserLang = navigator.language.toLowerCase();

    let detected: Locale = "en";
    if (stored && ["en", "ur"].includes(stored)) {
      detected = stored;
    } else if (browserLang.startsWith("ur")) {
      detected = "ur";
    }

    setLocale(detected);
    setDirection(detected === "ur" ? "rtl" : "ltr");
    document.documentElement.dir = detected === "ur" ? "rtl" : "ltr";
    document.documentElement.lang = detected;
  }, []);

  const handleLocaleChange = (newLocale: Locale) => {
    setLocale(newLocale);
    setDirection(newLocale === "ur" ? "rtl" : "ltr");

    // Store preference
    localStorage.setItem("todo-locale", newLocale);

    // Update document direction
    document.documentElement.dir = newLocale === "ur" ? "rtl" : "ltr";
    document.documentElement.lang = newLocale;

    // Close dropdown
    setIsOpen(false);

    // Optional: Reload to apply translations
    // router.refresh();
  };

  const currentLocale = locales.find(l => l.code === locale);

  return (
    <div className="relative" dir={direction}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-zinc-800/50 transition-colors text-sm"
        aria-label={messages[locale].switchLanguage}
      >
        <Globe className="w-4 h-4 text-zinc-400" />
        <span className="text-zinc-300">{currentLocale?.nativeName}</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute top-full right-0 mt-2 z-20 w-48 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl overflow-hidden">
            {locales.map((loc) => (
              <button
                key={loc.code}
                onClick={() => handleLocaleChange(loc.code)}
                className={`w-full flex items-center justify-between px-4 py-3 text-sm transition-colors hover:bg-zinc-800/50 ${
                  loc.code === locale ? "bg-zinc-800/30" : ""
                }`}
                dir={loc.direction}
              >
                <div className="flex items-center gap-3">
                  <span className="font-medium text-zinc-200">{loc.nativeName}</span>
                  <span className="text-zinc-500 text-xs">{loc.name}</span>
                </div>
                {loc.code === locale && (
                  <Check className="w-4 h-4 text-violet-500" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
