// Valores aceitos por `ordering` em /api/product/products/ (ver ProductSimpleListViewSet).
export const PRODUCT_SORT_OPTIONS = [
    "-created_at",
    "name",
    "-name",
    "price",
    "-price",
] as const;

export type ProductSort = (typeof PRODUCT_SORT_OPTIONS)[number];

export const DEFAULT_PRODUCT_SORT: ProductSort = "-created_at";

export function isProductSort(value: string): value is ProductSort {
    return PRODUCT_SORT_OPTIONS.some((option) => option === value);
}

export function getProductSort(searchParams: URLSearchParams): ProductSort {
    const value = searchParams.get("ordering");

    return value !== null && isProductSort(value)
        ? value
        : DEFAULT_PRODUCT_SORT;
}
