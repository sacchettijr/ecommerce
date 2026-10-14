import { AccountLayout } from "../components/account/AccountLayout.tsx";
import { Alert } from "../components/ui/Alert.tsx";
import { ShieldCheckIcon } from "../components/ui/icons.tsx";
import { useAuth } from "../context/useAuth.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

interface ProfileFieldProps {
    label: string;
    value: string;
}

function ProfileField({ label, value }: ProfileFieldProps) {
    return (
        <div className="grid grid-cols-1 gap-1 py-3 sm:grid-cols-3 sm:gap-4">
            <dt className="text-sm font-medium text-gray-500">{label}</dt>
            <dd className="text-sm text-gray-900 sm:col-span-2">{value}</dd>
        </div>
    );
}

// Interpreta "YYYY-MM-DD" como data local (não UTC) para evitar que
// new Date(string) volte um dia em fusos com offset negativo.
function parseDateBirth(value: string): Date {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
}

export function ProfilePage() {
    const { user, loading } = useAuth();
    const { t, language } = useLanguage();
    const { messages, dismissMessage } = useMessages();

    if (loading) {
        return (
            <AccountLayout title={t.profile.title}>
                <p>{t.common.loading}</p>
            </AccountLayout>
        );
    }

    if (!user) {
        return (
            <AccountLayout title={t.profile.title}>
                <Alert variant="error">{t.profile.loadError}</Alert>
            </AccountLayout>
        );
    }

    return (
        <AccountLayout
            title={t.profile.title}
            messages={messages}
            onDismissMessage={dismissMessage}
        >
            <div className="mb-6 flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                    {t.profile.heading}
                </h1>
                {user.is_staff && (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-800 ring-1 ring-blue-300">
                        <ShieldCheckIcon className="size-4" />
                        {t.profile.staffBadge}
                    </span>
                )}
            </div>

            <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <dl className="divide-y divide-gray-100">
                    <ProfileField label={t.profile.nameLabel} value={user.name} />
                    <ProfileField
                        label={t.profile.emailLabel}
                        value={user.email}
                    />
                    <ProfileField
                        label={t.profile.dateBirthLabel}
                        value={parseDateBirth(
                            user.date_birth,
                        ).toLocaleDateString(language)}
                    />
                    <ProfileField
                        label={t.profile.phoneLabel}
                        value={user.phone || t.profile.notProvided}
                    />
                    {user.created_at && (
                        <ProfileField
                            label={t.profile.memberSinceLabel}
                            value={new Date(
                                user.created_at,
                            ).toLocaleDateString(language)}
                        />
                    )}
                </dl>
            </div>
        </AccountLayout>
    );
}
