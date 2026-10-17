import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { fetchProduct } from "../api/products.ts";
import type { ProductDetail } from "../api/types.ts";
import {
    addToWishlist,
    checkWishlistMembership,
    removeFromWishlistItem,
} from "../api/wishlist.ts";
import { makeSessionUser, makeWishlistItem } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { ProductDetailPage } from "./ProductDetailPage.tsx";

vi.mock("../api/products.ts", () => ({
    fetchProduct: vi.fn(),
}));

vi.mock("../api/wishlist.ts", () => ({
    checkWishlistMembership: vi.fn(),
    addToWishlist: vi.fn(),
    removeFromWishlistItem: vi.fn(),
}));

const mockedFetchProduct = vi.mocked(fetchProduct);
const mockedCheck = vi.mocked(checkWishlistMembership);
const mockedAdd = vi.mocked(addToWishlist);
const mockedRemove = vi.mocked(removeFromWishlistItem);

function makeProductDetail(
    overrides: Partial<ProductDetail> = {},
): ProductDetail {
    return {
        id: 10,
        name: "Blue Mug",
        slug: "blue-mug",
        category: { id: 1, name: "Kitchen", slug: "kitchen" },
        description: null,
        price: "19.90",
        images: [],
        ...overrides,
    };
}

beforeEach(() => {
    mockedFetchProduct.mockReset();
    mockedCheck.mockReset();
    mockedAdd.mockReset();
    mockedRemove.mockReset();
});

describe("ProductDetailPage wishlist button", () => {
    it("shows a login link for guests instead of a wishlist button", async () => {
        mockedFetchProduct.mockResolvedValue(makeProductDetail());

        renderWithProviders(<ProductDetailPage />, {
            route: "/product/blue-mug",
            path: "product/:slug",
        });

        const link = await screen.findByRole("link", {
            name: "Add to wishlist",
        });
        expect(link).toHaveAttribute("href", expect.stringContaining("/login"));
        expect(mockedCheck).not.toHaveBeenCalled();
    });

    it("shows 'Add to wishlist' when the product is absent, and adds it on click", async () => {
        const user = userEvent.setup();
        mockedFetchProduct.mockResolvedValue(makeProductDetail());
        mockedCheck.mockResolvedValue({ in_wishlist: false, item_id: null });
        mockedAdd.mockResolvedValue([makeWishlistItem({ id: 5, product: { id: 10, name: "Blue Mug", slug: "blue-mug", price: "19.90", thumbnail: null } })]);

        renderWithProviders(<ProductDetailPage />, {
            user: makeSessionUser(),
            route: "/product/blue-mug",
            path: "product/:slug",
        });

        const button = await screen.findByRole("button", {
            name: "Add to wishlist",
        });
        await user.click(button);

        expect(mockedAdd).toHaveBeenCalledWith(10, expect.anything());
        expect(
            await screen.findByRole("button", { name: "Remove from wishlist" }),
        ).toBeInTheDocument();
    });

    it("shows 'Remove from wishlist' when the product is already present, and removes it on click", async () => {
        const user = userEvent.setup();
        mockedFetchProduct.mockResolvedValue(makeProductDetail());
        mockedCheck.mockResolvedValue({ in_wishlist: true, item_id: 7 });
        mockedRemove.mockResolvedValue([]);

        renderWithProviders(<ProductDetailPage />, {
            user: makeSessionUser(),
            route: "/product/blue-mug",
            path: "product/:slug",
        });

        const button = await screen.findByRole("button", {
            name: "Remove from wishlist",
        });
        await user.click(button);

        expect(mockedRemove).toHaveBeenCalledWith(7, expect.anything());
        expect(
            await screen.findByRole("button", { name: "Add to wishlist" }),
        ).toBeInTheDocument();
    });

    it("keeps the previous visual state when the backend request fails", async () => {
        const user = userEvent.setup();
        mockedFetchProduct.mockResolvedValue(makeProductDetail());
        mockedCheck.mockResolvedValue({ in_wishlist: false, item_id: null });
        mockedAdd.mockRejectedValue(new Error("boom"));

        renderWithProviders(<ProductDetailPage />, {
            user: makeSessionUser(),
            route: "/product/blue-mug",
            path: "product/:slug",
        });

        const button = await screen.findByRole("button", {
            name: "Add to wishlist",
        });
        await user.click(button);

        expect(
            await screen.findByText(
                "Could not update your wishlist. Please try again.",
            ),
        ).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: "Add to wishlist" }),
        ).toBeInTheDocument();
    });

    it("the button starts disabled until the initial check resolves, preventing duplicate requests", async () => {
        let resolveCheck: (value: { in_wishlist: boolean; item_id: number | null }) => void =
            () => {};
        mockedFetchProduct.mockResolvedValue(makeProductDetail());
        mockedCheck.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveCheck = resolve;
                }),
        );

        renderWithProviders(<ProductDetailPage />, {
            user: makeSessionUser(),
            route: "/product/blue-mug",
            path: "product/:slug",
        });

        const button = await screen.findByRole("button", {
            name: "Add to wishlist",
        });
        expect(button).toBeDisabled();

        resolveCheck({ in_wishlist: false, item_id: null });
        await waitFor(() => expect(button).not.toBeDisabled());
        expect(mockedCheck).toHaveBeenCalledTimes(1);
    });
});
