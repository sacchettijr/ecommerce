import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useParams, useSearchParams } from "react-router";

import { ApiError } from "../api/client.ts";
import { fetchProduct } from "../api/products.ts";
import {
    addToWishlist,
    checkWishlistMembership,
    removeFromWishlistItem,
} from "../api/wishlist.ts";
import { withNext } from "../auth/authRoutes.ts";
import { ExpandableDescription } from "../components/product/ExpandableDescription.tsx";
import { ImageCarousel } from "../components/product/ImageCarousel.tsx";
import { ProductBreadcrumb } from "../components/product/ProductBreadcrumb.tsx";
import { ProductPrice } from "../components/product/ProductPrice.tsx";
import { useAddToCart } from "../components/product/useAddToCart.ts";
import { CartPlusIcon, HeartIcon } from "../components/ui/icons.tsx";
import { useAuth } from "../context/useAuth.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import { NotFoundPage } from "./NotFoundPage.tsx";

function WishlistToggleButton({ productId }: { productId: number }) {
    const { t } = useLanguage();
    const { user } = useAuth();
    const location = useLocation();
    // null = not checked yet (guest, or the initial check hasn't resolved).
    const [itemId, setItemId] = useState<number | null>(null);
    const [checked, setChecked] = useState(false);
    const [pending, setPending] = useState(false);
    const [errorText, setErrorText] = useState<string | null>(null);
    const requestTokenRef = useRef(0);
    const abortControllerRef = useRef<AbortController | null>(null);

    useEffect(() => {
        if (!user) {
            return;
        }

        const controller = new AbortController();
        abortControllerRef.current = controller;
        const token = (requestTokenRef.current += 1);

        checkWishlistMembership(productId, controller.signal)
            .then((result) => {
                if (token !== requestTokenRef.current) {
                    return;
                }
                setItemId(result.item_id);
                setChecked(true);
            })
            .catch(() => {
                // Leaves the button disabled-looking (checked stays false) rather than
                // guessing a state that might trigger the wrong action.
            });

        return () => controller.abort();
    }, [productId, user]);

    useEffect(() => {
        return () => abortControllerRef.current?.abort();
    }, []);

    if (!user) {
        const next = `${location.pathname}${location.search}`;
        return (
            <Link
                to={withNext("/login", next)}
                className="inline-flex items-center gap-2 rounded-lg border border-blue-600 px-6 py-3 text-lg font-medium text-blue-600 hover:bg-blue-50"
            >
                <HeartIcon className="size-5" />
                {t.product.addToWishlist}
            </Link>
        );
    }

    const inWishlist = itemId !== null;

    const onClick = async () => {
        if (pending || !checked) {
            return;
        }

        abortControllerRef.current?.abort();
        const controller = new AbortController();
        abortControllerRef.current = controller;
        const token = (requestTokenRef.current += 1);
        setPending(true);
        setErrorText(null);

        try {
            if (inWishlist) {
                await removeFromWishlistItem(itemId, controller.signal);
                if (token !== requestTokenRef.current) {
                    return;
                }
                setItemId(null);
            } else {
                const updated = await addToWishlist(productId, controller.signal);
                if (token !== requestTokenRef.current) {
                    return;
                }
                const created = updated.find(
                    (item) => item.product.id === productId,
                );
                setItemId(created?.id ?? null);
            }
            setPending(false);
        } catch (err) {
            if (token !== requestTokenRef.current) {
                return;
            }
            setPending(false);

            if (err instanceof DOMException && err.name === "AbortError") {
                return;
            }

            setErrorText(t.wishlist.updateError);
        }
    };

    return (
        <div>
            <button
                type="button"
                disabled={!checked || pending}
                onClick={() => void onClick()}
                className="inline-flex items-center gap-2 rounded-lg border border-blue-600 px-6 py-3 text-lg font-medium text-blue-600 hover:bg-blue-50 disabled:opacity-60"
            >
                <HeartIcon
                    className="size-5"
                    fill={inWishlist ? "currentColor" : "none"}
                />
                {inWishlist ? t.product.removeFromWishlist : t.product.addToWishlist}
            </button>
            {errorText && (
                <p role="alert" className="mt-1 text-sm text-red-600">
                    {errorText}
                </p>
            )}
        </div>
    );
}

function ProductDetail({ slug }: { slug: string }) {
    const { t } = useLanguage();
    const { user } = useAuth();
    const { data, error, loading } = useAsync(fetchProduct, slug);
    const [searchParams, setSearchParams] = useSearchParams();
    const addToCart = useAddToCart({ id: data?.id ?? 0, slug });
    const resumedRef = useRef(false);

    // Resumes an add-to-cart intent carried through the login redirect
    // (?addToCart=1, see useAddToCart.ts) — fires at most once, and strips the query
    // param immediately so refreshing this page afterward never re-adds the product.
    useEffect(() => {
        if (
            resumedRef.current ||
            data === undefined ||
            !user ||
            searchParams.get("addToCart") !== "1"
        ) {
            return;
        }

        resumedRef.current = true;
        setSearchParams(
            (params) => {
                params.delete("addToCart");
                return params;
            },
            { replace: true },
        );
        addToCart.add();
    }, [data, user, searchParams, setSearchParams, addToCart]);

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

                        <div className="mb-6 flex flex-wrap items-start gap-3">
                            <div>
                                <button
                                    type="button"
                                    disabled={addToCart.pending}
                                    onClick={addToCart.add}
                                    className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-lg font-medium text-white hover:bg-blue-700 disabled:opacity-60"
                                >
                                    <CartPlusIcon className="size-5" />
                                    {t.product.addToCartLabel}
                                </button>
                                {addToCart.error && (
                                    <p role="alert" className="mt-1 text-sm text-red-600">
                                        {t.product.addToCartError}
                                    </p>
                                )}
                            </div>
                            <WishlistToggleButton productId={data.id} />
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
