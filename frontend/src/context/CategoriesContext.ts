import { createContext } from "react";

import type { ProductCategory } from "../api/types.ts";

export interface CategoriesState {
    categories: ProductCategory[];
    loading: boolean;
    error: boolean;
}

export const CategoriesContext = createContext<CategoriesState>({
    categories: [],
    loading: true,
    error: false,
});
