(function () {
    "use strict";

    const SpeechService = {};
    const DEFAULT_PERMISSION_CACHE_MS = 120000;
    const DEFAULT_TIMEOUT_MS = 11000;
    const VOICE_LANG_PRIORITY = ["en-US", "en-GB", "en"];

    let microphonePermission = {
        granted: false,
        checkedAt: 0
    };
    let voiceCache = [];

    const MESSAGES = {
        listening: "أستمع الآن...",
        unsupported: "الميكروفون للتصحيح يعمل غالبًا على Chrome أو Edge.",
        insecure: "الميكروفون يحتاج HTTPS بعد النشر، أو localhost أثناء التطوير.",
        permission_denied: "تم رفض إذن الميكروفون. افتح إعدادات المتصفح واسمح باستخدام المايك.",
        no_speech: "لم أسمع صوتًا واضحًا. اقترب من المايك وحاول مرة أخرى.",
        timeout: "انتهى وقت الاستماع قبل وصول صوت واضح. اضغط المايك وتكلم مباشرة.",
        audio_capture: "لم يتم العثور على ميكروفون. تأكد من توصيله ثم حاول مرة أخرى.",
        network: "لم تتصل خدمة التعرف على الصوت. تأكد من الإنترنت واضغط المايك مرة أخرى.",
        service_unavailable: "خدمة التعرف على الصوت غير متاحة الآن في المتصفح. جرّب Chrome أو Edge وحدث الصفحة.",
        low_similarity: "حاول مرة أخرى. استمع للكلمة ثم كررها.",
        unknown: "تعذر تشغيل المايك الآن. حاول مرة أخرى.",
        speaker_unsupported: "المتصفح لا يدعم النطق الصوتي. جرّب Chrome أو Edge.",
        speaker_error: "تعذر تشغيل الصوت الآن. اضغط السماعة مرة أخرى.",
        excellent: "ممتاز! نطقك صحيح.",
        good: "جيد جدًا، أعدها مرة أخرى لتصل إلى الإتقان.",
        retry: "حاول مرة أخرى. استمع للكلمة ثم كررها.",
        helper_note: "تصحيح النطق هنا مساعد تدريبي مبني على Web Speech API، وليس تحليلًا صوتيًا عميقًا."
    };

    const CONTRACTIONS = [
        [/\bi'm\b/g, "i am"],
        [/\byou're\b/g, "you are"],
        [/\bhe's\b/g, "he is"],
        [/\bshe's\b/g, "she is"],
        [/\bit's\b/g, "it is"],
        [/\bwe're\b/g, "we are"],
        [/\bthey're\b/g, "they are"],
        [/\bcan't\b/g, "cannot"],
        [/\bdon't\b/g, "do not"],
        [/\bdoesn't\b/g, "does not"],
        [/\bdidn't\b/g, "did not"],
        [/\bisn't\b/g, "is not"],
        [/\baren't\b/g, "are not"],
        [/\bwon't\b/g, "will not"],
        [/\blet's\b/g, "let us"]
    ];

    function debug(...args) {
        if (window.ABCZ_DEBUG_SPEECH) console.debug("[SpeechService]", ...args);
    }

    function nowMs() {
        return Math.round((window.performance?.now?.() ?? Date.now()) * 10) / 10;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function toElement(container) {
        if (!container) return null;
        if (typeof container === "string") return document.querySelector(container);
        return container;
    }

    function wordsOf(text) {
        return SpeechService.normalizeText(text).split(" ").filter(Boolean);
    }

    function resolveType(type, expected) {
        if (type && type !== "sentence") return type;
        const count = wordsOf(expected).length;
        if (count <= 1) return "word";
        if (count <= 8) return "short_sentence";
        return "long_sentence";
    }

    function errorReason(error) {
        const raw = typeof error === "string" ? error : (error?.error || error?.name || "");
        if (raw === "not-allowed" || raw === "permission-denied" || raw === "NotAllowedError") return "mic_permission_denied";
        if (raw === "no-speech") return "no_speech";
        if (raw === "audio-capture" || raw === "NotFoundError") return "audio_capture";
        if (raw === "network") return "network";
        if (raw === "service-not-allowed" || raw === "bad-grammar" || raw === "language-not-supported") return "service_unavailable";
        if (raw === "timeout") return "timeout";
        if (raw === "browser_not_supported") return "browser_not_supported";
        if (raw === "insecure_context") return "insecure_context";
        return "unknown";
    }

    function messageForReason(reason) {
        if (reason === "browser_not_supported") return MESSAGES.unsupported;
        if (reason === "insecure_context") return MESSAGES.insecure;
        if (reason === "mic_permission_denied") return MESSAGES.permission_denied;
        if (reason === "no_speech") return MESSAGES.no_speech;
        if (reason === "timeout") return MESSAGES.timeout;
        if (reason === "audio_capture") return MESSAGES.audio_capture;
        if (reason === "network") return MESSAGES.network;
        if (reason === "service_unavailable") return MESSAGES.service_unavailable;
        if (reason === "low_similarity") return MESSAGES.low_similarity;
        return MESSAGES.unknown;
    }

    function addMetrics(result, metrics) {
        const endedAt = nowMs();
        const totalMs = Math.max(0, Math.round(endedAt - metrics.startedAt));
        return {
            ...result,
            latency_ms: totalMs,
            speech_metrics: {
                total_ms: totalMs,
                permission_ms: metrics.permissionMs,
                recognition_start_ms: metrics.recognitionStartMs,
                first_result_ms: metrics.firstResultMs,
                permission_cached: Boolean(metrics.permissionCached)
            }
        };
    }

    function permissionCacheFresh(cacheMs) {
        return microphonePermission.granted && (Date.now() - microphonePermission.checkedAt) < cacheMs;
    }

    function collectAlternatives(event) {
        const rows = Array.from(event.results || []);
        const alternatives = [];
        rows.forEach(result => {
            Array.from(result || []).forEach(item => {
                const transcript = String(item.transcript || "").trim();
                if (!transcript) return;
                alternatives.push({
                    transcript,
                    confidence: typeof item.confidence === "number" ? item.confidence : null
                });
            });
        });
        const seen = new Set();
        return alternatives.filter(item => {
            const key = SpeechService.normalizeText(item.transcript);
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }

    function injectStyles() {
        if (document.getElementById("speech-service-styles")) return;
        const style = document.createElement("style");
        style.id = "speech-service-styles";
        style.textContent = `
            .speech-service-result{margin-top:10px;padding:10px 12px;border:1px solid #d7e1ee;border-radius:8px;background:#fff;display:grid;gap:6px;color:#172033;line-height:1.55}
            .speech-service-result.excellent{border-color:#16a34a;background:#f0fdf4}
            .speech-service-result.good{border-color:#2563eb;background:#eff6ff}
            .speech-service-result.retry,.speech-service-result.error{border-color:#f59e0b;background:#fffbeb}
            .speech-service-result strong{font-weight:900}
            .speech-service-result .speech-note{font-size:12px;color:#64748b}
            .speech-service-result .speech-meta{display:flex;flex-wrap:wrap;gap:8px;font-size:12px;color:#475569}
            .speech-service-result .speech-pill{display:inline-flex;align-items:center;border:1px solid #d7e1ee;border-radius:999px;padding:2px 8px;background:rgba(255,255,255,.72)}
        `;
        document.head.appendChild(style);
    }

    SpeechService.messages = MESSAGES;

    SpeechService.isSupported = function () {
        return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
    };

    SpeechService.isSecureContextReady = function () {
        const host = window.location.hostname;
        return window.isSecureContext || ["localhost", "127.0.0.1", "::1"].includes(host);
    };

    SpeechService.getSupportMessage = function () {
        if (!SpeechService.isSecureContextReady()) return MESSAGES.insecure;
        if (!SpeechService.isSupported()) return MESSAGES.unsupported;
        return "";
    };

    SpeechService.ensureMicrophoneReady = async function (options = {}) {
        if (options.requestPermission === false || !navigator.mediaDevices?.getUserMedia) {
            return { ok: true, cached: false, skipped: true };
        }
        const cacheMs = Number(options.permissionCacheMs || DEFAULT_PERMISSION_CACHE_MS);
        if (permissionCacheFresh(cacheMs)) {
            return { ok: true, cached: true };
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: options.audioConstraints || {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            stream.getTracks().forEach(track => track.stop());
            microphonePermission = { granted: true, checkedAt: Date.now() };
            return { ok: true, cached: false };
        } catch (error) {
            microphonePermission = { granted: false, checkedAt: Date.now() };
            const failure_reason = errorReason(error);
            return {
                ok: false,
                cached: false,
                failure_reason,
                browser_error: error?.name || "permission",
                message: messageForReason(failure_reason)
            };
        }
    };

    SpeechService.normalizeText = function (text) {
        let value = String(text || "").toLowerCase().trim();
        CONTRACTIONS.forEach(([pattern, replacement]) => {
            value = value.replace(pattern, replacement);
        });
        return value
            .replace(/[^a-z0-9\s']/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    };

    SpeechService.levenshtein = function (a, b) {
        const left = SpeechService.normalizeText(a);
        const right = SpeechService.normalizeText(b);
        if (!left.length) return right.length;
        if (!right.length) return left.length;
        const matrix = Array.from({ length: left.length + 1 }, (_, i) => [i]);
        for (let j = 1; j <= right.length; j += 1) matrix[0][j] = j;
        for (let i = 1; i <= left.length; i += 1) {
            for (let j = 1; j <= right.length; j += 1) {
                const cost = left[i - 1] === right[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j - 1] + cost
                );
            }
        }
        return matrix[left.length][right.length];
    };

    SpeechService.similarity = function (expected, spoken) {
        const expectedClean = SpeechService.normalizeText(expected);
        const spokenClean = SpeechService.normalizeText(spoken);
        if (!expectedClean || !spokenClean) return 0;
        if (expectedClean === spokenClean) return 100;

        const distance = SpeechService.levenshtein(expectedClean, spokenClean);
        const charScore = Math.max(0, Math.round((1 - distance / Math.max(expectedClean.length, spokenClean.length)) * 100));

        const expectedWords = expectedClean.split(" ").filter(Boolean);
        const spokenWords = new Set(spokenClean.split(" ").filter(Boolean));
        const wordScore = expectedWords.length
            ? Math.round((expectedWords.filter(word => spokenWords.has(word)).length / expectedWords.length) * 100)
            : 0;

        if (expectedWords.length === 1) return charScore;
        return Math.round((charScore * 0.45) + (wordScore * 0.55));
    };

    SpeechService.compareWord = function (expected, spoken) {
        const score = SpeechService.similarity(expected, spoken);
        return {
            expected,
            spoken,
            score,
            status: SpeechService.getStatus(score, "word"),
            correctWords: score >= 70 ? [SpeechService.normalizeText(expected)] : [],
            missingWords: score >= 70 ? [] : [SpeechService.normalizeText(expected)].filter(Boolean),
            extraWords: [],
            orderGood: score >= 70
        };
    };

    SpeechService.compareSentence = function (expected, spoken) {
        const expectedWords = wordsOf(expected);
        const spokenWords = wordsOf(spoken);
        const spokenSet = new Set(spokenWords);
        const expectedSet = new Set(expectedWords);
        const correctWords = expectedWords.filter(word => spokenSet.has(word));
        const missingWords = expectedWords.filter(word => !spokenSet.has(word));
        const extraWords = spokenWords.filter(word => !expectedSet.has(word));
        const score = SpeechService.similarity(expected, spoken);
        const orderGood = correctWords.join(" ") === expectedWords.filter(word => spokenSet.has(word)).join(" ");
        return {
            expected,
            spoken,
            score,
            status: SpeechService.getStatus(score, resolveType("sentence", expected)),
            correctWords,
            missingWords,
            extraWords,
            orderGood
        };
    };

    SpeechService.getStatus = function (score, type) {
        const resolved = resolveType(type, "");
        const limits = {
            word: { excellent: 85, good: 70 },
            sound: { excellent: 85, good: 70 },
            pronoun: { excellent: 80, good: 65 },
            short_sentence: { excellent: 80, good: 65 },
            sentence: { excellent: 80, good: 65 },
            long_sentence: { excellent: 75, good: 60 },
            story: { excellent: 75, good: 60 }
        }[resolved] || { excellent: 80, good: 65 };
        if (score >= limits.excellent) return "excellent";
        if (score >= limits.good) return "good";
        return "retry";
    };

    SpeechService.statusLabel = function (status) {
        if (status === "excellent") return "ممتاز";
        if (status === "good") return "جيد";
        return "حاول مرة أخرى";
    };

    SpeechService.statusMessage = function (status) {
        if (status === "excellent") return MESSAGES.excellent;
        if (status === "good") return MESSAGES.good;
        return MESSAGES.retry;
    };

    SpeechService.renderResult = function (container, result) {
        const el = toElement(container);
        if (!el || !result) return;
        injectStyles();
        if (result.error) {
            const latency = result.latency_ms ? `<span class="speech-pill">زمن الاستجابة: ${escapeHtml(result.latency_ms)}ms</span>` : "";
            el.innerHTML = `<div class="speech-service-result error"><strong>${escapeHtml(result.message || MESSAGES.unknown)}</strong><div class="speech-meta">${latency}</div><div class="speech-note">${escapeHtml(MESSAGES.helper_note)}</div></div>`;
            return;
        }
        const missing = Array.isArray(result.missingWords) && result.missingWords.length
            ? `<div>ملاحظة: نسيت كلمة ${escapeHtml(result.missingWords.slice(0, 5).join(", "))}</div>`
            : "";
        const latency = result.latency_ms ? `<span class="speech-pill">زمن التصحيح: ${escapeHtml(result.latency_ms)}ms</span>` : "";
        const alternatives = Array.isArray(result.alternatives) && result.alternatives.length > 1
            ? `<span class="speech-pill">بدائل مسموعة: ${escapeHtml(result.alternatives.length)}</span>`
            : "";
        el.innerHTML = `
            <div class="speech-service-result ${escapeHtml(result.status)}">
                <div><strong>المطلوب:</strong> ${escapeHtml(result.expected || result.targetText || "")}</div>
                <div><strong>ما سمعته:</strong> ${escapeHtml(result.spoken || result.spokenText || "غير واضح")}</div>
                <div><strong>النسبة:</strong> ${Number(result.score || 0)}%</div>
                ${missing}
                <div><strong>الحالة:</strong> ${escapeHtml(SpeechService.statusLabel(result.status))}</div>
                <div class="speech-meta">${latency}${alternatives}</div>
                <div class="speech-note">${escapeHtml(MESSAGES.helper_note)}</div>
            </div>
        `;
    };

    SpeechService.isSynthesisSupported = function () {
        return Boolean("speechSynthesis" in window && window.SpeechSynthesisUtterance);
    };

    SpeechService.loadVoices = function () {
        if (!SpeechService.isSynthesisSupported()) return [];
        voiceCache = window.speechSynthesis.getVoices() || [];
        return voiceCache;
    };

    SpeechService.pickVoice = function (lang = "en-US") {
        const voices = voiceCache.length ? voiceCache : SpeechService.loadVoices();
        const normalizedLang = String(lang || "en-US").toLowerCase();
        return (
            voices.find(voice => String(voice.lang || "").toLowerCase() === normalizedLang) ||
            VOICE_LANG_PRIORITY
                .map(code => voices.find(voice => String(voice.lang || "").toLowerCase().startsWith(code.toLowerCase())))
                .find(Boolean) ||
            voices.find(voice => String(voice.lang || "").toLowerCase().startsWith("en")) ||
            null
        );
    };

    SpeechService.speakText = function (text, options = {}) {
        const message = String(text || "").trim();
        if (!message) return Promise.resolve({ ok: false, reason: "empty_text" });
        if (!SpeechService.isSynthesisSupported()) {
            return Promise.resolve({ ok: false, reason: "speaker_unsupported", message: MESSAGES.speaker_unsupported });
        }
        const startedAt = nowMs();
        return new Promise(resolve => {
            let settled = false;
            let watchdogId = null;
            const settle = value => {
                if (settled) return;
                settled = true;
                if (watchdogId) window.clearTimeout(watchdogId);
                resolve(value);
            };
            try {
                if (options.cancel !== false) window.speechSynthesis.cancel();
                const utterance = new window.SpeechSynthesisUtterance(message);
                utterance.lang = options.lang || "en-US";
                utterance.rate = Number(options.rate || (message.length <= 3 ? 0.78 : 0.9));
                utterance.pitch = Number(options.pitch || 1);
                const voice = options.voice || SpeechService.pickVoice(utterance.lang);
                if (voice) utterance.voice = voice;
                watchdogId = window.setTimeout(() => {
                    settle({ ok: true, latency_ms: Math.max(0, Math.round(nowMs() - startedAt)), watchdog: true });
                }, Number(options.timeoutMs || Math.min(18000, Math.max(3500, message.length * 140))));
                utterance.onend = () => settle({ ok: true, latency_ms: Math.max(0, Math.round(nowMs() - startedAt)) });
                utterance.onerror = event => settle({ ok: false, reason: event.error || "speaker_error", message: MESSAGES.speaker_error });
                window.speechSynthesis.speak(utterance);
            } catch (error) {
                settle({ ok: false, reason: error?.name || "speaker_error", message: MESSAGES.speaker_error });
            }
        });
    };

    SpeechService.saveProgress = async function (payload, saveProgress) {
        if (!saveProgress) return null;
        try {
            if (typeof saveProgress === "function") return await saveProgress(payload);
            if (typeof saveProgress === "string") {
                const response = await fetch(saveProgress, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith("csrftoken="))?.split("=")[1] || ""
                    },
                    body: JSON.stringify(payload)
                });
                return await response.json();
            }
        } catch (error) {
            debug("save failed", error);
        }
        return null;
    };

    SpeechService.startRecognition = async function (options = {}) {
        const targetText = String(options.targetText || "");
        const type = resolveType(options.type || "word", targetText);
        const section = options.section || "";
        const level = options.level || "";
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const metrics = {
            startedAt: nowMs(),
            permissionMs: 0,
            recognitionStartMs: null,
            firstResultMs: null,
            permissionCached: false
        };

        if (!SpeechService.isSecureContextReady()) {
            const result = addMetrics({ error: true, failure_reason: "insecure_context", browser_error: "insecure_context", message: MESSAGES.insecure, targetText, section, level }, metrics);
            options.onError?.(result);
            options.onEnd?.(result);
            return result;
        }

        if (!Recognition) {
            const result = addMetrics({ error: true, failure_reason: "browser_not_supported", browser_error: "browser_not_supported", message: MESSAGES.unsupported, targetText, section, level }, metrics);
            options.onError?.(result);
            options.onEnd?.(result);
            return result;
        }

        options.onStart?.({ targetText, type, section, level, message: MESSAGES.listening });
        debug("start", { targetText, type, section, level });

        const permissionStartedAt = nowMs();
        const permission = await SpeechService.ensureMicrophoneReady(options);
        metrics.permissionMs = Math.max(0, Math.round(nowMs() - permissionStartedAt));
        metrics.permissionCached = Boolean(permission.cached);
        if (!permission.ok) {
            const result = addMetrics({ error: true, ...permission, targetText, section, level, score: 0, status: "retry", is_mastered: false, mastered: false, spokenText: "" }, metrics);
            options.onError?.(result);
            options.onEnd?.(result);
            await SpeechService.saveProgress(result, options.saveProgress);
            return result;
        }

        return await new Promise(resolve => {
            const recognition = new Recognition();
            let settled = false;
            let timeoutId = null;
            let timeoutExpired = false;

            function finish(result) {
                if (settled) return;
                settled = true;
                if (timeoutId) window.clearTimeout(timeoutId);
                const finalResult = addMetrics(result, metrics);
                options.onEnd?.(finalResult);
                resolve(finalResult);
            }

            async function finishAfterSave(result, callback) {
                if (settled) return;
                settled = true;
                if (timeoutId) window.clearTimeout(timeoutId);
                const finalResult = addMetrics(result, metrics);
                callback?.(finalResult);
                await SpeechService.saveProgress(finalResult, options.saveProgress);
                options.onEnd?.(finalResult);
                resolve(finalResult);
            }

            recognition.lang = options.lang || "en-US";
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = options.maxAlternatives || 8;

            recognition.onstart = () => {
                metrics.recognitionStartMs = Math.max(0, Math.round(nowMs() - metrics.startedAt));
                options.onListening?.({ targetText, type, section, level, message: MESSAGES.listening, speech_metrics: { ...metrics } });
            };

            recognition.onresult = async event => {
                metrics.firstResultMs = Math.max(0, Math.round(nowMs() - metrics.startedAt));
                const alternativeRows = collectAlternatives(event);
                const alternatives = alternativeRows.map(item => item.transcript);
                const scored = alternatives
                    .map(spoken => {
                        const comparison = type === "word" || type === "sound"
                            ? SpeechService.compareWord(targetText, spoken)
                            : SpeechService.compareSentence(targetText, spoken);
                        return { ...comparison, spokenText: spoken };
                    })
                    .sort((a, b) => b.score - a.score);
                const best = scored[0] || { expected: targetText, spoken: "", spokenText: "", score: 0, status: "retry", missingWords: wordsOf(targetText), extraWords: [], correctWords: [] };
                const result = {
                    ...best,
                    targetText,
                    type,
                    section,
                    level,
                    alternatives,
                    alternative_confidence: alternativeRows,
                    is_mastered: best.status === "excellent",
                    mastered: best.status !== "retry",
                    failure_reason: best.status === "retry" ? "low_similarity" : null,
                    browser_error: null
                };
                debug("result", result);
                finishAfterSave(result, options.onResult);
            };

            recognition.onerror = async event => {
                const failure_reason = timeoutExpired ? "timeout" : errorReason(event);
                const result = { error: true, targetText, type, section, level, score: 0, status: "retry", is_mastered: false, mastered: false, spokenText: "", failure_reason, browser_error: event.error || "unknown", message: messageForReason(failure_reason) };
                debug("error", result);
                finishAfterSave(result, options.onError);
            };

            recognition.onend = () => {
                if (!settled) {
                    const failure_reason = timeoutExpired ? "timeout" : "no_speech";
                    const result = { error: true, targetText, type, section, level, score: 0, status: "retry", is_mastered: false, mastered: false, spokenText: "", failure_reason, browser_error: timeoutExpired ? "timeout" : "no-result", message: messageForReason(failure_reason) };
                    finishAfterSave(result, options.onError);
                }
            };

            try {
                timeoutId = window.setTimeout(() => {
                    timeoutExpired = true;
                    try { recognition.abort(); } catch {}
                }, options.timeoutMs || DEFAULT_TIMEOUT_MS);
                recognition.start();
            } catch (error) {
                const failure_reason = errorReason(error);
                finish({ error: true, targetText, type, section, level, score: 0, status: "retry", is_mastered: false, mastered: false, spokenText: "", failure_reason, browser_error: error?.name || "start_failed", message: messageForReason(failure_reason) });
            }
        });
    };

    SpeechService.testMicrophone = function (container) {
        return SpeechService.startRecognition({
            targetText: "hello",
            type: "word",
            section: "mic_test",
            onStart: () => SpeechService.renderResult(container, { expected: "hello", spoken: MESSAGES.listening, score: 0, status: "retry" }),
            onResult: result => SpeechService.renderResult(container, result),
            onError: result => SpeechService.renderResult(container, result)
        });
    };

    window.SpeechService = SpeechService;
    window.PronunciationManager = SpeechService;
    if (SpeechService.isSynthesisSupported()) {
        SpeechService.loadVoices();
        if (typeof window.speechSynthesis.addEventListener === "function") {
            window.speechSynthesis.addEventListener("voiceschanged", SpeechService.loadVoices);
        } else {
            window.speechSynthesis.onvoiceschanged = SpeechService.loadVoices;
        }
    }
})();
