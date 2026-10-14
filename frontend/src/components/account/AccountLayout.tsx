import type { ReactNode } from "react";
import { NavLink } from "react-router";

import { useAuth } from "../../context/useAuth.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import type { PageMessage } from "../../hooks/useMessages.ts";
import { Alert } from "../ui/Alert.tsx";
import {
    ArchiveBoxIcon,
    HeartIcon,
    LockClosedIcon,
    MapPinIcon,
    PencilIcon,
    UserIcon,
} from "../ui/icons.tsx";

interface AccountLayoutProps {
    title: string;
    messages?: PageMessage[];
    onDismissMessage?: (id: number) => void;
    children: ReactNode;
}

const navItemClassName =
    "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium";
const activeNavItemClassName = `${navItemClassName} bg-blue-50 text-blue-700`;
const inactiveNavItemClassName = `${navItemClassName} text-gray-700 hover:bg-gray-50`;
// Itens do menu que ainda não têm página própria (pedidos, endereços, lista de desejos) —
// mesmo tratamento "reservado" já usado pelo UserMenu da navbar.
const reservedNavItemClassName = `${navItemClassName} cursor-default text-gray-400`;

// Layout compartilhado pelas páginas autenticadas da conta (equivalente ao antigo
// accounts/profile_base.html). Novas páginas da conta (editar perfil, pedidos...) devem
// reaproveitar este componente em vez de duplicar a barra lateral.
export function AccountLayout({
    title,
    messages = [],
    onDismissMessage,
    children,
}: AccountLayoutProps) {
    const { t } = useLanguage();
    const { user } = useAuth();

    return (
        <>
            <title>{title}</title>

            <div className="mx-auto max-w-7xl px-4 py-8">
                <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
                    <aside className="lg:col-span-1">
                        <nav
                            aria-label={t.account.navAriaLabel}
                            className="space-y-1 rounded-lg bg-white p-2 shadow-sm ring-1 ring-gray-200"
                        >
                            <NavLink
                                to="/profile"
                                end
                                className={({ isActive }) =>
                                    isActive
                                        ? activeNavItemClassName
                                        : inactiveNavItemClassName
                                }
                            >
                                <UserIcon className="size-5 shrink-0" />
                                {t.userMenu.profile}
                            </NavLink>
                            <NavLink
                                to="/profile/edit"
                                end
                                className={({ isActive }) =>
                                    isActive
                                        ? activeNavItemClassName
                                        : inactiveNavItemClassName
                                }
                            >
                                <PencilIcon className="size-5 shrink-0" />
                                {t.userMenu.editProfile}
                            </NavLink>
                            <NavLink
                                to="/profile/password"
                                end
                                className={({ isActive }) =>
                                    isActive
                                        ? activeNavItemClassName
                                        : inactiveNavItemClassName
                                }
                            >
                                <LockClosedIcon className="size-5 shrink-0" />
                                {t.userMenu.changePassword}
                            </NavLink>
                            <span className={reservedNavItemClassName}>
                                <ArchiveBoxIcon className="size-5 shrink-0" />
                                {t.userMenu.orders}
                            </span>
                            <span className={reservedNavItemClassName}>
                                <MapPinIcon className="size-5 shrink-0" />
                                {t.userMenu.addresses}
                            </span>
                            <span className={reservedNavItemClassName}>
                                <HeartIcon className="size-5 shrink-0" />
                                {t.userMenu.wishlist}
                            </span>
                            {user?.is_staff && (
                                <a
                                    href="/admin/"
                                    className={inactiveNavItemClassName}
                                >
                                    {t.userMenu.admin}
                                </a>
                            )}
                        </nav>
                    </aside>

                    <section className="lg:col-span-3">
                        {messages.map((message) =>
                            onDismissMessage ? (
                                <Alert
                                    key={message.id}
                                    variant={message.variant}
                                    onDismiss={() =>
                                        onDismissMessage(message.id)
                                    }
                                    dismissLabel={t.common.dismiss}
                                >
                                    {message.text}
                                </Alert>
                            ) : (
                                <Alert key={message.id} variant={message.variant}>
                                    {message.text}
                                </Alert>
                            ),
                        )}

                        {children}
                    </section>
                </div>
            </div>
        </>
    );
}
