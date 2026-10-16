import { describe, expect, it } from "vitest";

import { formatPrice } from "./formatPrice.ts";

describe("formatPrice", () => {
    it("formats a value with cents using thousands and decimal separators", () => {
        expect(formatPrice(1234.56)).toBe("$1,234.56");
    });

    it("formats a large integer value with multiple thousands separators", () => {
        expect(formatPrice(1000000)).toBe("$1,000,000.00");
    });

    it("formats a value without needing a thousands separator", () => {
        expect(formatPrice(99.99)).toBe("$99.99");
    });

    it("formats zero", () => {
        expect(formatPrice(0)).toBe("$0.00");
    });

    it("adds a thousands separator right at the 1,000 boundary", () => {
        expect(formatPrice(999.99)).toBe("$999.99");
        expect(formatPrice(1000)).toBe("$1,000.00");
    });
});
