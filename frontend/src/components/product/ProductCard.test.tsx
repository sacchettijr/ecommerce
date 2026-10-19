import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import type { Product } from "../../api/types.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { ProductCard } from "./ProductCard.tsx";

function buildProduct(overrides: Partial<Product> = {}): Product {
    return {
        id: 1,
        name: "Wireless Keyboard",
        slug: "wireless-keyboard",
        price: "199.90",
        thumbnail: "/media/products/wireless-keyboard.jpg",
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
});
