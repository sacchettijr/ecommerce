import { createContext } from "react";

import type { SessionUser } from "../api/types.ts";

export interface AuthState {
    user: SessionUser | null;
    // true até a primeira resposta do endpoint de sessão.
    loading: boolean;
    setUser: (user: SessionUser | null) => void;
}

export const AuthContext = createContext<AuthState>({
    user: null,
    loading: true,
    setUser: () => {},
});
