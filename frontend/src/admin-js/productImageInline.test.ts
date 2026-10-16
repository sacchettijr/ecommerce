import { describe, expect, it } from "vitest";

import { fireChange, fireFormsetAdded, loadAdminScript } from "./loadAdminScript.ts";

// Mirrors the real inline markup: existing rows get class "form-row has_original"
// (no "dynamic-images" - that class is only added by Django's own inlines.js to
// rows cloned via "Add another"), each with is_primary/order/DELETE inputs.
function existingRow(index: number, order: number, deleted = false): string {
    return `<tr class="form-row has_original">
        <td class="field-is_primary">
            <input type="checkbox" name="images-${index}-is_primary">
        </td>
        <td class="field-order">
            <input type="number" name="images-${index}-order" value="${order}">
        </td>
        <td class="delete">
            <input type="checkbox" name="images-${index}-DELETE" ${deleted ? "checked" : ""}>
        </td>
    </tr>`;
}

function html(existingRows: string[]): string {
    return `<!doctype html>
<html><body>
<div id="images-group">
    <table><tbody>${existingRows.join("\n")}</tbody></table>
</div>
</body></html>`;
}

function orderInput(dom: Awaited<ReturnType<typeof loadAdminScript>>, index: number) {
    const element = dom.window.document.querySelector(`[name="images-${index}-order"]`);
    if (!(element instanceof dom.window.HTMLInputElement)) {
        throw new Error(`order input ${index} not found`);
    }
    return element;
}

function primaryCheckbox(dom: Awaited<ReturnType<typeof loadAdminScript>>, index: number) {
    const element = dom.window.document.querySelector(`[name="images-${index}-is_primary"]`);
    if (!(element instanceof dom.window.HTMLInputElement)) {
        throw new Error(`is_primary checkbox ${index} not found`);
    }
    return element;
}

// Simulates Django's "Add another" cloning a new row: same markup shape as an
// existing row, but class "dynamic-images" instead of "has_original", and no
// DELETE checkbox (new, unsaved rows use a remove link instead).
function addNewRow(dom: Awaited<ReturnType<typeof loadAdminScript>>, index: number): Element {
    const tbody = dom.window.document.querySelector("#images-group tbody");
    if (!tbody) {
        throw new Error("tbody not found");
    }
    const row = dom.window.document.createElement("tr");
    row.className = "form-row dynamic-images";
    row.innerHTML = `
        <td class="field-is_primary">
            <input type="checkbox" name="images-${index}-is_primary">
        </td>
        <td class="field-order">
            <input type="number" name="images-${index}-order" value="0">
        </td>`;
    tbody.appendChild(row);
    fireFormsetAdded(dom, row, "images");
    return row;
}

describe("product_image_inline.js", () => {
    it("pre-fills a new row's order with max(existing)+1, excluding an existing row marked for deletion", async () => {
        // Regression test for the actual reported bug: a pre-existing row (order 5)
        // is marked deleted; the real bug was that ".dynamic-images" never matched an
        // existing row, so its DELETE checkbox was never found and its stale order
        // still counted toward the max.
        const dom = await loadAdminScript(
            "product_image_inline.js",
            html([
                existingRow(0, 0),
                existingRow(1, 1),
                existingRow(2, 5, /* deleted */ true),
            ]),
        );

        addNewRow(dom, 3);

        expect(orderInput(dom, 3).value).toBe("2");
    });

    it("gives consistent, incrementing values to multiple new rows added in one session", async () => {
        const dom = await loadAdminScript(
            "product_image_inline.js",
            html([existingRow(0, 0), existingRow(1, 1)]),
        );

        addNewRow(dom, 2);
        addNewRow(dom, 3);

        expect(orderInput(dom, 2).value).toBe("2");
        expect(orderInput(dom, 3).value).toBe("3");
    });

    it("computes the position correctly after deleting then adding in the same session", async () => {
        const dom = await loadAdminScript(
            "product_image_inline.js",
            html([existingRow(0, 0), existingRow(1, 1), existingRow(2, 2)]),
        );

        // Mark the last existing row (order 2) for deletion before adding a new one.
        const deleteCheckbox = dom.window.document.querySelector(
            '[name="images-2-DELETE"]',
        );
        if (!(deleteCheckbox instanceof dom.window.HTMLInputElement)) {
            throw new Error("delete checkbox not found");
        }
        deleteCheckbox.checked = true;

        addNewRow(dom, 3);

        // Rows 0 and 1 (orders 0, 1) remain; row 2 (order 2) was deleted, so the
        // next position is max(0, 1) + 1 = 2, not 3.
        expect(orderInput(dom, 3).value).toBe("2");
    });

    it("re-confirms is_primary exclusivity under jsdom", async () => {
        const dom = await loadAdminScript(
            "product_image_inline.js",
            html([existingRow(0, 0), existingRow(1, 1)]),
        );

        primaryCheckbox(dom, 0).checked = true;
        fireChange(dom, primaryCheckbox(dom, 0));
        primaryCheckbox(dom, 1).checked = true;
        fireChange(dom, primaryCheckbox(dom, 1));

        expect(primaryCheckbox(dom, 0).checked).toBe(false);
        expect(primaryCheckbox(dom, 1).checked).toBe(true);
    });
});
