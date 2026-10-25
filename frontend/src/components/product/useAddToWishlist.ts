import { useState } from "react";
import { useNavigate } from "react-router";

import { addToWishlist } from "../../api/wishlist.ts";
import { withNext } from "../../auth/authRoutes.ts";
import { useAuth } from "../../context/useAuth.ts";
import { useWishlist } from "../../context/useWishlist.ts";

interface WishlistableProduct {
    id: number;
    slug: string;
}

// Mirrors useAddToCart.ts's logged-out "preserve the intent, redirect to login, resume
// after auth" shape (?addToWishlist=1 instead of ?addToCart=1). Kept as its own small
// hook rather than generalized with useAddToCart — this project tolerates small
// near-identical mixins over a shared abstraction across unrelated concerns (see
// conventions.md). `added` reflects real membership from the shared WishlistContext
// (fetched once for the whole app, not one request per product card), so the heart
// icon already shows filled for a product that's in the wishlist from a previous visit,
// not just right after this exact click. A duplicate add attempt is a no-op (`added`
// guards it) rather than a request that would 400.
export function useAddToWishlist(product: WishlistableProduct) {
    const { user } = useAuth();
    const { items, setItems } = useWishlist();
    const navigate = useNavigate();
    const [pending, setPending] = useState(false);
    const [error, setError] = useState(false);

    const added = items?.some((item) => item.product.id === product.id) ?? false;

    const add = async () => {
        if (pending || added) {
            return;
        }

        if (!user) {
            navigate(withNext("/login", `/product/${product.slug}?addToWishlist=1`));
            return;
        }

        setPending(true);
        setError(false);

        try {
            const updated = await addToWishlist(product.id);
            setItems(updated);
            setPending(false);
        } catch {
            setPending(false);
            setError(true);
        }
    };

    return { add: () => void add(), pending, added, error };
}
