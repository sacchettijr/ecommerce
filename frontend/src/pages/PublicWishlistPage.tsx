import { useEffect, useState } from "react";
import { useParams } from "react-router";

import { ApiError } from "../api/client.ts";
import { fetchPublicWishlist, fetchWishlistShareLink } from "../api/wishlist.ts";
import type { PublicWishlistItem } from "../api/types.ts";
import { formatPrice } from "../components/product/formatPrice.ts";
import { Tooltip } from "../components/ui/Tooltip.tsx";
import { GiftIcon } from "../components/ui/icons.tsx";
import { useAuth } from "../context/useAuth.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import type { Translations } from "../i18n/types.ts";
import { NotFoundPage } from "./NotFoundPage.tsx";
import { WishlistPage } from "./WishlistPage.tsx";

const inertIconButtonClassName =
    "rounded-lg px-3 py-2 text-sm font-medium text-gray-400 opacity-60 cursor-not-allowed ring-1 ring-gray-200";

function PublicWishlistItemRow({
    item,
    language,
    t,
}: {
    item: PublicWishlistItem;
    language: string;
    t: Translations;
}) {
    const { product } = item;

    return (
        <div className="flex flex-col gap-4 rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-200 sm:flex-row sm:items-center">
            <span
                className="shrink-0 text-center text-sm font-semibold text-gray-700 sm:w-16"
                aria-label={t.wishlist.priorityLabel(item.position + 1)}
            >
                {item.position + 1}
            </span>

            <div className="flex aspect-square w-20 shrink-0 items-center justify-center overflow-hidden rounded border border-gray-100 bg-white">
                {product.thumbnail ? (
                    <img
                        src={product.thumbnail}
                        alt={product.name}
                        loading="lazy"
                        className="max-h-full max-w-full object-contain"
                    />
                ) : (
                    <div className="flex h-full w-full items-center justify-center bg-gray-100 text-xs text-gray-500">
                        {t.product.noImage}
                    </div>
                )}
            </div>

            <div className="min-w-0 flex-1">
                <h3 className="font-semibold wrap-break-words">
                    {product.name}
                </h3>
                <p className="font-bold">{formatPrice(Number(product.price))}</p>
                <p className="text-sm text-gray-500">
                    {t.wishlist.addedOnLabel(
                        new Date(item.added_at).toLocaleDateString(language),
                    )}
                </p>
            </div>

            <Tooltip text={t.wishlist.giveAsGiftLabel}>
                <button
                    type="button"
                    aria-disabled="true"
                    aria-label={t.wishlist.giveAsGiftLabel}
                    className={`shrink-0 inline-flex items-center gap-2 ${inertIconButtonClassName}`}
                >
                    <GiftIcon className="size-5" />
                    {t.wishlist.giveAsGiftLabel}
                </button>
            </Tooltip>
        </div>
    );
}

function PublicWishlist({ publicId }: { publicId: string }) {
    const { t, language } = useLanguage();
    const { data, error, loading } = useAsync(fetchPublicWishlist, publicId);

    if (error instanceof ApiError && error.status === 404) {
        return <NotFoundPage />;
    }

    return (
        <>
            <title>{t.wishlist.publicViewTitle}</title>

            <div className="mx-auto max-w-4xl px-4 py-12">
                <h1 className="mb-6 text-2xl font-bold text-gray-900">
                    {t.wishlist.heading}
                </h1>

                {loading && <p>{t.common.loading}</p>}

                {!loading && error !== undefined && (
                    <p role="alert" className="text-red-600">
                        {t.wishlist.loadError}
                    </p>
                )}

                {!loading && error === undefined && data !== undefined && (
                    <>
                        {data.items.length === 0 ? (
                            <p className="text-gray-600">
                                {t.wishlist.publicEmptyState}
                            </p>
                        ) : (
                            <div className="space-y-4">
                                {data.items.map((item) => (
                                    <PublicWishlistItemRow
                                        key={item.id}
                                        item={item}
                                        language={language}
                                        t={t}
                                    />
                                ))}
                            </div>
                        )}
                    </>
                )}
            </div>
        </>
    );
}

export function PublicWishlistPage() {
    const { publicId } = useParams<{ publicId: string }>();
    const { user } = useAuth();
    // Starts false so an anonymous or different-user visitor sees the public view
    // immediately, with no extra request and no behavior change from before. Only flips to
    // true in the background, for the one specific case where the signed-in visitor turns
    // out to own this exact wishlist — this is a presentation choice, not a security
    // boundary: the public endpoint itself never returns private items to anyone regardless
    // of what this check concludes.
    const [isOwner, setIsOwner] = useState(false);

    useEffect(() => {
        if (!user || publicId === undefined) {
            return;
        }

        let active = true;

        fetchWishlistShareLink()
            .then(({ public_id }) => {
                if (active && public_id === publicId) {
                    setIsOwner(true);
                }
            })
            .catch(() => {
                // Keeps the public-only view, which is always the safe default.
            });

        return () => {
            active = false;
        };
    }, [user, publicId]);

    if (publicId === undefined) {
        return <NotFoundPage />;
    }

    if (isOwner) {
        return <WishlistPage />;
    }

    return <PublicWishlist key={publicId} publicId={publicId} />;
}
