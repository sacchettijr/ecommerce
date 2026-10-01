import { Link, useSearchParams } from "react-router";

import { useLanguage } from "../../i18n/useLanguage.ts";

interface PaginationProps {
    page: number;
    totalPages: number;
}

const WINDOW = 2;

const baseItem =
    "inline-flex min-w-10 items-center justify-center border border-gray-300 px-3 py-2 text-sm";

export function Pagination({ page, totalPages }: PaginationProps) {
    const [searchParams] = useSearchParams();
    const { t } = useLanguage();

    if (totalPages <= 1) {
        return null;
    }

    const hrefFor = (target: number): string => {
        const params = new URLSearchParams(searchParams);
        params.set("page", String(target));
        return `?${params.toString()}`;
    };

    const first = Math.max(1, page - WINDOW);
    const last = Math.min(totalPages, page + WINDOW);
    const numbers = Array.from(
        { length: last - first + 1 },
        (_, index) => first + index,
    );

    const step = (label: string, target: number, disabled: boolean) =>
        disabled ? (
            <span
                aria-disabled="true"
                className={`${baseItem} cursor-not-allowed bg-gray-100 text-gray-400`}
            >
                {label}
            </span>
        ) : (
            <Link
                to={hrefFor(target)}
                className={`${baseItem} bg-white text-blue-600 hover:bg-gray-50`}
            >
                {label}
            </Link>
        );

    return (
        <nav aria-label={t.pagination.navigation} className="mt-10">
            <ul className="flex flex-wrap items-center justify-center gap-1">
                <li>{step(t.pagination.first, 1, page <= 1)}</li>
                <li>{step(t.pagination.previous, page - 1, page <= 1)}</li>
                {first > 1 && (
                    <li aria-hidden="true" className="px-1 text-gray-400">
                        …
                    </li>
                )}
                {numbers.map((number) => (
                    <li key={number}>
                        {number === page ? (
                            <span
                                aria-current="page"
                                className={`${baseItem} border-blue-600 bg-blue-600 text-white`}
                            >
                                {number}
                            </span>
                        ) : (
                            <Link
                                to={hrefFor(number)}
                                className={`${baseItem} bg-white text-blue-600 hover:bg-gray-50`}
                            >
                                {number}
                            </Link>
                        )}
                    </li>
                ))}
                {last < totalPages && (
                    <li aria-hidden="true" className="px-1 text-gray-400">
                        …
                    </li>
                )}
                <li>{step(t.pagination.next, page + 1, page >= totalPages)}</li>
                <li>
                    {step(t.pagination.last, totalPages, page >= totalPages)}
                </li>
            </ul>
        </nav>
    );
}
