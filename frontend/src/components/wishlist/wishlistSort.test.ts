import { describe, expect, it } from "vitest";

import { isWishlistSort, sortWishlistItems } from "./wishlistSort.ts";

interface Item {
    id: number;
    added_at: string;
    product: { name: string; price: string };
}

function item(id: number, name: string, price: string, added_at: string): Item {
    return { id, added_at, product: { name, price } };
}

const items: Item[] = [
    item(1, "Banana Stand", "15.00", "2026-01-02T00:00:00Z"),
    item(2, "Apple Watch", "250.00", "2026-01-03T00:00:00Z"),
    item(3, "Cherry Pie", "8.00", "2026-01-01T00:00:00Z"),
];

describe("isWishlistSort", () => {
    it("accepts every documented sort value", () => {
        for (const value of [
            "priority",
            "name",
            "-name",
            "price",
            "-price",
            "added_at",
            "-added_at",
        ]) {
            expect(isWishlistSort(value)).toBe(true);
        }
    });

    it("rejects an arbitrary string", () => {
        expect(isWishlistSort("relevance")).toBe(false);
    });
});

describe("sortWishlistItems", () => {
    it("leaves the array untouched (same order, same reference) for 'priority'", () => {
        const result = sortWishlistItems(items, "priority");

        expect(result).toBe(items);
        expect(result.map((i) => i.id)).toEqual([1, 2, 3]);
    });

    it("sorts alphabetically ascending by product name", () => {
        const result = sortWishlistItems(items, "name");

        expect(result.map((i) => i.product.name)).toEqual([
            "Apple Watch",
            "Banana Stand",
            "Cherry Pie",
        ]);
    });

    it("sorts alphabetically descending by product name", () => {
        const result = sortWishlistItems(items, "-name");

        expect(result.map((i) => i.product.name)).toEqual([
            "Cherry Pie",
            "Banana Stand",
            "Apple Watch",
        ]);
    });

    it("sorts by price ascending", () => {
        const result = sortWishlistItems(items, "price");

        expect(result.map((i) => i.id)).toEqual([3, 1, 2]);
    });

    it("sorts by price descending", () => {
        const result = sortWishlistItems(items, "-price");

        expect(result.map((i) => i.id)).toEqual([2, 1, 3]);
    });

    it("sorts by date added, oldest first", () => {
        const result = sortWishlistItems(items, "added_at");

        expect(result.map((i) => i.id)).toEqual([3, 1, 2]);
    });

    it("sorts by date added, newest first", () => {
        const result = sortWishlistItems(items, "-added_at");

        expect(result.map((i) => i.id)).toEqual([2, 1, 3]);
    });

    it("does not mutate the original array", () => {
        const original = [...items];
        sortWishlistItems(items, "-price");

        expect(items).toEqual(original);
    });
});
