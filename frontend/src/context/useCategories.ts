import { use } from "react";

import { CategoriesContext } from "./CategoriesContext.ts";

export function useCategories() {
    return use(CategoriesContext);
}
