import { Link } from "react-router";

import { useLanguage } from "../../i18n/useLanguage.ts";

export function ProductBreadcrumb({
    categoryName,
    categorySlug,
    productName,
}: {
    categoryName: string;
    categorySlug: string;
    productName: string;
}) {
    const { t } = useLanguage();

    return (
        <nav aria-label={t.product.breadcrumbLabel} className="mb-6">
            <ol className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
                <li>
                    <Link to="/" className="hover:underline">
                        {t.nav.home}
                    </Link>
                </li>
                <li aria-hidden="true">/</li>
                <li>
                    <Link
                        to={`/category/${categorySlug}`}
                        className="hover:underline"
                    >
                        {categoryName}
                    </Link>
                </li>
                <li aria-hidden="true">/</li>
                <li
                    aria-current="page"
                    title={productName}
                    className="max-w-[10rem] truncate text-gray-900 sm:max-w-xs"
                >
                    {productName}
                </li>
            </ol>
        </nav>
    );
}
