import { useEffect, useRef, useState } from "react";

import {
    fetchMyWishlist,
    fetchWishlistShareLink,
    moveWishlistItem,
    removeFromWishlistItem,
    toggleWishlistItemPrivacy,
} from "../api/wishlist.ts";
import type { WishlistItem } from "../api/types.ts";
import { AccountLayout } from "../components/account/AccountLayout.tsx";
import { Alert } from "../components/ui/Alert.tsx";
import { Tooltip } from "../components/ui/Tooltip.tsx";
import {
    ArrowDownIcon,
    ArrowUpIcon,
    CartPlusIcon,
    TrashIcon,
} from "../components/ui/icons.tsx";
import { formatPrice } from "../components/product/formatPrice.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import type { Translations } from "../i18n/types.ts";

const inertIconButtonClassName =
    "rounded p-1.5 text-gray-400 opacity-60 cursor-not-allowed";

interface WishlistItemRowProps {
    item: WishlistItem;
    isFirst: boolean;
    isLast: boolean;
    pending: boolean;
    language: string;
    t: Translations;
    onMoveUp: () => void;
    onMoveDown: () => void;
    onTogglePrivacy: () => void;
    onRemove: () => void;
}

function WishlistItemRow({
    item,
    isFirst,
    isLast,
    pending,
    language,
    t,
    onMoveUp,
    onMoveDown,
    onTogglePrivacy,
    onRemove,
}: WishlistItemRowProps) {
    const { product } = item;

    return (
        <div className="flex flex-col gap-4 rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-200 sm:flex-row sm:items-center">
            <div className="flex shrink-0 flex-col items-center gap-1">
                <button
                    type="button"
                    disabled={pending || isFirst}
                    aria-label={t.wishlist.moveUpLabel(product.name)}
                    onClick={onMoveUp}
                    className="rounded p-1 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                >
                    <ArrowUpIcon className="size-4" />
                </button>
                <span
                    className="text-sm font-semibold text-gray-700"
                    aria-label={t.wishlist.priorityLabel(item.position + 1)}
                >
                    {item.position + 1}
                </span>
                <button
                    type="button"
                    disabled={pending || isLast}
                    aria-label={t.wishlist.moveDownLabel(product.name)}
                    onClick={onMoveDown}
                    className="rounded p-1 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                >
                    <ArrowDownIcon className="size-4" />
                </button>
            </div>

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

            <div className="flex shrink-0 flex-wrap items-center gap-2">
                <button
                    type="button"
                    disabled={pending}
                    onClick={onTogglePrivacy}
                    className="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 ring-1 ring-gray-200 hover:bg-gray-50 disabled:opacity-50"
                >
                    {item.private ? t.wishlist.privateBadge : t.wishlist.publicBadge}
                </button>

                <Tooltip text={t.wishlist.deleteItemAccessibleLabel(product.name)}>
                    <button
                        type="button"
                        disabled={pending}
                        aria-label={t.wishlist.deleteItemAccessibleLabel(product.name)}
                        onClick={onRemove}
                        className="rounded p-1.5 text-red-600 hover:bg-red-50 disabled:opacity-50"
                    >
                        <TrashIcon className="size-5" />
                    </button>
                </Tooltip>

                <Tooltip text={t.product.addToCartLabel}>
                    <button
                        type="button"
                        aria-disabled="true"
                        aria-label={t.product.addToCartLabel}
                        className={inertIconButtonClassName}
                    >
                        <CartPlusIcon className="size-5" />
                    </button>
                </Tooltip>
            </div>
        </div>
    );
}

