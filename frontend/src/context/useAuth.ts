import { use } from "react";

import { AuthContext } from "./AuthContext.ts";

export function useAuth() {
    return use(AuthContext);
}
