document.addEventListener("DOMContentLoaded", function () {
    var ckeditor = window.CKEDITOR;

    if (!ckeditor) {
        return;
    }

    var language = (document.documentElement.lang || "en").toLowerCase();
    var hasTranslation = Boolean(
        window.CKEDITOR_TRANSLATIONS && window.CKEDITOR_TRANSLATIONS[language],
    );
    var paragraphTitles = {
        "pt-br": "Parágrafo",
        es: "Párrafo",
    };

    var plugins = [
        ckeditor.Essentials,
        ckeditor.Paragraph,
        ckeditor.Heading,
        ckeditor.Bold,
        ckeditor.Italic,
        ckeditor.Strikethrough,
        ckeditor.Link,
        ckeditor.AutoLink,
        ckeditor.List,
        ckeditor.BlockQuote,
        ckeditor.Code,
        ckeditor.CodeBlock,
        ckeditor.HorizontalLine,
        ckeditor.Autoformat,
        ckeditor.SourceEditing,
        ckeditor.Undo,
        ckeditor.Markdown,
    ];

    var toolbar = [
        "heading",
        "|",
        "bold",
        "italic",
        "strikethrough",
        "link",
        "|",
        "bulletedList",
        "numberedList",
        "|",
        "blockQuote",
        "code",
        "codeBlock",
        "horizontalLine",
        "|",
        "sourceEditing",
        "|",
        "undo",
        "redo",
    ];

    document
        .querySelectorAll("textarea.markdown-editor")
        .forEach(function (textarea) {
            if (textarea.name.indexOf("__prefix__") !== -1) {
                return;
            }

            ckeditor.ClassicEditor.create(textarea, {
                licenseKey: "GPL",
                language: hasTranslation ? language : "en",
                plugins: plugins,
                toolbar: toolbar,
                heading: {
                    options: [
                        {
                            model: "paragraph",
                            title: paragraphTitles[language] || "Paragraph",
                            class: "ck-heading_paragraph",
                        },
                        {
                            model: "heading2",
                            view: "h2",
                            title: "H2",
                            class: "ck-heading_heading2",
                        },
                        {
                            model: "heading3",
                            view: "h3",
                            title: "H3",
                            class: "ck-heading_heading3",
                        },
                        {
                            model: "heading4",
                            view: "h4",
                            title: "H4",
                            class: "ck-heading_heading4",
                        },
                    ],
                },
            }).catch(function (error) {
                console.error("CKEditor 5:", error);
            });
        });
});
