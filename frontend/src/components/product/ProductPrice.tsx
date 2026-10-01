import { formatPrice } from "./formatPrice.ts";

interface ProductPriceProps {
    price: string;
    promotionalPrice?: string | null;
}

export function ProductPrice({ price, promotionalPrice }: ProductPriceProps) {
    const original = Number(price);
    const promotional =
        promotionalPrice === undefined || promotionalPrice === null
            ? null
            : Number(promotionalPrice);
    const hasPromotion =
        promotional !== null && original > 0 && promotional < original;

    // min-h reserva o espaço da promoção: o layout não "pula" quando ela existir.
    return (
        <div className="mb-4 flex min-h-12 flex-wrap items-baseline gap-x-3 gap-y-1">
            {hasPromotion ? (
                <>
                    <span className="text-lg text-gray-500 line-through">
                        {formatPrice(original)}
                    </span>
                    <span className="rounded bg-red-600 px-2 py-0.5 text-sm font-semibold text-white">
                        -{Math.round((1 - promotional / original) * 100)}%
                    </span>
                    <span className="text-3xl font-bold">
                        {formatPrice(promotional)}
                    </span>
                </>
            ) : (
                <span className="text-3xl font-bold">
                    {formatPrice(original)}
                </span>
            )}
        </div>
    );
}
