import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { detectInitialLanguage, LANGUAGE_STORAGE_KEY } from "./detectInitialLanguage.ts";
import { LanguageContext } from "./LanguageContext.ts";
import { LANGUAGES } from "./languages.ts";
import type { LanguageCode } from "./languages.ts";
import { translations } from "./locales/index.ts";

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguageState] = useState<LanguageCode>(
        detectInitialLanguage,
    );

    useEffect(() => {
        document.documentElement.lang = language;

        try {
            localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
        } catch {
            // Nothing to do if storage is unavailable.
        }
    }, [language]);

    return (
        <LanguageContext
            value={{
                language,
                setLanguage: setLanguageState,
                languages: LANGUAGES,
                t: translations[language],
            }}
        >
            {children}
        </LanguageContext>
    );
}
