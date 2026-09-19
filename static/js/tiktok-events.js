(() => {
    "use strict";

    const consentKey = "smartlearning_analytics_marketing_consent_v1";
    let initialEventsSent = false;
    let purchaseRequested = false;

    function hasConsent() {
        try {
            return window.localStorage.getItem(consentKey) === "granted";
        } catch (error) {
            return false;
        }
    }

    window.trackTikTokEvent = function (eventName, payload) {
        try {
            if (
                hasConsent() &&
                window.ttq &&
                typeof window.ttq.track === "function" &&
                typeof eventName === "string" &&
                eventName.length > 0
            ) {
                window.ttq.track(eventName, payload || {});
                return true;
            }
        } catch (error) {
            // Analytics is best-effort and must never break user flows.
        }
        return false;
    };

    function csrfToken() {
        const item = document.cookie.split(";").map((value) => value.trim())
            .find((value) => value.startsWith("csrftoken="));
        return item ? decodeURIComponent(item.split("=").slice(1).join("=")) : "";
    }

    function sendInitialEvents() {
        if (initialEventsSent || !hasConsent()) return;
        const data = document.getElementById("tiktok-event-data");
        const events = data ? JSON.parse(data.textContent) : [];
        if (!Array.isArray(events)) return;
        events.forEach((item) => {
            if (!item || typeof item !== "object") return;
            window.trackTikTokEvent(item.name, item.payload);
        });
        initialEventsSent = true;
    }

    async function claimAndSendPurchase() {
        if (purchaseRequested || !hasConsent()) return;
        const data = document.getElementById("tiktok-purchase-url");
        const url = data ? JSON.parse(data.textContent) : "";
        if (typeof url !== "string" || !url) return;
        purchaseRequested = true;
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken(),
                    "X-Analytics-Marketing-Consent": "granted",
                    "Accept": "application/json",
                },
                credentials: "same-origin",
            });
            if (response.status === 204) return;
            if (!response.ok) throw new Error("Purchase claim failed");
            const result = await response.json();
            if (result && result.event) {
                window.trackTikTokEvent(result.event.name, result.event.payload);
            }
        } catch (error) {
            purchaseRequested = false;
        }
    }

    function flush() {
        try {
            sendInitialEvents();
            claimAndSendPurchase();
        } catch (error) {}
    }

    window.addEventListener("tiktok:ready", flush);
    flush();
})();
