import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import {
    fetchMyWishlist,
    fetchWishlistShareLink,
    moveWishlistItem,
    removeFromWishlistItem,
    toggleWishlistItemPrivacy,
} from "../api/wishlist.ts";
import { makeSessionUser, makeWishlistItem } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { WishlistPage } from "./WishlistPage.tsx";

vi.mock("../api/wishlist.ts", () => ({
    fetchMyWishlist: vi.fn(),
    addToWishlist: vi.fn(),
    removeFromWishlistItem: vi.fn(),
    toggleWishlistItemPrivacy: vi.fn(),
    moveWishlistItem: vi.fn(),
    fetchWishlistShareLink: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchMyWishlist);
const mockedRemove = vi.mocked(removeFromWishlistItem);
const mockedToggle = vi.mocked(toggleWishlistItemPrivacy);
const mockedMove = vi.mocked(moveWishlistItem);
const mockedShareLink = vi.mocked(fetchWishlistShareLink);

beforeEach(() => {
    mockedFetch.mockReset();
    mockedRemove.mockReset();
    mockedToggle.mockReset();
    mockedMove.mockReset();
    mockedShareLink.mockReset();
});

describe("WishlistPage", () => {
    it("shows a loading state before the items arrive", () => {
        mockedFetch.mockImplementation(() => new Promise(() => {}));

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        expect(screen.getByText("Loading…")).toBeInTheDocument();
    });

    it("shows an error notification when the request fails", async () => {
        mockedFetch.mockRejectedValue(new Error("network down"));

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        expect(
            await screen.findByText(
                "Could not load your wishlist. Please try again.",
            ),
        ).toBeInTheDocument();
    });

    it("shows the empty-state message when there are no items", async () => {
        mockedFetch.mockResolvedValue([]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        expect(
            await screen.findByText("Your wishlist is empty."),
        ).toBeInTheDocument();
    });

    it("renders thumbnail, name, price, date and priority for each item", async () => {
        mockedFetch.mockResolvedValue([
            makeWishlistItem({
                id: 1,
                position: 0,
                product: {
                    id: 10,
                    name: "Blue Mug",
                    slug: "blue-mug",
                    price: "19.90",
                    thumbnail: null,
                },
            }),
        ]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        await screen.findByText("Blue Mug");
        expect(screen.getByText("$19.90")).toBeInTheDocument();
        expect(screen.getByLabelText("Priority 1")).toHaveTextContent("1");
    });

    it("moving the first item up is disabled; moving it down calls the API", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeWishlistItem({ id: 1, position: 0 }),
            makeWishlistItem({ id: 2, position: 1 }),
        ]);
        mockedMove.mockResolvedValue([
            makeWishlistItem({ id: 2, position: 0 }),
            makeWishlistItem({ id: 1, position: 1 }),
        ]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        await screen.findByLabelText("Priority 1");
        const upButtons = screen.getAllByRole("button", { name: /move .* up/i });
        expect(upButtons[0]).toBeDisabled();

        const downButtons = screen.getAllByRole("button", {
            name: /move .* down/i,
        });
        await user.click(downButtons[0]);

        expect(mockedMove).toHaveBeenCalledWith(1, "down", expect.anything());
    });

    it("removing an item calls the API and shows a success message", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([makeWishlistItem({ id: 1 })]);
        mockedRemove.mockResolvedValue([]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        const removeButton = await screen.findByRole("button", {
            name: /remove .* from your wishlist/i,
        });
        await user.click(removeButton);

        expect(mockedRemove).toHaveBeenCalledWith(1, expect.anything());
        expect(
            await screen.findByText("Item removed from your wishlist."),
        ).toBeInTheDocument();
        expect(
            await screen.findByText("Your wishlist is empty."),
        ).toBeInTheDocument();
    });

    it("toggling privacy calls the API and reflects the new state", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeWishlistItem({ id: 1, private: false }),
        ]);
        mockedToggle.mockResolvedValue([
            makeWishlistItem({ id: 1, private: true }),
        ]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        const toggleButton = await screen.findByRole("button", {
            name: "Public",
        });
        await user.click(toggleButton);

        expect(mockedToggle).toHaveBeenCalledWith(1, expect.anything());
        expect(await screen.findByRole("button", { name: "Private" })).toBeInTheDocument();
        expect(screen.queryByRole("alert")).not.toBeInTheDocument();
        expect(screen.queryByRole("status")).not.toBeInTheDocument();
    });

    it("sorting by price reorders the list and disables the move buttons", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeWishlistItem({
                id: 1,
                position: 0,
                product: {
                    id: 10,
                    name: "Expensive Thing",
                    slug: "expensive-thing",
                    price: "99.00",
                    thumbnail: null,
                },
            }),
            makeWishlistItem({
                id: 2,
                position: 1,
                product: {
                    id: 20,
                    name: "Cheap Thing",
                    slug: "cheap-thing",
                    price: "5.00",
                    thumbnail: null,
                },
            }),
        ]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        await screen.findByText("Expensive Thing");
        const names = () =>
            screen
                .getAllByRole("heading", { level: 3 })
                .map((heading) => heading.textContent);
        expect(names()).toEqual(["Expensive Thing", "Cheap Thing"]);

        await user.selectOptions(
            screen.getByLabelText("Sort by"),
            "Price: low to high",
        );

        expect(names()).toEqual(["Cheap Thing", "Expensive Thing"]);
        for (const button of screen.getAllByRole("button", {
            name: /move .* (up|down)/i,
        })) {
            expect(button).toBeDisabled();
        }
    });

    it("switching back to priority sort re-enables the move buttons", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeWishlistItem({ id: 1, position: 0 }),
            makeWishlistItem({ id: 2, position: 1 }),
        ]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        await screen.findByLabelText("Priority 1");
        const sortSelect = screen.getByLabelText("Sort by");
        await user.selectOptions(sortSelect, "Price: low to high");
        await user.selectOptions(sortSelect, "Priority");

        const downButtons = screen.getAllByRole("button", {
            name: /move .* down/i,
        });
        expect(downButtons[0]).not.toBeDisabled();
    });

    it("the Add to cart button is inert: no request, no navigation", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([makeWishlistItem({ id: 1 })]);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        const cartButton = await screen.findByRole("button", {
            name: "Add to cart",
        });
        expect(cartButton).toHaveAttribute("aria-disabled", "true");

        await user.click(cartButton);

        expect(mockedFetch).toHaveBeenCalledTimes(1);
    });

    it("copies the public share link to the clipboard", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([]);
        mockedShareLink.mockResolvedValue({ public_id: "abc-123" });
        vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue(undefined);

        renderWithProviders(<WishlistPage />, { user: makeSessionUser() });

        await user.click(
            await screen.findByRole("button", { name: "Share my wishlist" }),
        );

        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
            expect.stringContaining("/wishlist/abc-123"),
        );
        expect(
            await screen.findByText("Link copied to clipboard."),
        ).toBeInTheDocument();
    });
});
