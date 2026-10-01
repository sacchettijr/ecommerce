import { useState } from "react";
import type { ReactNode } from "react";

import { fetchSession } from "../api/auth.ts";
import type { SessionUser } from "../api/types.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { AuthContext } from "./AuthContext.ts";

export function AuthProvider({ children }: { children: ReactNode }) {
    const { data, loading } = useAsync(fetchSession, undefined);
    // Depois de login/logout a resposta desses endpoints vale mais do que a sessão inicial.
    const [override, setOverride] = useState<{
        user: SessionUser | null;
    } | null>(null);

    const user = override ? override.user : (data ?? null);

    return (
        <AuthContext
            value={{
                user,
                loading: loading && override === null,
                setUser: (next) => setOverride({ user: next }),
            }}
        >
            {children}
        </AuthContext>
    );
}
