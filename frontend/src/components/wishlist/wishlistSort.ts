// "priority" means "no secondary sort — show items in the owner's own stored order"
// (the array already arrives in that order from the backend), mirroring how the product
// list's "featured" sentinel means "send no ordering param, let the default apply."
export const WISHLIST_SORT_OPTIONS = [
    "priority",
    "name",
    "-name",
    "price",
    "-price",
    "added_at",
    "-added_at",
] as const;

export type WishlistSort = (typeof WISHLIST_SORT_OPTIONS)[number];

export const DEFAULT_WISHLIST_SORT: WishlistSort = "priority";

export function isWishlistSort(value: string): value is WishlistSort {
    return WISHLIST_SORT_OPTIONS.some((option) => option === value);
}

interface SortableWishlistItem {
    added_at: string;
    product: {
        name: string;
        price: string;
    };
}

// The whole wishlist is always fetched in one request (it's never paginated), so — unlike
// the product list's server-side `ordering` — this sorts the already-fetched items
// entirely client-side. Generic over T so it works for both the owner's own WishlistItem
// and a third party's PublicWishlistItem, which share this same shape.
export function sortWishlistItems<T extends SortableWishlistItem>(
    items: T[],
    sort: WishlistSort,
): T[] {
    if (sort === DEFAULT_WISHLIST_SORT) {
        return items;
    }

    const direction = sort.startsWith("-") ? -1 : 1;
    const sorted = [...items];

    sorted.sort((a, b) => {
        if (sort === "name" || sort === "-name") {
            return direction * a.product.name.localeCompare(b.product.name);
        }
        if (sort === "price" || sort === "-price") {
            return direction * (Number(a.product.price) - Number(b.product.price));
        }
        return (
            direction *
            (new Date(a.added_at).getTime() - new Date(b.added_at).getTime())
        );
    });

    return sorted;
}
