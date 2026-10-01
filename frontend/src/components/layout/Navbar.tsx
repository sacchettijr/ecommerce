import { useState } from "react";
import type { FormEvent } from "react";
import {
    Link,
    NavLink,
    useLocation,
    useNavigate,
    useSearchParams,
} from "react-router";

import { isAuthPath, withNext } from "../../auth/authRoutes.ts";
import { useAuth } from "../../context/useAuth.ts";
import { useCategories } from "../../context/useCategories.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { Dropdown } from "../ui/Dropdown.tsx";
import { CloseIcon, MenuIcon } from "../ui/icons.tsx";
import { LanguagePicker } from "./LanguagePicker.tsx";
import { UserMenu } from "./UserMenu.tsx";

const navLinkClassName = ({ isActive }: { isActive: boolean }): string =>
    `block rounded px-3 py-2 hover:text-white ${
        isActive ? "text-white" : "text-gray-300"
    }`;

export function Navbar() {
    const [open, setOpen] = useState(false);
    const { categories, loading, error } = useCategories();
    const { t } = useLanguage();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const currentSearch = searchParams.get("q") ?? "";
    const { user } = useAuth();
    const location = useLocation();
    // Voltar para a página atual depois de entrar (exceto nas próprias páginas de autenticação).
    const loginNext = isAuthPath(location.pathname)
        ? ""
        : `${location.pathname}${location.search}`;

    const closeMenu = () => setOpen(false);

    const onSearch = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const term = new FormData(event.currentTarget)
            .get("q")
            ?.toString()
            .trim();

        closeMenu();
        navigate(
            term ? `/products?q=${encodeURIComponent(term)}` : "/products",
        );
    };

    return (
        <header className="bg-gray-900">
            <nav className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-3">
                <Link to="/" onClick={closeMenu}>
                    <img
                        src="/img/logomarca.png"
                        alt="E-Commerce"
                        className="h-10 w-auto"
                    />
                </Link>

                <button
                    type="button"
                    aria-label={t.nav.toggleNav}
                    aria-expanded={open}
                    aria-controls="navbar-content"
                    onClick={() => setOpen((current) => !current)}
                    className="rounded border border-gray-600 p-2 text-gray-300 hover:text-white lg:hidden"
                >
                    {open ? (
                        <CloseIcon className="size-6" />
                    ) : (
                        <MenuIcon className="size-6" />
                    )}
                </button>

                <div
                    id="navbar-content"
                    className={`${open ? "block" : "hidden"} w-full lg:flex lg:w-auto lg:flex-1 lg:items-center lg:justify-between`}
                >
                    <ul className="mt-2 lg:mt-0 lg:flex lg:items-center">
                        <li>
                            <NavLink
                                to="/"
                                end
                                onClick={closeMenu}
                                className={navLinkClassName}
                            >
                                {t.nav.home}
                            </NavLink>
                        </li>
                        <li>
                            <Dropdown label={t.nav.category}>
                                {(close) => (
                                    <>
                                        <p className="px-4 py-2 text-xs font-semibold uppercase text-gray-500">
                                            {t.nav.categories}
                                        </p>
                                        {categories.map((category) => (
                                            <Link
                                                key={category.id}
                                                to={`/category/${category.slug}`}
                                                role="menuitem"
                                                onClick={() => {
                                                    close();
                                                    closeMenu();
                                                }}
                                                className="block px-4 py-2 hover:bg-gray-100"
                                            >
                                                {category.name}
                                            </Link>
                                        ))}
                                        {categories.length === 0 && (
                                            <span className="block px-4 py-2 text-sm italic text-gray-500">
                                                {loading
                                                    ? t.common.loading
                                                    : error
                                                      ? t.nav.loadError
                                                      : t.nav.noCategories}
                                            </span>
                                        )}
                                    </>
                                )}
                            </Dropdown>
                        </li>
                        <li>
                            <NavLink
                                to="/contact"
                                onClick={closeMenu}
                                className={navLinkClassName}
                            >
                                {t.nav.contact}
                            </NavLink>
                        </li>
                    </ul>

                    <form
                        role="search"
                        onSubmit={onSearch}
                        className="my-3 flex gap-2 lg:my-0 lg:mx-4"
                    >
                        <input
                            key={currentSearch}
                            type="search"
                            name="q"
                            defaultValue={currentSearch}
                            placeholder={t.nav.searchPlaceholder}
                            aria-label={t.nav.search}
                            className="w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-1.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
                        />
                        <button
                            type="submit"
                            className="rounded-lg border border-gray-400 px-3 py-1.5 text-gray-200 hover:bg-gray-800"
                        >
                            {t.nav.search}
                        </button>
                    </form>

                    <ul className="flex items-center gap-1 lg:gap-0">
                        <li>
                            <LanguagePicker />
                        </li>
                        <li>
                            {user ? (
                                <UserMenu
                                    user={user}
                                    onCloseMobileMenu={closeMenu}
                                />
                            ) : (
                                <Link
                                    to={withNext("/login", loginNext)}
                                    onClick={closeMenu}
                                    className="block rounded px-3 py-2 text-gray-300 hover:text-white"
                                >
                                    {t.nav.login}
                                </Link>
                            )}
                        </li>
                        <li>
                            <a
                                href="#"
                                className="block rounded px-3 py-2 text-gray-300 hover:text-white"
                            >
                                {t.nav.cart}
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>
        </header>
    );
}
