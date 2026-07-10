(function () {
    "use strict";

    function bookHtml() {
        const book = document.getElementById("lettersWorksheetsBook");
        if (!book) return "";
        const styles = Array.from(document.querySelectorAll("style, link[rel='stylesheet']"))
            .map((node) => node.outerHTML)
            .join("\n");
        return `<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">${styles}</head><body>${book.outerHTML}</body></html>`;
    }

    function downloadWord() {
        const html = bookHtml();
        if (!html) return;
        const blob = new Blob(["\ufeff", html], { type: "application/msword;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "english_letters_worksheets_book.doc";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    function downloadPdf() {
        const book = document.getElementById("lettersWorksheetsBook");
        const button = document.getElementById("downloadLettersBookPdf");
        if (!book) return;

        if (typeof window.html2pdf !== "function") {
            window.print();
            return;
        }

        const originalText = button ? button.textContent : "";
        if (button) {
            button.disabled = true;
            button.textContent = "جاري تجهيز PDF...";
        }

        const restoreButton = () => {
            if (button) {
                button.disabled = false;
                button.textContent = originalText || "تحميل PDF";
            }
        };

        window.html2pdf()
            .set({
                margin: 8,
                filename: "english_letters_worksheets_book.pdf",
                image: { type: "jpeg", quality: 0.98 },
                html2canvas: { scale: 2, backgroundColor: "#ffffff", useCORS: true },
                jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
                pagebreak: { mode: ["css", "legacy"] },
            })
            .from(book)
            .save()
            .then(restoreButton)
            .catch(() => {
                restoreButton();
                window.print();
            });
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.getElementById("printLettersBook")?.addEventListener("click", () => window.print());
        document.getElementById("downloadLettersBookPdf")?.addEventListener("click", downloadPdf);
        document.getElementById("downloadLettersBookWord")?.addEventListener("click", downloadWord);
    });
})();
