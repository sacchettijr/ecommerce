import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";

import { fetchCart, removeCartItem, updateCartItemQuantity } from "../api/cart.ts";
import type { CartItem, CartSummary } from "../api/types.ts";
import { formatPrice } from "../components/product/formatPrice.ts";
import { Alert } from "../components/ui/Alert.tsx";
import { Tooltip } from "../components/ui/Tooltip.tsx";
import { MinusIcon, PlusIcon, TrashIcon } from "../components/ui/icons.tsx";
import { useCart } from "../context/useCart.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import type { Translations } from "../i18n/types.ts";

interface CartItemRowProps {
    item: CartItem;
    pending: boolean;
    t: Translations;
    onDecrease: () => void;
    onIncrease: () => void;
    onRemove: () => void;
}

function CartItemRow({
    item,
    pending,
    t,
    onDecrease,
    onIncrease,
    onRemove,
}: CartItemRowProps) {
    const { product } = item;

    return (
        <div className="flex flex-col gap-4 rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-200 sm:flex-row sm:items-center">
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
                <h3 className="font-semibold wrap-break-words">{product.name}</h3>
                <p className="text-sm text-gray-500">{product.slug}</p>
                <p className="text-sm text-gray-600">
                    {t.cart.unitPriceLabel}: {formatPrice(Number(item.unit_price))}
                </p>
            </div>

            <div className="flex shrink-0 items-center gap-2">
                <button
                    type="button"
                    disabled={pending || item.quantity <= 1}
                    aria-label={t.cart.decreaseQuantityLabel(product.name)}
                    onClick={onDecrease}
                    className="rounded p-1.5 text-gray-600 ring-1 ring-gray-200 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                >
                    <MinusIcon className="size-4" />
                </button>
                <span
                    className="w-8 text-center font-semibold text-gray-700"
                    aria-label={t.cart.quantityLabel(item.quantity)}
                >
                    {item.quantity}
                </span>
                <button
                    type="button"
                    disabled={pending}
                    aria-label={t.cart.increaseQuantityLabel(product.name)}
                    onClick={onIncrease}
                    className="rounded p-1.5 text-gray-600 ring-1 ring-gray-200 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent"
                >
                    <PlusIcon className="size-4" />
                </button>
            </div>

            <div className="shrink-0 text-right">
                <p className="text-sm text-gray-500">{t.cart.lineTotalLabel}</p>
                <p className="font-bold">{formatPrice(Number(item.line_total))}</p>
            </div>

            <Tooltip text={t.cart.removeItemAccessibleLabel(product.name)}>
                <button
                    type="button"
                    disabled={pending}
                    aria-label={t.cart.removeItemAccessibleLabel(product.name)}
                    onClick={onRemove}
                    className="shrink-0 rounded p-1.5 text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                    <TrashIcon className="size-5" />
                </button>
            </Tooltip>
        </div>
    );
}

export function CartPage() {
    const { t } = useLanguage();
    const { cart, loading, error: loadError, setCart } = useCart();
    const [pendingId, setPendingId] = useState<number | null>(null);
    const [coupon, setCoupon] = useState("");
    const requestTokenRef = useRef(0);
    const abortControllerRef = useRef<AbortController | null>(null);
    const { messages, beginAction, replaceMessages, dismissMessage } = useMessages();
    const actionRef = useRef(0);

    useEffect(() => {
        return () => abortControllerRef.current?.abort();
    }, []);

    const runAction = async (
        itemId: number,
        call: (signal: AbortSignal) => Promise<CartSummary>,
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
            setCart(updated);
            setPendingId(null);

            if (successText) {
                replaceMessages(actionRef.current, [{ variant: "success", text: successText }]);
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
                const fresh = await fetchCart(undefined, controller.signal);
                if (token === requestTokenRef.current) {
                    setCart(fresh);
                }
            } catch {
                // Keeps whatever was already displayed; the error message below still shows.
            }

            replaceMessages(actionRef.current, [{ variant: "error", text: t.cart.updateError }]);
        }
    };

    const onDecrease = (item: CartItem) => {
        if (item.quantity <= 1) {
            return;
        }
        void runAction(item.id, (signal) =>
            updateCartItemQuantity(item.id, item.quantity - 1, signal),
        );
    };

    const onIncrease = (item: CartItem) => {
        void runAction(item.id, (signal) =>
            updateCartItemQuantity(item.id, item.quantity + 1, signal),
        );
    };

    const onRemove = (item: CartItem) => {
        void runAction(
            item.id,
            (signal) => removeCartItem(item.id, signal),
            t.cart.itemRemoved,
        );
    };

    return (
        <>
            <title>{t.cart.title}</title>

            <div className="mx-auto max-w-5xl px-4 py-12">
                <h1 className="mb-6 text-2xl font-bold text-gray-900">{t.cart.heading}</h1>

                {messages.map((message) => (
                    <Alert
                        key={message.id}
                        variant={message.variant}
                        onDismiss={() => dismissMessage(message.id)}
                        dismissLabel={t.common.dismiss}
                    >
                        {message.text}
                    </Alert>
                ))}

                {loading && <p>{t.common.loading}</p>}

                {!loading && loadError && <Alert variant="error">{t.cart.loadError}</Alert>}

                {!loading && !loadError && cart !== null && (
                    <>
                        {cart.items.length === 0 ? (
                            <p className="text-gray-600">
                                {t.cart.emptyState}{" "}
                                <Link to="/products" className="text-blue-600 hover:underline">
                                    {t.cart.browseProducts}
                                </Link>
                            </p>
                        ) : (
                            <>
                                <div className="space-y-4">
                                    {cart.items.map((item) => (
                                        <CartItemRow
                                            key={item.id}
                                            item={item}
                                            pending={pendingId === item.id}
                                            t={t}
                                            onDecrease={() => onDecrease(item)}
                                            onIncrease={() => onIncrease(item)}
                                            onRemove={() => onRemove(item)}
                                        />
                                    ))}
                                </div>

                                <div className="mt-6 flex flex-col gap-4 rounded-lg bg-white p-4 shadow-sm ring-1 ring-gray-200 sm:flex-row sm:items-end sm:justify-between">
                                    <div className="flex items-end gap-2">
                                        <label className="flex flex-col text-sm">
                                            {t.cart.couponLabel}
                                            <input
                                                type="text"
                                                value={coupon}
                                                onChange={(event) =>
                                                    setCoupon(event.target.value)
                                                }
                                                className="mt-1 rounded-lg border border-gray-300 px-3 py-2"
                                            />
                                        </label>
                                        <button
                                            type="button"
                                            className="rounded-lg bg-gray-100 px-4 py-2 font-medium text-gray-700 hover:bg-gray-200"
                                        >
                                            {t.cart.couponButton}
                                        </button>
                                    </div>

                                    <dl className="text-right">
                                        <div className="flex justify-between gap-6 text-sm text-gray-600">
                                            <dt>{t.cart.discountLabel}</dt>
                                            <dd>{formatPrice(Number(cart.discount_total))}</dd>
                                        </div>
                                        <div className="flex justify-between gap-6 text-lg font-bold">
                                            <dt>{t.cart.totalLabel}</dt>
                                            <dd>{formatPrice(Number(cart.total))}</dd>
                                        </div>
                                    </dl>
                                </div>
                            </>
                        )}
                    </>
                )}
            </div>
        </>
    );
}
