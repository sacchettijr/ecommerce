import { use } from "react";

import { WishlistContext } from "./WishlistContext.ts";

export function useWishlist() {
    return use(WishlistContext);
}
