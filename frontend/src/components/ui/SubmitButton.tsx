interface SubmitButtonProps {
    submitting: boolean;
    label: string;
    submittingLabel: string;
}

export function SubmitButton({
    submitting,
    label,
    submittingLabel,
}: SubmitButtonProps) {
    return (
        <button
            type="submit"
            disabled={submitting}
            aria-busy={submitting}
            className="w-full rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
            {submitting ? submittingLabel : label}
        </button>
    );
}
