import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { LanguageContext } from "./LanguageContext.ts";
import { DEFAULT_LANGUAGE, LANGUAGES, isLanguageCode } from "./languages.ts";
import type { LanguageCode } from "./languages.ts";
import { translations } from "./locales/index.ts";

const STORAGE_KEY = "language";

function detectInitialLanguage(): LanguageCode {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && isLanguageCode(stored)) {
            return stored;
        }
    } catch {
        // localStorage indisponível (modo privado, etc.) — segue com a detecção do navegador.
    }

    const browserLanguage = navigator.language.toLowerCase();
    const match = LANGUAGES.find(
        (language) =>
            browserLanguage === language.code ||
            browserLanguage.startsWith(`${language.code.split("-")[0]}-`) ||
            browserLanguage === language.code.split("-")[0],
    );

    return match?.code ?? DEFAULT_LANGUAGE;
}

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguageState] = useState<LanguageCode>(
        detectInitialLanguage,
    );

    useEffect(() => {
        document.documentElement.lang = language;

        try {
            localStorage.setItem(STORAGE_KEY, language);
        } catch {
            // Nada a fazer se o storage não estiver disponível.
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
