import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { addToCart } from "../../api/cart.ts";
import type { Product } from "../../api/types.ts";
import { makeCartSummary, makeSessionUser } from "../../test/fixtures.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { ProductCard } from "./ProductCard.tsx";

vi.mock("../../api/cart.ts", () => ({
    fetchCart: vi.fn(),
    addToCart: vi.fn(),
    updateCartItemQuantity: vi.fn(),
    removeCartItem: vi.fn(),
}));

const mockedNavigate = vi.fn();

vi.mock("react-router", async (importOriginal) => ({
    ...(await importOriginal<typeof import("react-router")>()),
    useNavigate: () => mockedNavigate,
}));

const mockedAddToCart = vi.mocked(addToCart);

beforeEach(() => {
    mockedAddToCart.mockReset();
    mockedNavigate.mockReset();
});

function buildProduct(overrides: Partial<Product> = {}): Product {
    return {
        id: 1,
        name: "Wireless Keyboard",
        slug: "wireless-keyboard",
        price: "199.90",
        thumbnail: "/media/products/wireless-keyboard.jpg",
        active: true,
        ...overrides,
    };
}

describe("ProductCard", () => {
    it("links the image to the product page, same as the details button", () => {
        renderWithProviders(<ProductCard product={buildProduct()} />);

        expect(screen.getByRole("img", { name: "Wireless Keyboard" }).closest("a")).toHaveAttribute(
            "href",
            "/product/wireless-keyboard",
        );
    });

    it("links the title to the product page, same as the details button", () => {
        renderWithProviders(<ProductCard product={buildProduct()} />);

        const title = screen.getByRole("heading", { name: "Wireless Keyboard" });
        expect(title.querySelector("a")).toHaveAttribute("href", "/product/wireless-keyboard");
    });

    it("links the no-image placeholder to the product page too", () => {
        renderWithProviders(<ProductCard product={buildProduct({ thumbnail: null })} />);

        expect(screen.getByText("No image").closest("a")).toHaveAttribute(
            "href",
            "/product/wireless-keyboard",
        );
    });

    it("logged in: clicking add to cart adds the product and navigates to /cart", async () => {
        const user = userEvent.setup();
        mockedAddToCart.mockResolvedValue(makeCartSummary());

        renderWithProviders(<ProductCard product={buildProduct()} />, {
            user: makeSessionUser(),
        });

        await user.click(
            screen.getByRole("button", { name: "Add Wireless Keyboard to cart" }),
        );

        expect(mockedAddToCart).toHaveBeenCalledWith(1);
        expect(mockedNavigate).toHaveBeenCalledWith("/cart");
    });

    it("logged out: clicking add to cart redirects to login, preserving the resume intent", async () => {
        const user = userEvent.setup();

        renderWithProviders(<ProductCard product={buildProduct()} />);

        await user.click(
            screen.getByRole("button", { name: "Add Wireless Keyboard to cart" }),
        );

        expect(mockedAddToCart).not.toHaveBeenCalled();
        expect(mockedNavigate).toHaveBeenCalledWith(
            "/login?next=%2Fproduct%2Fwireless-keyboard%3FaddToCart%3D1",
        );
    });
});
