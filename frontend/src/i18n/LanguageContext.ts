import { createContext } from "react";

import { DEFAULT_LANGUAGE, LANGUAGES } from "./languages.ts";
import type { LanguageCode, LanguageInfo } from "./languages.ts";
import { translations } from "./locales/index.ts";

export interface LanguageState {
    language: LanguageCode;
    setLanguage: (language: LanguageCode) => void;
    languages: LanguageInfo[];
    t: (typeof translations)[LanguageCode];
}

export const LanguageContext = createContext<LanguageState>({
    language: DEFAULT_LANGUAGE,
    setLanguage: () => {},
    languages: LANGUAGES,
    t: translations[DEFAULT_LANGUAGE],
});
