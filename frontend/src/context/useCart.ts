import { use } from "react";

import { CartContext } from "./CartContext.ts";

export function useCart() {
    return use(CartContext);
}
