import { apiGet, apiPost } from "./client.ts";
import type { SessionUser } from "./types.ts";

interface UserResponse {
    user: SessionUser;
}

export interface SignupPayload {
    name: string;
    email: string;
    date_birth: string;
    phone: string;
    password1: string;
    password2: string;
}

export async function fetchSession(
    signal?: AbortSignal,
): Promise<SessionUser | null> {
    const data = await apiGet<{ user: SessionUser | null }>(
        "/account/session/",
        signal,
    );

    return data.user;
}

export async function login(
    email: string,
    password: string,
): Promise<SessionUser> {
    const data = await apiPost<UserResponse>("/account/login/", {
        email,
        password,
    });

    return data.user;
}

export function logout(): Promise<void> {
    return apiPost<void>("/account/logout/", {});
}

export function signup(payload: SignupPayload, next: string): Promise<void> {
    return apiPost<void>("/account/signup/", { ...payload, next });
}

export function resendVerificationEmail(
    email: string,
    next: string,
): Promise<void> {
    return apiPost<void>("/account/email-verification/resend/", {
        email,
        next,
    });
}

// A confirmação e a troca de senha (token, expiração, regras) ficam no Django;
// o React só repassa o que veio no link do e-mail.
export function confirmEmail(uid: string, token: string): Promise<void> {
    return apiPost<void>("/account/email-verification/confirm/", {
        uid,
        token,
    });
}

export function requestPasswordReset(
    email: string,
    next: string,
): Promise<void> {
    return apiPost<void>("/account/password-reset/", { email, next });
}

export function validatePasswordResetLink(
    uid: string,
    token: string,
    signal?: AbortSignal,
): Promise<void> {
    return apiPost<void>(
        "/account/password-reset/validate/",
        { uid, token },
        signal,
    );
}

export function confirmPasswordReset(
    uid: string,
    token: string,
    newPassword1: string,
    newPassword2: string,
): Promise<void> {
    return apiPost<void>("/account/password-reset/confirm/", {
        uid,
        token,
        new_password1: newPassword1,
        new_password2: newPassword2,
    });
}

// Always operates on the authenticated session's own user — the backend never accepts a
// user identifier here, so this can never target another account.
export function changePassword(
    oldPassword: string,
    newPassword1: string,
    newPassword2: string,
): Promise<void> {
    return apiPost<void>("/account/password-change/", {
        old_password: oldPassword,
        new_password1: newPassword1,
        new_password2: newPassword2,
    });
}

export interface ProfileUpdatePayload {
    name: string;
    date_birth: string;
    phone: string;
}

// Same session/no-user-id rule as changePassword above. Returns the fresh SessionUser so the
// caller can refresh AuthContext directly from the response, without a second request.
export async function updateProfile(
    payload: ProfileUpdatePayload,
): Promise<SessionUser> {
    const data = await apiPost<UserResponse>("/account/profile/", payload);

    return data.user;
}
