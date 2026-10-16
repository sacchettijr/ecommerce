import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { fetchProducts } from "../api/products.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { ProductListPage } from "./ProductListPage.tsx";

vi.mock("../api/products.ts", () => ({
    fetchProducts: vi.fn(),
}));

const mockedFetchProducts = vi.mocked(fetchProducts);

function emptyPage() {
    return Promise.resolve({
        count: 0,
        total_pages: 1,
        current_page: 1,
        next: null,
        previous: null,
        results: [],
    });
}

describe("ProductListPage ordering", () => {
    beforeEach(() => {
        mockedFetchProducts.mockReset();
        mockedFetchProducts.mockImplementation(emptyPage);
    });

    it("sends no ordering param by default (lets the backend's randomized order apply)", () => {
        renderWithProviders(<ProductListPage />, { route: "/products" });

        const [query] = mockedFetchProducts.mock.calls[0] ?? [];
        expect(query).not.toContain("ordering=");
    });

    it("sends an explicit ordering param once the user picks a sort option", async () => {
        const user = userEvent.setup();
        renderWithProviders(<ProductListPage />, { route: "/products" });

        await user.selectOptions(
            screen.getByLabelText("Sort by"),
            "Most recent",
        );

        const lastCall = mockedFetchProducts.mock.calls.at(-1) ?? [];
        expect(lastCall[0]).toContain("ordering=-created_at");
    });
});
