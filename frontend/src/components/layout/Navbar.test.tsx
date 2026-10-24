import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { makeCartItem, makeCartSummary } from "../../test/fixtures.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { Navbar } from "./Navbar.tsx";

describe("Navbar", () => {
    it("shows a cart count of 0 when there is no cart (logged out)", () => {
        renderWithProviders(<Navbar />);

        const link = screen.getByRole("link", { name: "Cart (0)" });
        expect(link).toHaveAttribute("href", "/cart");
    });

    it("shows the live item count from CartContext", () => {
        renderWithProviders(<Navbar />, {
            cart: makeCartSummary({ items: [makeCartItem(), makeCartItem({ id: 2 })] }),
        });

        expect(screen.getByRole("link", { name: "Cart (2)" })).toBeInTheDocument();
    });
});
