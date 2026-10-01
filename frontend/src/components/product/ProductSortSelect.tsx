import type { ChangeEvent } from "react";
import { useSearchParams } from "react-router";

import { useLanguage } from "../../i18n/useLanguage.ts";
import {
    PRODUCT_SORT_OPTIONS,
    getProductSort,
    isProductSort,
} from "./productSort.ts";
import type { ProductSort } from "./productSort.ts";

export function ProductSortSelect() {
    const [searchParams, setSearchParams] = useSearchParams();
    const { t } = useLanguage();

    const labels: Record<ProductSort, string> = {
        "-created_at": t.product.sortRecent,
        name: t.product.sortNameAsc,
        "-name": t.product.sortNameDesc,
        price: t.product.sortPriceAsc,
        "-price": t.product.sortPriceDesc,
    };

    const onChange = (event: ChangeEvent<HTMLSelectElement>) => {
        const value = event.target.value;

        if (!isProductSort(value)) {
            return;
        }

        const next = new URLSearchParams(searchParams);
        next.set("ordering", value);
        next.delete("page");
        setSearchParams(next);
    };

    return (
        <div className="flex items-center gap-2">
            <label htmlFor="product-sort" className="text-sm text-gray-600">
                {t.product.sortLabel}
            </label>
            <select
                id="product-sort"
                value={getProductSort(searchParams)}
                onChange={onChange}
                className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
                {PRODUCT_SORT_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                        {labels[option]}
                    </option>
                ))}
            </select>
        </div>
    );
}
