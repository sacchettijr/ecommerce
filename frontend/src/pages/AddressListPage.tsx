import { useEffect, useRef, useState } from "react";

import { fetchUserAddresses, setPrimaryAddress } from "../api/addresses.ts";
import type { UserAddress } from "../api/types.ts";
import { AccountLayout } from "../components/account/AccountLayout.tsx";
import { Alert } from "../components/ui/Alert.tsx";
import { Tooltip } from "../components/ui/Tooltip.tsx";
import {
    PencilIcon,
    PlusIcon,
    TrashIcon,
} from "../components/ui/icons.tsx";
import { useAsync } from "../hooks/useAsync.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import type { Translations } from "../i18n/types.ts";

function hasValue(value: string | null | undefined): value is string {
    return typeof value === "string" && value.trim().length > 0;
}

interface AddressFieldProps {
    label: string;
    value: string | null | undefined;
}

function AddressField({ label, value }: AddressFieldProps) {
    if (!hasValue(value)) {
        return null;
    }

    return (
        <div className="grid grid-cols-1 gap-0.5 sm:grid-cols-3 sm:gap-4">
            <dt className="text-sm font-medium text-gray-500">{label}</dt>
            <dd className="text-sm text-gray-900 sm:col-span-2">{value}</dd>
        </div>
    );
}

const inertIconButtonClassName =
    "rounded p-1.5 text-gray-400 opacity-60 cursor-not-allowed";

interface AddressCardProps {
    address: UserAddress;
    pending: boolean;
    onSelectPrimary: () => void;
    t: Translations;
}

function AddressCard({ address, pending, onSelectPrimary, t }: AddressCardProps) {
    const radioId = `address-primary-${address.id}`;
    const summary = `${address.street}, ${address.number}`;

    return (
        <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-200">
            <div className="mb-4 flex items-start justify-between gap-4">
                <label
                    htmlFor={radioId}
                    className="flex items-center gap-2 text-sm font-medium text-gray-700"
                >
                    <input
                        id={radioId}
                        type="radio"
                        name="primary-address"
                        checked={address.primary}
                        disabled={pending}
                        onChange={onSelectPrimary}
                        aria-label={t.addressList.setPrimaryAccessibleLabel(
                            summary,
                        )}
                        className="size-4 text-blue-600 focus:ring-blue-200"
                    />
                    {t.addressList.setPrimaryLabel}
                    {address.primary && (
                        <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                            {t.addressList.primaryBadge}
                        </span>
                    )}
                    {pending && (
                        <span className="text-xs text-gray-400">
                            {t.common.loading}
                        </span>
                    )}
                </label>

                <div className="flex shrink-0 items-center gap-1">
                    <Tooltip text={t.addressList.editAddress}>
                        <button
                            type="button"
                            aria-disabled="true"
                            aria-label={t.addressList.editAddress}
                            className={inertIconButtonClassName}
                        >
                            <PencilIcon className="size-5" />
                        </button>
                    </Tooltip>
                    <Tooltip text={t.addressList.deleteAddress}>
                        <button
                            type="button"
                            aria-disabled="true"
                            aria-label={t.addressList.deleteAddress}
                            className={inertIconButtonClassName}
                        >
                            <TrashIcon className="size-5" />
                        </button>
                    </Tooltip>
                </div>
            </div>

            <dl className="space-y-1.5">
                <AddressField label={t.addressList.streetLabel} value={address.street} />
                <AddressField label={t.addressList.numberLabel} value={address.number} />
                <AddressField
                    label={t.addressList.complementLabel}
                    value={address.complement}
                />
                <AddressField
                    label={t.addressList.referenceLabel}
                    value={address.reference}
                />
                <AddressField
                    label={t.addressList.districtLabel}
                    value={address.district}
                />
                <AddressField
                    label={t.addressList.postalCodeLabel}
                    value={address.postal_code}
                />
                <AddressField label={t.addressList.cityLabel} value={address.city.name} />
                <AddressField
                    label={t.addressList.stateLabel}
                    value={address.state.name}
                />
                <AddressField
                    label={t.addressList.countryLabel}
                    value={address.country.name}
                />
            </dl>
        </div>
    );
}

