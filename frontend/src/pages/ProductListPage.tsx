import { useEffect, useRef } from "react";
import { useParams, useSearchParams } from "react-router";

import { ApiError } from "../api/client.ts";
import { fetchProducts } from "../api/products.ts";
import { getProductSort } from "../components/product/productSort.ts";
import { ProductGrid } from "../components/product/ProductGrid.tsx";
import { ProductSortSelect } from "../components/product/ProductSortSelect.tsx";
import { Pagination } from "../components/ui/Pagination.tsx";
import { useCategories } from "../context/useCategories.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

function parsePage(value: string | null): number {
    const page = Number(value);
    return Number.isInteger(page) && page >= 1 ? page : 1;
}

export function ProductListPage() {
    const { slug } = useParams<{ slug?: string }>();
    const [searchParams] = useSearchParams();
    const page = parsePage(searchParams.get("page"));
    const search = searchParams.get("q") ?? "";

    const { t } = useLanguage();
    const { categories, loading: loadingCategories } = useCategories();
    const category = slug
        ? categories.find((item) => item.slug === slug)
        : undefined;

    const query = new URLSearchParams();
    if (slug) {
        query.set("category", slug);
    }
    if (search) {
        query.set("search", search);
    }
    query.set("ordering", getProductSort(searchParams));
    query.set("page", String(page));
    const queryKey = query.toString();

    const { data, error, loading } = useAsync(fetchProducts, queryKey);

    const listRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (page > 1 && data) {
            listRef.current?.scrollIntoView();
        }
    }, [page, data]);

    // Enquanto as categorias carregam, o título ainda não é conhecido: evita piscar "Produtos".
    const waitingForCategory =
        slug !== undefined && category === undefined && loadingCategories;
    const categoryName = category?.name;
    const searchLabel = search ? t.product.searchingFor(search) : undefined;
    const fallbackTitle =
        categoryName || searchLabel ? undefined : t.product.allProductsTitle;

    const titleText = waitingForCategory
        ? ""
        : [categoryName, searchLabel, fallbackTitle]
              .filter((part) => part !== undefined)
              .join(". ");

    const productsError =
        error instanceof ApiError && error.status === 404
            ? t.home.pageNotFound
            : t.home.loadProductsError;

    return (
        <>
            <title>
                {titleText ? `${titleText} | E-Commerce` : "E-Commerce"}
            </title>

            <div
                ref={listRef}
                className="mx-auto max-w-7xl scroll-mt-4 px-4 py-12"
            >
                <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
                    <h1 className="text-3xl font-bold wrap-break-words">
                        {waitingForCategory ? (
                            " "
                        ) : (
                            <>
                                {categoryName}
                                {categoryName && searchLabel && ". "}
                                {searchLabel && (
                                    <span
                                        className={
                                            categoryName
                                                ? "font-normal text-gray-600"
                                                : undefined
                                        }
                                    >
                                        {searchLabel}
                                    </span>
                                )}
                                {fallbackTitle}
                            </>
                        )}
                    </h1>
                    <ProductSortSelect />
                </div>

                {loading && (
                    <p className="text-gray-500">{t.home.loadingProducts}</p>
                )}
                {error !== undefined && (
                    <p role="alert" className="text-red-600">
                        {productsError}
                    </p>
                )}
                {data && (
                    <>
                        <ProductGrid
                            products={data.results}
                            emptyMessage={t.product.notFound}
                        />
                        <Pagination
                            page={data.current_page}
                            totalPages={data.total_pages}
                        />
                    </>
                )}
            </div>
        </>
    );
}
