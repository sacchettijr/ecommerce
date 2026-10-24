import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { fetchCart, removeCartItem, updateCartItemQuantity } from "../api/cart.ts";
import { makeCartItem, makeCartSummary, makeSessionUser } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { CartPage } from "./CartPage.tsx";

vi.mock("../api/cart.ts", () => ({
    fetchCart: vi.fn(),
    addToCart: vi.fn(),
    updateCartItemQuantity: vi.fn(),
    removeCartItem: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchCart);
const mockedUpdate = vi.mocked(updateCartItemQuantity);
const mockedRemove = vi.mocked(removeCartItem);

beforeEach(() => {
    mockedFetch.mockReset();
    mockedUpdate.mockReset();
    mockedRemove.mockReset();
});

describe("CartPage", () => {
    it("shows a loading state", () => {
        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cartLoading: true,
        });

        expect(screen.getByText("Loading…")).toBeInTheDocument();
    });

    it("shows an error notification when the cart failed to load", () => {
        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cartError: true,
        });

        expect(screen.getByText("Could not load your cart.")).toBeInTheDocument();
    });

    it("shows the empty-state message with a link to the product list", () => {
        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary(),
        });

        expect(screen.getByText(/Your cart is empty\./)).toBeInTheDocument();
        const link = screen.getByRole("link", { name: "Browse products" });
        expect(link).toHaveAttribute("href", "/products");
    });

    it("renders each item's thumbnail, name, unit price, quantity, and line total", () => {
        const item = makeCartItem({
            id: 1,
            quantity: 2,
            unit_price: "10.00",
            line_total: "20.00",
            product: {
                id: 5,
                name: "Blue Mug",
                slug: "blue-mug",
                price: "10.00",
                thumbnail: null,
                active: true,
            },
        });

        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({ items: [item], subtotal: "20.00", total: "99.99" }),
        });

        expect(screen.getByText("Blue Mug")).toBeInTheDocument();
        expect(screen.getByText("blue-mug")).toBeInTheDocument();
        expect(screen.getByText(/\$10\.00/)).toBeInTheDocument();
        expect(screen.getByLabelText("Quantity: 2")).toBeInTheDocument();
        expect(screen.getByText(/\$20\.00/)).toBeInTheDocument();
    });

    it("shows the discount and total lines", () => {
        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({
                items: [makeCartItem()],
                subtotal: "19.90",
                discount_total: "0.00",
                total: "19.90",
            }),
        });

        expect(screen.getByText("Discount")).toBeInTheDocument();
        expect(screen.getByText("Total to pay")).toBeInTheDocument();
    });

    it("increasing the quantity calls the API and reflects the fresh summary", async () => {
        const user = userEvent.setup();
        const item = makeCartItem({ id: 1, quantity: 1 });
        const setCart = vi.fn();
        const updated = makeCartSummary({
            items: [makeCartItem({ id: 1, quantity: 2, line_total: "39.80" })],
            total: "39.80",
        });
        mockedUpdate.mockResolvedValue(updated);

        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({ items: [item] }),
            setCart,
        });

        await user.click(screen.getByLabelText("Increase quantity of Blue Mug"));

        expect(mockedUpdate).toHaveBeenCalledWith(1, 2, expect.anything());
        expect(setCart).toHaveBeenCalledWith(updated);
    });

    it("decreasing the quantity below 1 is disabled, not sent to the API", () => {
        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({ items: [makeCartItem({ id: 1, quantity: 1 })] }),
        });

        expect(screen.getByLabelText("Decrease quantity of Blue Mug")).toBeDisabled();
    });

    it("removing an item calls the API and shows a success message", async () => {
        const user = userEvent.setup();
        const setCart = vi.fn();
        const updated = makeCartSummary();
        mockedRemove.mockResolvedValue(updated);

        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({ items: [makeCartItem({ id: 1 })] }),
            setCart,
        });

        await user.click(screen.getByLabelText("Remove Blue Mug from cart"));

        expect(mockedRemove).toHaveBeenCalledWith(1, expect.anything());
        expect(await screen.findByText("Item removed from your cart.")).toBeInTheDocument();
        expect(setCart).toHaveBeenCalledWith(updated);
    });

    it("the coupon field and button do nothing: no request, no message, no total change", async () => {
        const user = userEvent.setup();
        const item = makeCartItem({ unit_price: "12.34", line_total: "12.34" });

        renderWithProviders(<CartPage />, {
            user: makeSessionUser(),
            cart: makeCartSummary({ items: [item], total: "19.90" }),
        });

        await user.type(screen.getByLabelText("Discount coupon"), "SAVE10");
        await user.click(screen.getByRole("button", { name: "Apply" }));

        expect(mockedFetch).not.toHaveBeenCalled();
        expect(mockedUpdate).not.toHaveBeenCalled();
        expect(mockedRemove).not.toHaveBeenCalled();
        expect(screen.getByText(/\$19\.90/)).toBeInTheDocument();
    });
});