export function AddressListPage() {
    const { t } = useLanguage();
    const { data, error, loading } = useAsync(fetchUserAddresses, undefined);
    // Authoritative state after a set-primary call — takes precedence over the initial fetch,
    // same pattern AuthProvider uses for the current user after login/logout.
    const [override, setOverride] = useState<UserAddress[] | null>(null);
    const [pendingId, setPendingId] = useState<number | null>(null);
    const requestTokenRef = useRef(0);
    const abortControllerRef = useRef<AbortController | null>(null);
    const { messages, beginAction, replaceMessages, dismissMessage } =
        useMessages();
    const actionRef = useRef(0);

    useEffect(() => {
        return () => abortControllerRef.current?.abort();
    }, []);

    const addresses = override ?? data ?? null;
    const addressesLoading = loading && override === null;

    const onSelectPrimary = async (address: UserAddress) => {
        if (address.primary || pendingId === address.id) {
            return;
        }

        abortControllerRef.current?.abort();
        const controller = new AbortController();
        abortControllerRef.current = controller;
        const token = (requestTokenRef.current += 1);
        actionRef.current = beginAction();
        setPendingId(address.id);

        try {
            const updated = await setPrimaryAddress(address.id, controller.signal);

            if (token !== requestTokenRef.current) {
                return;
            }
            setOverride(updated);
            setPendingId(null);
            replaceMessages(actionRef.current, [
                { variant: "success", text: t.addressList.primaryUpdated },
            ]);
        } catch (err) {
            if (token !== requestTokenRef.current) {
                return;
            }
            setPendingId(null);

            if (err instanceof DOMException && err.name === "AbortError") {
                return;
            }

            // Reconcile with the backend's authoritative state rather than trusting whatever
            // was on screen before this failed attempt.
            try {
                const fresh = await fetchUserAddresses(undefined, controller.signal);
                if (token === requestTokenRef.current) {
                    setOverride(fresh);
                }
            } catch {
                // Keep whatever was already displayed; the error below still gets shown.
            }

            replaceMessages(actionRef.current, [
                { variant: "error", text: t.addressList.updateError },
            ]);
        }
    };

    return (
        <AccountLayout
            title={t.addressList.title}
            messages={messages}
            onDismissMessage={dismissMessage}
        >
            <div className="mb-6 flex items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-gray-900">
                    {t.addressList.heading}
                </h1>
                <Tooltip text={t.addressList.addAddress}>
                    <button
                        type="button"
                        aria-disabled="true"
                        aria-label={t.addressList.addAddress}
                        className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-gray-400 opacity-60 cursor-not-allowed ring-1 ring-gray-200"
                    >
                        <PlusIcon className="size-4" />
                        {t.addressList.addAddress}
                    </button>
                </Tooltip>
            </div>

            {addressesLoading && <p>{t.common.loading}</p>}

            {!addressesLoading && error !== undefined && (
                <Alert variant="error">{t.addressList.loadError}</Alert>
            )}

            {!addressesLoading && error === undefined && addresses !== null && (
                <>
                    {addresses.length === 0 ? (
                        <p className="text-gray-600">{t.addressList.emptyState}</p>
                    ) : (
                        <fieldset className="space-y-4">
                            <legend className="sr-only">
                                {t.addressList.radioGroupLabel}
                            </legend>
                            {addresses.map((address) => (
                                <AddressCard
                                    key={address.id}
                                    address={address}
                                    pending={pendingId === address.id}
                                    onSelectPrimary={() =>
                                        void onSelectPrimary(address)
                                    }
                                    t={t}
                                />
                            ))}
                        </fieldset>
                    )}
                </>
            )}
        </AccountLayout>
    );
}
