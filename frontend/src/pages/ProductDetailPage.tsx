import { useParams } from "react-router";

import { ApiError } from "../api/client.ts";
import { fetchProduct } from "../api/products.ts";
import { ExpandableDescription } from "../components/product/ExpandableDescription.tsx";
import { ImageCarousel } from "../components/product/ImageCarousel.tsx";
import { ProductBreadcrumb } from "../components/product/ProductBreadcrumb.tsx";
import { ProductPrice } from "../components/product/ProductPrice.tsx";
import { CartPlusIcon, HeartIcon } from "../components/ui/icons.tsx";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import { NotFoundPage } from "./NotFoundPage.tsx";

function ProductDetail({ slug }: { slug: string }) {
    const { t } = useLanguage();
    const { data, error, loading } = useAsync(fetchProduct, slug);

    // Produto inexistente ou inativo: a API responde 404 e a página cai no 404 padrão.
    if (error instanceof ApiError && error.status === 404) {
        return <NotFoundPage />;
    }

    if (data === undefined) {
        return (
            <>
                <title>E-Commerce</title>

                <div className="mx-auto max-w-7xl px-4 py-12">
                    {loading && (
                        <p className="text-gray-500">{t.common.loading}</p>
                    )}
                    {error !== undefined && (
                        <p role="alert" className="text-red-600">
                            {t.product.loadError}
                        </p>
                    )}
                </div>
            </>
        );
    }

    return (
        <>
            <title>{`${data.name} | E-Commerce`}</title>

            <div className="mx-auto max-w-7xl px-4 py-12">
                <ProductBreadcrumb
                    categoryName={data.category.name}
                    categorySlug={data.category.slug}
                    productName={data.name}
                />

                <div className="grid items-start gap-8 md:grid-cols-2">
                    <ImageCarousel
                        key={data.id}
                        images={data.images}
                        name={data.name}
                    />

                    <div>
                        <h1 className="mb-2 text-3xl font-bold wrap-break-words">
                            {data.name}
                        </h1>
                        <p className="mb-3 text-gray-500">
                            {data.category.name}
                        </p>

                        <ProductPrice price={data.price} />

                        <div className="mb-6 flex flex-wrap gap-3">
                            <button
                                type="button"
                                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-lg font-medium text-white hover:bg-blue-700"
                            >
                                <CartPlusIcon className="size-5" />
                                {t.product.addToCartLabel}
                            </button>
                            <button
                                type="button"
                                className="inline-flex items-center gap-2 rounded-lg border border-blue-600 px-6 py-3 text-lg font-medium text-blue-600 hover:bg-blue-50"
                            >
                                <HeartIcon className="size-5" />
                                {t.product.addToWishlist}
                            </button>
                        </div>

                        {data.description && (
                            <section className="border-t border-gray-200 pt-4">
                                <h2 className="mb-2 text-xl font-semibold">
                                    {t.product.descriptionTitle}
                                </h2>
                                <ExpandableDescription
                                    description={data.description}
                                />
                            </section>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export function ProductDetailPage() {
    const { slug } = useParams<{ slug: string }>();

    if (slug === undefined) {
        return <NotFoundPage />;
    }

    return <ProductDetail key={slug} slug={slug} />;
}
