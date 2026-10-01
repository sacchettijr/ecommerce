import { apiGet } from "./client.ts";
import type {
    Paginated,
    Product,
    ProductCategory,
    ProductDetail,
} from "./types.ts";

const MAX_CATEGORY_PAGES = 20;

export function fetchProducts(
    query: string,
    signal: AbortSignal,
): Promise<Paginated<Product>> {
    return apiGet<Paginated<Product>>(`/product/products/?${query}`, signal);
}

export function fetchProduct(
    slug: string,
    signal: AbortSignal,
): Promise<ProductDetail> {
    return apiGet<ProductDetail>(
        `/product/products/${encodeURIComponent(slug)}/`,
        signal,
    );
}

export async function fetchAllCategories(
    _arg: undefined,
    signal: AbortSignal,
): Promise<ProductCategory[]> {
    const categories: ProductCategory[] = [];

    for (let page = 1; page <= MAX_CATEGORY_PAGES; page++) {
        const data = await apiGet<Paginated<ProductCategory>>(
            `/product/categories/?page=${page}`,
            signal,
        );
        categories.push(...data.results);

        if (!data.next) {
            break;
        }
    }

    return categories;
}
