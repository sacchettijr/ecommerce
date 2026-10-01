export type LanguageCode = "pt-br" | "en" | "es" | "fr" | "it";

export interface LanguageInfo {
    code: LanguageCode;
    nativeName: string;
    flag: string;
}

// PROJECT/settings/internationalization.py (LANGUAGES) só declara pt-br/en/es hoje —
// fr/it existem só na interface React por enquanto (ver decisão em i18n/types.ts).
export const LANGUAGES: LanguageInfo[] = [
    { code: "pt-br", nativeName: "Português", flag: "/img/locale/pt-br.png" },
    { code: "en", nativeName: "English", flag: "/img/locale/en.png" },
    { code: "es", nativeName: "Español", flag: "/img/locale/es.png" },
    { code: "fr", nativeName: "Français", flag: "/img/locale/fr.png" },
    { code: "it", nativeName: "Italiano", flag: "/img/locale/it.png" },
];

export const DEFAULT_LANGUAGE: LanguageCode = "pt-br";

export function isLanguageCode(value: string): value is LanguageCode {
    return LANGUAGES.some((language) => language.code === value);
}
