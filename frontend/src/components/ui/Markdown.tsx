import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";

const components: Components = {
    h1: ({ children }) => (
        <h2 className="mt-6 mb-2 text-2xl font-semibold">{children}</h2>
    ),
    h2: ({ children }) => (
        <h2 className="mt-6 mb-2 text-2xl font-semibold">{children}</h2>
    ),
    h3: ({ children }) => (
        <h3 className="mt-5 mb-2 text-xl font-semibold">{children}</h3>
    ),
    h4: ({ children }) => (
        <h4 className="mt-4 mb-2 text-lg font-semibold">{children}</h4>
    ),
    p: ({ children }) => <p className="mb-3 leading-relaxed">{children}</p>,
    ul: ({ children }) => <ul className="mb-3 list-disc pl-6">{children}</ul>,
    ol: ({ children }) => (
        <ol className="mb-3 list-decimal pl-6">{children}</ol>
    ),
    li: ({ children }) => <li className="mb-1">{children}</li>,
    a: ({ href, children }) => (
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
        >
            {children}
        </a>
    ),
    blockquote: ({ children }) => (
        <blockquote className="mb-3 border-l-4 border-gray-300 pl-4 text-gray-600 italic">
            {children}
        </blockquote>
    ),
    pre: ({ children }) => (
        <pre className="mb-3 overflow-x-auto rounded-lg bg-gray-100 p-3 text-sm">
            {children}
        </pre>
    ),
    code: ({ children }) => (
        <code className="rounded bg-gray-100 px-1 text-sm">{children}</code>
    ),
    hr: () => <hr className="my-4 border-gray-200" />,
};

export function Markdown({ children }: { children: string }) {
    return (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
            {children}
        </ReactMarkdown>
    );
}
