import { useState } from "react";
import { useNavigate } from "react-router";

import { addToCart } from "../../api/cart.ts";
import { withNext } from "../../auth/authRoutes.ts";
import { useAuth } from "../../context/useAuth.ts";
import { useCart } from "../../context/useCart.ts";

interface AddableProduct {
    id: number;
    slug: string;
}

// Shared by ProductCard and ProductDetailPage so the logged-out "preserve the intent,
// redirect to login, resume after auth" flow is written and tested exactly once. The
// product page is always the resume target (?addToCart=1), since the grid has nowhere of
// its own to land back on — ProductDetailPage reads that flag on mount.
export function useAddToCart(product: AddableProduct) {
    const { user } = useAuth();
    const { setCart } = useCart();
    const navigate = useNavigate();
    const [pending, setPending] = useState(false);
    const [error, setError] = useState(false);

    const add = async () => {
        if (pending) {
            return;
        }

        if (!user) {
            navigate(withNext("/login", `/product/${product.slug}?addToCart=1`));
            return;
        }

        setPending(true);
        setError(false);

        try {
            const summary = await addToCart(product.id);
            setCart(summary);
            navigate("/cart");
        } catch {
            setPending(false);
            setError(true);
        }
    };

    return { add: () => void add(), pending, error };
}
