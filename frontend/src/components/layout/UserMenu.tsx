import { useNavigate } from "react-router";

import { logout } from "../../api/auth.ts";
import type { SessionUser } from "../../api/types.ts";
import { useAuth } from "../../context/useAuth.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { Dropdown } from "../ui/Dropdown.tsx";
import {
    ArchiveBoxIcon,
    ArrowRightOnRectangleIcon,
    HeartIcon,
    LockClosedIcon,
    MapPinIcon,
    PencilIcon,
    ShieldCheckIcon,
    UserIcon,
} from "../ui/icons.tsx";

const itemClassName =
    "flex w-full items-center gap-2 px-4 py-2 text-left hover:bg-gray-100";

interface UserMenuProps {
    user: SessionUser;
    // Fecha também o menu hambúrguer (mobile) quando uma opção é escolhida.
    onCloseMobileMenu: () => void;
}

// Menu do usuário autenticado, equivalente em função ao dropdown de
// frontend.old/core/base.html, reconstruído com os componentes do React atual.
export function UserMenu({ user, onCloseMobileMenu }: UserMenuProps) {
    const { t } = useLanguage();
    const { setUser } = useAuth();
    const navigate = useNavigate();

    const onLogout = async (close: () => void) => {
        close();
        onCloseMobileMenu();

        try {
            await logout();
        } catch {
            // Sem resposta do servidor a sessão continua válida; não finge que saiu.
            return;
        }

        setUser(null);
        void navigate("/logged-out");
    };

    return (
        <Dropdown
            label={t.userMenu.hello(user.name.split(" ")[0] ?? user.name)}
            align="right"
        >
            {(close) => {
                const closeAll = () => {
                    close();
                    onCloseMobileMenu();
                };

                return (
                    <>
                        {/* Pedidos ainda não tem uma página própria: segue o mesmo padrão
                            reservado do carrinho do catálogo (ação reservada para quando
                            existir). */}
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                closeAll();
                                void navigate("/profile");
                            }}
                            className={itemClassName}
                        >
                            <UserIcon className="size-5 shrink-0" />
                            {t.userMenu.profile}
                        </button>
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                closeAll();
                                void navigate("/profile/edit");
                            }}
                            className={itemClassName}
                        >
                            <PencilIcon className="size-5 shrink-0" />
                            {t.userMenu.editProfile}
                        </button>
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                closeAll();
                                void navigate("/profile/password");
                            }}
                            className={itemClassName}
                        >
                            <LockClosedIcon className="size-5 shrink-0" />
                            {t.userMenu.changePassword}
                        </button>
                        <button
                            type="button"
                            role="menuitem"
                            className={itemClassName}
                        >
                            <ArchiveBoxIcon className="size-5 shrink-0" />
                            {t.userMenu.orders}
                        </button>
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                closeAll();
                                void navigate("/profile/addresses");
                            }}
                            className={itemClassName}
                        >
                            <MapPinIcon className="size-5 shrink-0" />
                            {t.userMenu.addresses}
                        </button>
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                closeAll();
                                void navigate("/profile/wishlist");
                            }}
                            className={itemClassName}
                        >
                            <HeartIcon className="size-5 shrink-0" />
                            {t.userMenu.wishlist}
                        </button>
                        {user.is_staff && (
                            <a
                                href="/admin/"
                                role="menuitem"
                                className={itemClassName}
                            >
                                <ShieldCheckIcon className="size-5 shrink-0" />
                                {t.userMenu.admin}
                            </a>
                        )}
                        <hr className="my-1 border-gray-200" />
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => void onLogout(closeAll)}
                            className={itemClassName}
                        >
                            <ArrowRightOnRectangleIcon className="size-5 shrink-0" />
                            {t.nav.logout}
                        </button>
                    </>
                );
            }}
        </Dropdown>
    );
}
