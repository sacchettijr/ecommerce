import { describe, expect, it } from "vitest";

import { sanitizePhoneInput } from "./sanitizePhoneInput.ts";

describe("sanitizePhoneInput", () => {
    it("removes letters while keeping digits and symbols", () => {
        expect(sanitizePhoneInput("(11a) 9b8765-c4321")).toBe(
            "(11) 98765-4321",
        );
    });

    it("removes accented letters too", () => {
        expect(sanitizePhoneInput("11987é65ção4321")).toBe("11987654321");
    });

    it("leaves a value with no letters untouched", () => {
        expect(sanitizePhoneInput("+55 (11) 98765-4321")).toBe(
            "+55 (11) 98765-4321",
        );
    });

    it("returns an empty string unchanged", () => {
        expect(sanitizePhoneInput("")).toBe("");
    });
});
