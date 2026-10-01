import { Link } from "react-router";

import type { Product } from "../../api/types.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { CartPlusIcon } from "../ui/icons.tsx";
import { formatPrice } from "./formatPrice.ts";

export function ProductCard({ product }: { product: Product }) {
    const { t } = useLanguage();

    return (
        <div className="flex h-full flex-col overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200">
            {product.thumbnail ? (
                <div className="flex aspect-square w-full items-center justify-center overflow-hidden border-b border-gray-100 bg-white p-4">
                    <img
                        src={product.thumbnail}
                        alt={product.name}
                        loading="lazy"
                        className="max-h-full max-w-full object-contain"
                    />
                </div>
            ) : (
                <div className="flex aspect-square w-full items-center justify-center bg-gray-100 text-sm text-gray-500">
                    {t.product.noImage}
                </div>
            )}

            <div className="flex flex-1 flex-col p-4">
                <h3 className="text-lg font-semibold">{product.name}</h3>
                <p className="mt-auto pt-3 font-bold">
                    {formatPrice(Number(product.price))}
                </p>
                <div className="mt-3 flex gap-2">
                    <Link
                        to={`/product/${product.slug}`}
                        className="flex-1 rounded-lg bg-blue-600 px-3 py-2 text-center font-medium text-white hover:bg-blue-700"
                    >
                        {t.product.viewDetails}
                    </Link>
                    <button
                        type="button"
                        title={t.product.addToCart(product.name)}
                        aria-label={t.product.addToCart(product.name)}
                        className="rounded-lg border border-blue-600 px-3 py-2 text-blue-600 hover:bg-blue-50"
                    >
                        <CartPlusIcon className="size-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
