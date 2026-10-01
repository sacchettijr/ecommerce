import type { ReactNode } from "react";

import { fetchAllCategories } from "../api/products.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { CategoriesContext } from "./CategoriesContext.ts";

export function CategoriesProvider({ children }: { children: ReactNode }) {
    const { data, error, loading } = useAsync(fetchAllCategories, undefined);

    return (
        <CategoriesContext
            value={{
                categories: data ?? [],
                loading,
                error: error !== undefined,
            }}
        >
            {children}
        </CategoriesContext>
    );
}
