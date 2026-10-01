import type { Product } from "../../api/types.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { ProductCard } from "./ProductCard.tsx";

interface ProductGridProps {
    products: Product[];
    emptyMessage?: string;
}

export function ProductGrid({ products, emptyMessage }: ProductGridProps) {
    const { t } = useLanguage();

    if (products.length === 0) {
        return (
            <p className="text-gray-500">{emptyMessage ?? t.product.empty}</p>
        );
    }

    return (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {products.map((product) => (
                <ProductCard key={product.id} product={product} />
            ))}
        </div>
    );
}
