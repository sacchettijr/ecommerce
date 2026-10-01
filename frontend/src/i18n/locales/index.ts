import type { LanguageCode } from "../languages.ts";
import type { Translations } from "../types.ts";
import en from "./en.ts";
import es from "./es.ts";
import fr from "./fr.ts";
import it from "./it.ts";
import ptBr from "./pt-br.ts";

export const translations: Record<LanguageCode, Translations> = {
    "pt-br": ptBr,
    en,
    es,
    fr,
    it,
};
