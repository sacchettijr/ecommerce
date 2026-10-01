import { useEffect, useRef } from "react";
import { Link, useSearchParams } from "react-router";

import { ApiError } from "../api/client.ts";
import { fetchProducts } from "../api/products.ts";
import { Pagination } from "../components/ui/Pagination.tsx";
import { ProductGrid } from "../components/product/ProductGrid.tsx";
import { useCategories } from "../context/useCategories.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

function parsePage(value: string | null): number {
    const page = Number(value);
    return Number.isInteger(page) && page >= 1 ? page : 1;
}

export function HomePage() {
    const [searchParams] = useSearchParams();
    const page = parsePage(searchParams.get("page"));

    const { t } = useLanguage();
    const { categories, loading: loadingCategories } = useCategories();
    const { data, error, loading } = useAsync(fetchProducts, `page=${page}`);

    const productsSectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        if (page > 1 && data) {
            productsSectionRef.current?.scrollIntoView();
        }
    }, [page, data]);

    const productsError =
        error instanceof ApiError && error.status === 404
            ? t.home.pageNotFound
            : t.home.loadProductsError;

    const features = [
        {
            title: t.home.featureFastDeliveryTitle,
            description: t.home.featureFastDeliveryText,
        },
        {
            title: t.home.featureSecurePurchaseTitle,
            description: t.home.featureSecurePurchaseText,
        },
        {
            title: t.home.featureSupportTitle,
            description: t.home.featureSupportText,
        },
    ];

    return (
        <>
            <title>{t.home.title}</title>

            <section className="mb-12 bg-gray-900 py-16 text-gray-100">
                <div className="mx-auto max-w-7xl px-4 text-center">
                    <h1 className="mb-3 text-4xl font-bold md:text-5xl">
                        {t.home.heroTitle}
                    </h1>
                    <p className="mb-6 text-lg text-gray-300">
                        {t.home.heroSubtitle}
                    </p>
                    <Link
                        to="/products"
                        className="inline-block rounded-lg bg-blue-600 px-6 py-3 text-lg font-medium text-white hover:bg-blue-700"
                    >
                        {t.home.heroCta}
                    </Link>
                </div>
            </section>

            <section className="mx-auto mb-12 max-w-7xl px-4">
                <h2 className="mb-4 text-2xl font-semibold">
                    {t.home.categoriesTitle}
                </h2>
                {categories.length > 0 ? (
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                        {categories.map((category) => (
                            <Link
                                key={category.id}
                                to={`/category/${category.slug}`}
                                className="rounded-lg bg-white p-6 text-center shadow-sm ring-1 ring-gray-200 transition hover:-translate-y-0.5 hover:shadow-md"
                            >
                                <h3 className="text-lg font-semibold">
                                    {category.name}
                                </h3>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-500">
                        {loadingCategories
                            ? t.home.loadingCategories
                            : t.home.noCategories}
                    </p>
                )}
            </section>

            <section
                id="novidades"
                ref={productsSectionRef}
                className="mx-auto mb-12 max-w-7xl scroll-mt-4 px-4"
            >
                <h2 className="mb-4 text-2xl font-semibold">
                    {t.home.newProductsTitle}
                </h2>

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
                        <ProductGrid products={data.results} />
                        <Pagination
                            page={data.current_page}
                            totalPages={data.total_pages}
                        />
                    </>
                )}
            </section>

            <section className="mx-auto max-w-7xl px-4">
                <div className="grid gap-6 text-center md:grid-cols-3">
                    {features.map((feature) => (
                        <div key={feature.title}>
                            <h5 className="text-lg font-semibold">
                                {feature.title}
                            </h5>
                            <p className="text-sm text-gray-500">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </section>
        </>
    );
}
