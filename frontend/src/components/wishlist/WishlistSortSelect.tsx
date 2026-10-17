import type { ChangeEvent } from "react";

import { useLanguage } from "../../i18n/useLanguage.ts";
import { WISHLIST_SORT_OPTIONS, isWishlistSort } from "./wishlistSort.ts";
import type { WishlistSort } from "./wishlistSort.ts";

interface WishlistSortSelectProps {
    value: WishlistSort;
    onChange: (value: WishlistSort) => void;
}

// Same visual pattern as ProductSortSelect.tsx, but driven by local state (value/onChange)
// instead of the URL's search params — the whole wishlist is fetched in one request (no
// pagination), so sorting it is a pure client-side view concern, unlike the product list's
// server-side `ordering` query param.
export function WishlistSortSelect({ value, onChange }: WishlistSortSelectProps) {
    const { t } = useLanguage();

    const labels: Record<WishlistSort, string> = {
        priority: t.wishlist.sortPriority,
        name: t.wishlist.sortNameAsc,
        "-name": t.wishlist.sortNameDesc,
        price: t.wishlist.sortPriceAsc,
        "-price": t.wishlist.sortPriceDesc,
        added_at: t.wishlist.sortDateAddedAsc,
        "-added_at": t.wishlist.sortDateAddedDesc,
    };

    const onSelectChange = (event: ChangeEvent<HTMLSelectElement>) => {
        const next = event.target.value;

        if (isWishlistSort(next)) {
            onChange(next);
        }
    };

    return (
        <div className="flex items-center gap-2">
            <label htmlFor="wishlist-sort" className="text-sm text-gray-600">
                {t.wishlist.sortLabel}
            </label>
            <select
                id="wishlist-sort"
                value={value}
                onChange={onSelectChange}
                className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
                {WISHLIST_SORT_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                        {labels[option]}
                    </option>
                ))}
            </select>
        </div>
    );
}
