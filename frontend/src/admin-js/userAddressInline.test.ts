import { describe, expect, it } from "vitest";

import { fireChange, loadAdminScript } from "./loadAdminScript.ts";

// Mirrors the real inline markup: three rows inside #user_addresses-group, each
// with a "primary" checkbox named per Django's formset convention
// (user_addresses-{index}-primary), plus a DELETE checkbox on existing rows.
function html(rows: number): string {
    const trs = Array.from({ length: rows }, (_, index) => {
        const deleteCell =
            index < rows
                ? `<input type="checkbox" name="user_addresses-${index}-DELETE">`
                : "";
        return `<tr class="form-row has_original">
            <td class="field-primary">
                <input type="checkbox" name="user_addresses-${index}-primary">
            </td>
            <td class="delete">${deleteCell}</td>
        </tr>`;
    }).join("\n");

    return `<!doctype html>
<html><body>
<div id="user_addresses-group">
    <table><tbody>${trs}</tbody></table>
</div>
</body></html>`;
}

function checkbox(dom: Awaited<ReturnType<typeof loadAdminScript>>, index: number) {
    const element = dom.window.document.querySelector(
        `[name="user_addresses-${index}-primary"]`,
    );
    if (!(element instanceof dom.window.HTMLInputElement)) {
        throw new Error(`primary checkbox ${index} not found`);
    }
    return element;
}

describe("user_address_inline.js", () => {
    it("checking one primary checkbox unchecks every other one in the group", async () => {
        const dom = await loadAdminScript("user_address_inline.js", html(3));

        checkbox(dom, 0).checked = true;
        fireChange(dom, checkbox(dom, 0));

        expect(checkbox(dom, 0).checked).toBe(true);
        expect(checkbox(dom, 1).checked).toBe(false);
        expect(checkbox(dom, 2).checked).toBe(false);
    });

    it("keeps only the most recently checked one after switching selection several times", async () => {
        const dom = await loadAdminScript("user_address_inline.js", html(3));

        checkbox(dom, 0).checked = true;
        fireChange(dom, checkbox(dom, 0));
        checkbox(dom, 1).checked = true;
        fireChange(dom, checkbox(dom, 1));
        checkbox(dom, 2).checked = true;
        fireChange(dom, checkbox(dom, 2));

        expect(checkbox(dom, 0).checked).toBe(false);
        expect(checkbox(dom, 1).checked).toBe(false);
        expect(checkbox(dom, 2).checked).toBe(true);
    });

    it("unchecking a checkbox does not affect the others", async () => {
        const dom = await loadAdminScript("user_address_inline.js", html(2));

        checkbox(dom, 0).checked = true;
        fireChange(dom, checkbox(dom, 0));
        checkbox(dom, 0).checked = false;
        fireChange(dom, checkbox(dom, 0));

        expect(checkbox(dom, 0).checked).toBe(false);
        expect(checkbox(dom, 1).checked).toBe(false);
    });

    it("does nothing (no error) when the group isn't on the page", async () => {
        const dom = await loadAdminScript(
            "user_address_inline.js",
            "<!doctype html><html><body></body></html>",
        );

        expect(dom.window.document.getElementById("user_addresses-group")).toBeNull();
    });
});
