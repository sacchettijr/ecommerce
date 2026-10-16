import { describe, expect, it } from "vitest";

import {
    DEFAULT_PRODUCT_SORT,
    getProductSort,
    isProductSort,
} from "./productSort.ts";

describe("productSort", () => {
    it("defaults to featured", () => {
        expect(DEFAULT_PRODUCT_SORT).toBe("featured");
    });

    it("falls back to featured when no ordering param is present", () => {
        expect(getProductSort(new URLSearchParams())).toBe("featured");
    });

    it("falls back to featured when the ordering param is invalid", () => {
        expect(
            getProductSort(new URLSearchParams("ordering=not-a-real-field")),
        ).toBe("featured");
    });

    it("returns an explicit, valid ordering param as-is", () => {
        expect(getProductSort(new URLSearchParams("ordering=price"))).toBe(
            "price",
        );
    });

    it("recognizes featured as a valid sort value", () => {
        expect(isProductSort("featured")).toBe(true);
    });
});
