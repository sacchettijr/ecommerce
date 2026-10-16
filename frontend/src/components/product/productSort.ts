// Values accepted by `ordering` in /api/product/products/ (see ProductSimpleListViewSet),
// plus "featured": a frontend-only sentinel meaning "send no ordering param at all", which
// lets the backend's randomized default (ProductSimpleListViewSet._shuffle) apply.
export const PRODUCT_SORT_OPTIONS = [
    "featured",
    "-created_at",
    "name",
    "-name",
    "price",
    "-price",
] as const;

export type ProductSort = (typeof PRODUCT_SORT_OPTIONS)[number];

export const DEFAULT_PRODUCT_SORT: ProductSort = "featured";

export function isProductSort(value: string): value is ProductSort {
    return PRODUCT_SORT_OPTIONS.some((option) => option === value);
}

export function getProductSort(searchParams: URLSearchParams): ProductSort {
    const value = searchParams.get("ordering");

    return value !== null && isProductSort(value)
        ? value
        : DEFAULT_PRODUCT_SORT;
}
