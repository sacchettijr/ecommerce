import { apiPost } from "./client.ts";
import type { ContactPayload } from "./types.ts";

export function sendContact(payload: ContactPayload): Promise<unknown> {
    return apiPost<unknown>("/core/contact/", payload);
}