export function WishlistPage() {
    const { t, language } = useLanguage();
    const { data, error, loading } = useAsync(fetchMyWishlist, undefined);
    const [override, setOverride] = useState<WishlistItem[] | null>(null);
    const [pendingId, setPendingId] = useState<number | null>(null);
    const [copyingLink, setCopyingLink] = useState(false);
    const requestTokenRef = useRef(0);
    const abortControllerRef = useRef<AbortController | null>(null);
    const { messages, beginAction, replaceMessages, dismissMessage } =
        useMessages();
    const actionRef = useRef(0);

    useEffect(() => {
        return () => abortControllerRef.current?.abort();
    }, []);

    const items = override ?? data ?? null;
    const itemsLoading = loading && override === null;

    const runAction = async (
        itemId: number,
        call: (signal: AbortSignal) => Promise<WishlistItem[]>,
        successText?: string,
    ) => {
        abortControllerRef.current?.abort();
        const controller = new AbortController();
        abortControllerRef.current = controller;
        const token = (requestTokenRef.current += 1);
        actionRef.current = beginAction();
        setPendingId(itemId);

        try {
            const updated = await call(controller.signal);

            if (token !== requestTokenRef.current) {
                return;
            }
            setOverride(updated);
            setPendingId(null);

            if (successText) {
                replaceMessages(actionRef.current, [
                    { variant: "success", text: successText },
                ]);
            }
        } catch (err) {
            if (token !== requestTokenRef.current) {
                return;
            }
            setPendingId(null);

            if (err instanceof DOMException && err.name === "AbortError") {
                return;
            }

            try {
                const fresh = await fetchMyWishlist(undefined, controller.signal);
                if (token === requestTokenRef.current) {
                    setOverride(fresh);
                }
            } catch {
                // Keeps whatever was already displayed; the error message below still shows.
            }

            replaceMessages(actionRef.current, [
                { variant: "error", text: t.wishlist.updateError },
            ]);
        }
    };

    const onCopyLink = async () => {
        setCopyingLink(true);
        const token = (requestTokenRef.current += 1);
        actionRef.current = beginAction();

        try {
            const { public_id } = await fetchWishlistShareLink();
            const url = `${window.location.origin}/wishlist/${public_id}`;
            await navigator.clipboard.writeText(url);

            if (token !== requestTokenRef.current) {
                return;
            }
            replaceMessages(actionRef.current, [
                { variant: "success", text: t.wishlist.linkCopied },
            ]);
        } catch {
            if (token !== requestTokenRef.current) {
                return;
            }
            replaceMessages(actionRef.current, [
                { variant: "error", text: t.wishlist.copyLinkError },
            ]);
        } finally {
            if (token === requestTokenRef.current) {
                setCopyingLink(false);
            }
        }
    };

    return (
        <AccountLayout
            title={t.wishlist.title}
            messages={messages}
            onDismissMessage={dismissMessage}
        >
            <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-gray-900">
                    {t.wishlist.heading}
                </h1>
                <button
                    type="button"
                    disabled={copyingLink}
                    onClick={() => void onCopyLink()}
                    className="rounded-lg px-3 py-2 text-sm font-medium text-blue-600 ring-1 ring-blue-200 hover:bg-blue-50 disabled:opacity-50"
                >
                    {t.wishlist.shareLinkLabel}
                </button>
            </div>

            {itemsLoading && <p>{t.common.loading}</p>}

            {!itemsLoading && error !== undefined && (
                <Alert variant="error">{t.wishlist.loadError}</Alert>
            )}

            {!itemsLoading && error === undefined && items !== null && (
                <>
                    {items.length === 0 ? (
                        <p className="text-gray-600">{t.wishlist.emptyState}</p>
                    ) : (
                        <div className="space-y-4">
                            {items.map((item, index) => (
                                <WishlistItemRow
                                    key={item.id}
                                    item={item}
                                    isFirst={index === 0}
                                    isLast={index === items.length - 1}
                                    pending={pendingId === item.id}
                                    language={language}
                                    t={t}
                                    onMoveUp={() =>
                                        void runAction(item.id, (signal) =>
                                            moveWishlistItem(item.id, "up", signal),
                                        )
                                    }
                                    onMoveDown={() =>
                                        void runAction(item.id, (signal) =>
                                            moveWishlistItem(item.id, "down", signal),
                                        )
                                    }
                                    onTogglePrivacy={() =>
                                        void runAction(
                                            item.id,
                                            (signal) =>
                                                toggleWishlistItemPrivacy(
                                                    item.id,
                                                    signal,
                                                ),
                                            t.wishlist.privacyUpdated,
                                        )
                                    }
                                    onRemove={() =>
                                        void runAction(
                                            item.id,
                                            (signal) =>
                                                removeFromWishlistItem(
                                                    item.id,
                                                    signal,
                                                ),
                                            t.wishlist.itemRemoved,
                                        )
                                    }
                                />
                            ))}
                        </div>
                    )}
                </>
            )}
        </AccountLayout>
    );
}
