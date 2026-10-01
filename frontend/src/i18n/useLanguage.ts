import { use } from "react";

import { LanguageContext } from "./LanguageContext.ts";

export function useLanguage() {
    return use(LanguageContext);
}
