import { DEFAULT_LANGUAGE, LANGUAGES, isLanguageCode } from "./languages.ts";
import type { LanguageCode } from "./languages.ts";

export const LANGUAGE_STORAGE_KEY = "language";

export function detectInitialLanguage(): LanguageCode {
    try {
        const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
        if (stored && isLanguageCode(stored)) {
            return stored;
        }
    } catch {
        // localStorage unavailable (private mode, etc.) — fall back to browser detection.
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
