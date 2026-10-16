import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { detectInitialLanguage } from "./detectInitialLanguage.ts";

describe("detectInitialLanguage", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("falls back to English when there is no stored preference and the browser language is unsupported", () => {
        vi.spyOn(navigator, "language", "get").mockReturnValue("de-DE");

        expect(detectInitialLanguage()).toBe("en");
    });

    it("prefers a stored preference over the browser language", () => {
        localStorage.setItem("language", "es");
        vi.spyOn(navigator, "language", "get").mockReturnValue("pt-BR");

        expect(detectInitialLanguage()).toBe("es");
    });

    it("matches a supported browser language when there is no stored preference", () => {
        vi.spyOn(navigator, "language", "get").mockReturnValue("fr-FR");

        expect(detectInitialLanguage()).toBe("fr");
    });
});
