(() => {
    "use strict";

    const arabicDigits = "٠١٢٣٤٥٦٧٨٩";
    const persianDigits = "۰۱۲۳۴۵۶۷۸۹";

    function toAsciiDigits(value) {
        return value
            .replace(/[٠-٩]/g, (digit) => String(arabicDigits.indexOf(digit)))
            .replace(/[۰-۹]/g, (digit) => String(persianDigits.indexOf(digit)));
    }

    function cleanMobileInput(event) {
        const field = event.currentTarget;
        const asciiValue = toAsciiDigits(field.value);
        const hasLeadingPlus = asciiValue.trimStart().startsWith("+");
        const digits = asciiValue.replace(/\D/g, "").slice(0, hasLeadingPlus ? 12 : 13);
        field.value = hasLeadingPlus ? `+${digits}` : digits;
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-saudi-mobile]").forEach((field) => {
            field.addEventListener("input", cleanMobileInput);
        });
    });
})();
