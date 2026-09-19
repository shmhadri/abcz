/* TikTok's standard browser pixel bootstrap, with the ID supplied by Django. */
(() => {
    "use strict";

    let initialized = false;

    window.initializeTikTokPixel = function () {
        if (initialized) {
            window.ttq?.grantConsent?.();
            window.dispatchEvent(new CustomEvent("tiktok:ready"));
            return true;
        }
        const config = document.getElementById("tiktok-pixel-config");
        const pixelId = config ? JSON.parse(config.textContent) : "";
        if (typeof pixelId !== "string" || !/^[A-Z0-9]+$/.test(pixelId)) return false;

        !function (w, d, t) {
            w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie","holdConsent","revokeConsent","grantConsent"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e},ttq.load=function(e,n){var r="https://analytics.tiktok.com/i18n/pixel/events.js",o=n&&n.partner;ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=r,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};n=d.createElement("script"),n.type="text/javascript",n.async=!0,n.src=r+"?sdkid="+e+"&lib="+t;e=d.getElementsByTagName("script")[0];e.parentNode.insertBefore(n,e)};

            ttq.load(pixelId);
            ttq.grantConsent();
            ttq.page();
        }(window, document, "ttq");
        initialized = true;
        window.dispatchEvent(new CustomEvent("tiktok:ready"));
        return true;
    };

    try {
        if (window.localStorage.getItem("smartlearning_analytics_marketing_consent_v1") === "granted") {
            window.initializeTikTokPixel();
        }
    } catch (error) {}
})();
