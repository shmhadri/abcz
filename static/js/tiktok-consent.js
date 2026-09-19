(() => {
    "use strict";

    const consentKey = "smartlearning_analytics_marketing_consent_v1";
    const banner = document.getElementById("tiktok-consent-banner");
    const settingsButton = document.getElementById("analytics-marketing-consent-settings");
    const acceptButton = banner?.querySelector("[data-analytics-marketing-accept]");
    const rejectButton = banner?.querySelector("[data-analytics-marketing-reject]");
    if (!banner || !settingsButton || !acceptButton || !rejectButton) return;

    function readChoice() {
        try {
            return window.localStorage.getItem(consentKey);
        } catch (error) {
            return null;
        }
    }

    function saveChoice(choice) {
        try {
            window.localStorage.setItem(consentKey, choice);
            return true;
        } catch (error) {
            return false;
        }
    }

    function openBanner() {
        banner.hidden = false;
        acceptButton.focus({ preventScroll: true });
    }

    function closeBanner() {
        banner.hidden = true;
    }

    acceptButton.addEventListener("click", () => {
        if (!saveChoice("granted")) return;
        closeBanner();
        window.initializeTikTokPixel?.();
    });

    rejectButton.addEventListener("click", () => {
        if (!saveChoice("denied")) return;
        window.ttq?.revokeConsent?.();
        closeBanner();
    });

    settingsButton.addEventListener("click", openBanner);
    if (!readChoice()) openBanner();
})();
