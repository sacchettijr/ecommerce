import { afterEach, describe, expect, it, vi } from "vitest";

import { fireChange, loadAdminScript } from "./loadAdminScript.ts";

// Mirrors the real rendered <select> markup: country has no data attributes of
// its own; state options carry data-country (StateLocationSelect); city options
// carry data-state/data-country (CityLocationSelect). Matches the standalone
// UserAddressAdmin form's plain (unprefixed) field names - the regex-based field
// lookup in the script also supports a "{prefix}-{n}-{field}" inline name, not
// exercised directly here since the selector logic is identical either way.
const HTML = `<!doctype html>
<html><body>
<select name="country">
    <option value="">---------</option>
    <option value="1">Brazil</option>
    <option value="2">United States</option>
</select>
<select name="state">
    <option value="">---------</option>
    <option value="10" data-country="1">Sao Paulo</option>
    <option value="11" data-country="1">Rio de Janeiro</option>
    <option value="12" data-country="2">California</option>
</select>
<select name="city">
    <option value="">---------</option>
    <option value="100" data-state="10" data-country="1">Sao Paulo City</option>
    <option value="101" data-state="12" data-country="2">Los Angeles</option>
</select>
</body></html>`;

function select(dom: Awaited<ReturnType<typeof loadAdminScript>>, name: string) {
    const element = dom.window.document.querySelector(`[name="${name}"]`);
    if (!(element instanceof dom.window.HTMLSelectElement)) {
        throw new Error(`select "${name}" not found`);
    }
    return element;
}

describe("city_location_select.js", () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("populates the country when a state is picked directly", async () => {
        const dom = await loadAdminScript("city_location_select.js", HTML);
        dom.window.fetch = vi.fn().mockResolvedValue({
            json: () => Promise.resolve([]),
        }) as typeof fetch;

        select(dom, "state").value = "11"; // Rio de Janeiro, country 1
        fireChange(dom, select(dom, "state"));

        expect(select(dom, "country").value).toBe("1");
    });

    it("still syncs city -> state/country after a state-first selection (regression guard)", async () => {
        const dom = await loadAdminScript("city_location_select.js", HTML);
        dom.window.fetch = vi.fn().mockResolvedValue({
            json: () =>
                Promise.resolve([
                    { id: 100, name: "Sao Paulo City", state: 10, country: 1 },
                ]),
        }) as typeof fetch;

        select(dom, "state").value = "10";
        fireChange(dom, select(dom, "state"));
        await vi.waitFor(() => {
            expect(select(dom, "city").querySelector('option[value="100"]')).not.toBeNull();
        });

        // The city list was rebuilt by the state-change handler - its options must
        // still carry data-state/data-country so picking one still syncs correctly.
        select(dom, "city").value = "100";
        fireChange(dom, select(dom, "city"));

        expect(select(dom, "state").value).toBe("10");
        expect(select(dom, "country").value).toBe("1");
    });

    it("populates state and country when a city is picked directly", async () => {
        const dom = await loadAdminScript("city_location_select.js", HTML);

        select(dom, "city").value = "101"; // Los Angeles
        fireChange(dom, select(dom, "city"));

        expect(select(dom, "state").value).toBe("12");
        expect(select(dom, "country").value).toBe("2");
    });

    it("clears state and city when the country changes to one they don't belong to", async () => {
        const dom = await loadAdminScript("city_location_select.js", HTML);
        select(dom, "state").value = "10";
        select(dom, "city").value = "100";
        dom.window.fetch = vi.fn().mockImplementation((url: string) => {
            if (url.includes("/states/")) {
                return Promise.resolve({
                    json: () => Promise.resolve([{ id: 12, name: "California", country: 2 }]),
                });
            }
            return Promise.resolve({ json: () => Promise.resolve([]) });
        }) as typeof fetch;

        select(dom, "country").value = "2";
        fireChange(dom, select(dom, "country"));

        await vi.waitFor(() => {
            expect(select(dom, "state").value).toBe("");
        });
        expect(select(dom, "city").value).toBe("");
    });

    it("does not let a stale response overwrite a newer selection", async () => {
        const dom = await loadAdminScript("city_location_select.js", HTML);
        let resolveFirst: (value: unknown) => void = () => {};
        const firstResponse = new Promise((resolve) => {
            resolveFirst = resolve;
        });

        dom.window.fetch = vi
            .fn()
            .mockImplementationOnce(() => firstResponse.then(() => ({
                json: () => Promise.resolve([{ id: 999, name: "Stale State", country: 1 }]),
            })))
            .mockImplementationOnce(() =>
                Promise.resolve({
                    json: () => Promise.resolve([{ id: 12, name: "California", country: 2 }]),
                }),
            ) as typeof fetch;

        select(dom, "country").value = "1";
        fireChange(dom, select(dom, "country")); // slow first request, started but not resolved yet

        select(dom, "country").value = "2";
        fireChange(dom, select(dom, "country")); // second request, resolves first

        await vi.waitFor(() => {
            expect(select(dom, "state").querySelector('option[value="12"]')).not.toBeNull();
        });

        resolveFirst(undefined); // now let the stale first request resolve
        await new Promise((r) => setTimeout(r, 10));

        // The stale "Stale State" option must never have been applied.
        expect(select(dom, "state").querySelector('option[value="999"]')).toBeNull();
    });

    it("does not fire any sync on load for an address's pre-populated values", async () => {
        const prepopulated = HTML.replace(
            'value="11" data-country="1"',
            'value="11" data-country="1" selected',
        ).replace('value="100" data-state="10"', 'value="100" data-state="10" selected');
        const dom = await loadAdminScript("city_location_select.js", prepopulated);

        // No change event fired - values must remain exactly as server-rendered.
        expect(select(dom, "state").value).toBe("11");
        expect(select(dom, "city").value).toBe("100");
    });
});
