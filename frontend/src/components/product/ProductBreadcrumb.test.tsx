import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { ProductBreadcrumb } from "./ProductBreadcrumb.tsx";

describe("ProductBreadcrumb", () => {
    it("renders a short product name in full, without truncation styling needed", () => {
        renderWithProviders(
            <ProductBreadcrumb
                categoryName="Shoes"
                categorySlug="shoes"
                productName="Red Sneakers"
            />,
        );

        expect(screen.getByText("Red Sneakers")).toBeInTheDocument();
        expect(screen.getByText("Shoes")).toBeInTheDocument();
    });

    it("keeps the full product name in the DOM and as a title attribute even when visually truncated", () => {
        const longName =
            "Premium Hand-Stitched Leather Running Shoes With Extra Cushioning";

        renderWithProviders(
            <ProductBreadcrumb
                categoryName="Shoes"
                categorySlug="shoes"
                productName={longName}
            />,
        );

        const item = screen.getByText(longName);
        expect(item).toBeInTheDocument();
        expect(item).toHaveAttribute("title", longName);
        expect(item.className).toContain("truncate");
    });

    it("does not truncate the category segment", () => {
        const longCategory = "Outdoor and Hiking Equipment";

        renderWithProviders(
            <ProductBreadcrumb
                categoryName={longCategory}
                categorySlug="outdoor"
                productName="Tent"
            />,
        );

        const categoryLink = screen.getByText(longCategory);
        expect(categoryLink.className).not.toContain("truncate");
    });

    it("links the category segment to the category page", () => {
        renderWithProviders(
            <ProductBreadcrumb
                categoryName="Shoes"
                categorySlug="shoes"
                productName="Red Sneakers"
            />,
        );

        expect(screen.getByText("Shoes").closest("a")).toHaveAttribute(
            "href",
            "/category/shoes",
        );
    });
});
