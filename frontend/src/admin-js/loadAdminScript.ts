import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { JSDOM } from "jsdom";

// Loads and executes one of the project's real Django Admin static JS files
// (static/src/js/admin/*.js, served by Django, no build step of its own) inside
// an isolated jsdom window built to match the markup Django actually renders.
// This exercises the exact shipped source via fs.readFileSync, not a
// reimplementation of its logic.
//
// runScripts: "dangerously" is required for window.eval'd code to see `document`
// as a bare global (matching how a real <script> tag behaves) - safe here since
// the "script" is this project's own trusted source file, not page content.
export async function loadAdminScript(scriptName: string, html: string): Promise<JSDOM> {
    const dom = new JSDOM(html, {
        url: "http://localhost/admin/",
        runScripts: "dangerously",
    });
    //   /repo-static is a read-only bind mount of the repo root's static/ directory
    //   (see docker-compose.yml's frontend service) - that's where Django actually
    //   serves these files from; this container only otherwise has frontend/ itself.
    const source = readFileSync(
        resolve("/repo-static/src/js/admin", scriptName),
        "utf-8",
    );

    dom.window.eval(source);

    // The scripts register their real logic inside a DOMContentLoaded listener,
    // which jsdom dispatches asynchronously - wait for it so callers can rely on
    // the listeners being attached before firing any change/formset events.
    if (dom.window.document.readyState === "loading") {
        await new Promise<void>((resolveReady) => {
            dom.window.document.addEventListener("DOMContentLoaded", () => resolveReady());
        });
    }

    return dom;
}

export function fireChange(dom: JSDOM, element: Element): void {
    element.dispatchEvent(new dom.window.Event("change", { bubbles: true }));
}

export function fireFormsetAdded(dom: JSDOM, row: Element, formsetName: string): void {
    row.dispatchEvent(
        new dom.window.CustomEvent("formset:added", {
            bubbles: true,
            detail: { formsetName },
        }),
    );
}
