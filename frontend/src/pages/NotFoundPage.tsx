import { Link } from "react-router";

import { useLanguage } from "../i18n/useLanguage.ts";

export function NotFoundPage() {
    const { t } = useLanguage();

    return (
        <>
            <title>{t.notFound.title}</title>

            <div className="mx-auto max-w-7xl px-4 py-24 text-center">
                <h1 className="mb-3 text-4xl font-bold">
                    {t.notFound.heading}
                </h1>
                <p className="mb-6 text-gray-500">{t.notFound.description}</p>
                <Link
                    to="/"
                    className="inline-block rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
                >
                    {t.notFound.backHome}
                </Link>
            </div>
        </>
    );
}
