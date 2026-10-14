import type { SessionUser } from "../api/types.ts";

export function makeSessionUser(overrides: Partial<SessionUser> = {}): SessionUser {
    return {
        id: 1,
        name: "Jane Doe",
        email: "jane@example.com",
        date_birth: "1990-05-20",
        phone: "",
        created_at: "2026-01-10T12:00:00-04:00",
        is_staff: false,
        ...overrides,
    };
}
