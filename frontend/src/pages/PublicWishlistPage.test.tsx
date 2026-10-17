import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";

import { ApiError } from "../api/client.ts";
import {
    fetchMyWishlist,
    fetchPublicWishlist,
    fetchWishlistShareLink,
} from "../api/wishlist.ts";
import { makePublicWishlistItem, makeSessionUser, makeWishlistItem } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { PublicWishlistPage } from "./PublicWishlistPage.tsx";

vi.mock("../api/wishlist.ts", () => ({
    fetchPublicWishlist: vi.fn(),
    fetchWishlistShareLink: vi.fn(),
    fetchMyWishlist: vi.fn(),
    addToWishlist: vi.fn(),
    removeFromWishlistItem: vi.fn(),
    toggleWishlistItemPrivacy: vi.fn(),
    moveWishlistItem: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchPublicWishlist);
const mockedShareLink = vi.mocked(fetchWishlistShareLink);
const mockedMyWishlist = vi.mocked(fetchMyWishlist);

beforeEach(() => {
    mockedFetch.mockReset();
    mockedShareLink.mockReset();
    mockedMyWishlist.mockReset();
});

describe("PublicWishlistPage", () => {
    it("renders a 404 page for an unknown public id", async () => {
        mockedFetch.mockRejectedValue(new ApiError(404, {}));

        renderWithProviders(<PublicWishlistPage />, {
            route: "/wishlist/does-not-exist",
            path: "wishlist/:publicId",
        });

        expect(await screen.findByText(/page not found/i)).toBeInTheDocument();
    });

    it("shows the empty state when there are no public items", async () => {
        mockedFetch.mockResolvedValue({ public_id: "abc", items: [] });

        renderWithProviders(<PublicWishlistPage />, {
            route: "/wishlist/abc",
            path: "wishlist/:publicId",
        });

        expect(
            await screen.findByText("This wishlist has no public items yet."),
        ).toBeInTheDocument();
    });

    it("renders public items with the gift button and no edit/delete controls", async () => {
        mockedFetch.mockResolvedValue({
            public_id: "abc",
            items: [
                makePublicWishlistItem({
                    id: 1,
                    product: {
                        id: 10,
                        name: "Blue Mug",
                        slug: "blue-mug",
                        price: "19.90",
                        thumbnail: null,
                    },
                }),
            ],
        });

        renderWithProviders(<PublicWishlistPage />, {
            route: "/wishlist/abc",
            path: "wishlist/:publicId",
        });

        await screen.findByText("Blue Mug");

        const giftButton = screen.getByRole("button", {
            name: "Give as a gift",
        });
        expect(giftButton).toHaveAttribute("aria-disabled", "true");

        expect(
            screen.queryByRole("button", { name: /remove/i }),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByRole("button", { name: /move .* up/i }),
        ).not.toBeInTheDocument();
        expect(screen.queryByRole("button", { name: "Public" })).not.toBeInTheDocument();
        expect(screen.queryByRole("button", { name: "Private" })).not.toBeInTheDocument();
    });

    it("shows the own, editable wishlist page when the visitor owns this exact public link", async () => {
        mockedFetch.mockResolvedValue({
            public_id: "abc",
            items: [makePublicWishlistItem({ id: 1 })],
        });
        mockedShareLink.mockResolvedValue({ public_id: "abc" });
        mockedMyWishlist.mockResolvedValue([
            makeWishlistItem({ id: 1, private: true }),
        ]);

        renderWithProviders(<PublicWishlistPage />, {
            user: makeSessionUser(),
            route: "/wishlist/abc",
            path: "wishlist/:publicId",
        });

        // Swaps from the public-only view to the full WishlistPage once ownership is
        // confirmed — the private item and its owner-only controls become visible.
        expect(
            await screen.findByRole("button", { name: "Private" }),
        ).toBeInTheDocument();
        expect(
            screen.queryByRole("button", { name: "Give as a gift" }),
        ).not.toBeInTheDocument();
    });

    it("keeps the public-only view for a signed-in visitor who isn't the owner", async () => {
        mockedFetch.mockResolvedValue({
            public_id: "abc",
            items: [makePublicWishlistItem({ id: 1 })],
        });
        mockedShareLink.mockResolvedValue({ public_id: "someone-else" });

        renderWithProviders(<PublicWishlistPage />, {
            user: makeSessionUser(),
            route: "/wishlist/abc",
            path: "wishlist/:publicId",
        });

        expect(
            await screen.findByRole("button", { name: "Give as a gift" }),
        ).toBeInTheDocument();
        expect(mockedMyWishlist).not.toHaveBeenCalled();
    });
});
