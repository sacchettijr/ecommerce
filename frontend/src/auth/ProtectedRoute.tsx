import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";

import { useAuth } from "../context/useAuth.ts";
import { withNext } from "./authRoutes.ts";

interface ProtectedRouteProps {
    children: ReactNode;
}

// Protege rotas que exigem login (ex.: /profile). A segurança real continua no Django —
// isto só evita que a página autenticada pisque na tela antes do redirecionamento.
export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return null;
    }

    if (!user) {
        const next = `${location.pathname}${location.search}`;
        return <Navigate to={withNext("/login", next)} replace />;
    }

    return children;
}
