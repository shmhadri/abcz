(function (window) {
    "use strict";

    const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    const WORDS_PER_LETTER = 5;
    const MAX_WORD_LENGTH = 4;

    const SHORT_LETTER_WORDS = {
        A: [
            { word: "ant", translation: "نملة", emoji: "🐜" },
            { word: "axe", translation: "فأس", emoji: "🪓" },
            { word: "arm", translation: "ذراع", emoji: "💪" },
            { word: "art", translation: "فن", emoji: "🎨" },
            { word: "air", translation: "هواء", emoji: "💨" }
        ],
        B: [
            { word: "bat", translation: "خفاش", emoji: "🦇" },
            { word: "bag", translation: "حقيبة", emoji: "🎒" },
            { word: "bed", translation: "سرير", emoji: "🛏️" },
            { word: "bus", translation: "حافلة", emoji: "🚌" },
            { word: "box", translation: "صندوق", emoji: "📦" }
        ],
        C: [
            { word: "cat", translation: "قطة", emoji: "🐱" },
            { word: "car", translation: "سيارة", emoji: "🚗" },
            { word: "cup", translation: "كوب", emoji: "☕" },
            { word: "cow", translation: "بقرة", emoji: "🐮" },
            { word: "cap", translation: "قبعة", emoji: "🧢" }
        ],
        D: [
            { word: "dog", translation: "كلب", emoji: "🐶" },
            { word: "door", translation: "باب", emoji: "🚪" },
            { word: "doll", translation: "دمية", emoji: "🧸" },
            { word: "duck", translation: "بطة", emoji: "🦆" },
            { word: "desk", translation: "مكتب", emoji: "🪑" }
        ],
        E: [
            { word: "egg", translation: "بيضة", emoji: "🥚" },
            { word: "ear", translation: "أذن", emoji: "👂" },
            { word: "eye", translation: "عين", emoji: "👁️" },
            { word: "elf", translation: "قزم", emoji: "🧝" },
            { word: "end", translation: "نهاية", emoji: "🏁" }
        ],
        F: [
            { word: "fan", translation: "مروحة", emoji: "🪭" },
            { word: "fish", translation: "سمكة", emoji: "🐟" },
            { word: "fox", translation: "ثعلب", emoji: "🦊" },
            { word: "foot", translation: "قدم", emoji: "🦶" },
            { word: "fire", translation: "نار", emoji: "🔥" }
        ],
        G: [
            { word: "goat", translation: "ماعز", emoji: "🐐" },
            { word: "girl", translation: "فتاة", emoji: "👧" },
            { word: "gum", translation: "علكة", emoji: "🍬" },
            { word: "gate", translation: "بوابة", emoji: "🚪" },
            { word: "gift", translation: "هدية", emoji: "🎁" }
        ],
        H: [
            { word: "hat", translation: "قبعة", emoji: "🎩" },
            { word: "hen", translation: "دجاجة", emoji: "🐔" },
            { word: "hand", translation: "يد", emoji: "✋" },
            { word: "home", translation: "منزل", emoji: "🏠" },
            { word: "hill", translation: "تل", emoji: "⛰️" }
        ],
        I: [
            { word: "ice", translation: "ثلج", emoji: "🧊" },
            { word: "ink", translation: "حبر", emoji: "🖋️" },
            { word: "ill", translation: "مريض", emoji: "🤒" },
            { word: "in", translation: "داخل", emoji: "📥" },
            { word: "iron", translation: "مكواة", emoji: "🔥" }
        ],
        J: [
            { word: "jam", translation: "مربى", emoji: "🍓" },
            { word: "jet", translation: "طائرة", emoji: "✈️" },
            { word: "jar", translation: "جرة", emoji: "🫙" },
            { word: "jeep", translation: "جيب", emoji: "🚙" },
            { word: "jump", translation: "يقفز", emoji: "🏃" }
        ],
        K: [
            { word: "key", translation: "مفتاح", emoji: "🔑" },
            { word: "kid", translation: "طفل", emoji: "🧒" },
            { word: "king", translation: "ملك", emoji: "🤴" },
            { word: "kite", translation: "طائرة ورقية", emoji: "🪁" },
            { word: "kick", translation: "ركلة", emoji: "⚽" }
        ],
        L: [
            { word: "lion", translation: "أسد", emoji: "🦁" },
            { word: "leg", translation: "رجل", emoji: "🦵" },
            { word: "lamp", translation: "مصباح", emoji: "💡" },
            { word: "log", translation: "جذع", emoji: "🪵" },
            { word: "leaf", translation: "ورقة", emoji: "🍃" }
        ],
        M: [
            { word: "man", translation: "رجل", emoji: "👨" },
            { word: "map", translation: "خريطة", emoji: "🗺️" },
            { word: "milk", translation: "حليب", emoji: "🥛" },
            { word: "moon", translation: "قمر", emoji: "🌙" },
            { word: "mug", translation: "كوب", emoji: "☕" }
        ],
        N: [
            { word: "net", translation: "شبكة", emoji: "🥅" },
            { word: "nose", translation: "أنف", emoji: "👃" },
            { word: "nut", translation: "جوز", emoji: "🥜" },
            { word: "nest", translation: "عش", emoji: "🪹" },
            { word: "nail", translation: "ظفر", emoji: "💅" }
        ],
        O: [
            { word: "ox", translation: "ثور", emoji: "🐂" },
            { word: "owl", translation: "بومة", emoji: "🦉" },
            { word: "orb", translation: "كرة", emoji: "🔮" },
            { word: "oven", translation: "فرن", emoji: "🍳" },
            { word: "open", translation: "يفتح", emoji: "🔓" }
        ],
        P: [
            { word: "pen", translation: "قلم", emoji: "🖊️" },
            { word: "pie", translation: "فطيرة", emoji: "🥧" },
            { word: "pot", translation: "قدر", emoji: "🍲" },
            { word: "park", translation: "حديقة", emoji: "🏞️" },
            { word: "pear", translation: "كمثرى", emoji: "🍐" }
        ],
        Q: [
            { word: "quiz", translation: "اختبار", emoji: "❓" },
            { word: "quit", translation: "يتوقف", emoji: "🛑" },
            { word: "quip", translation: "نكتة", emoji: "💬" },
            { word: "quad", translation: "رباعي", emoji: "4️⃣" },
            { word: "quay", translation: "رصيف", emoji: "⚓" }
        ],
        R: [
            { word: "rat", translation: "جرذ", emoji: "🐀" },
            { word: "red", translation: "أحمر", emoji: "🔴" },
            { word: "ring", translation: "خاتم", emoji: "💍" },
            { word: "road", translation: "طريق", emoji: "🛣️" },
            { word: "rain", translation: "مطر", emoji: "🌧️" }
        ],
        S: [
            { word: "sun", translation: "شمس", emoji: "☀️" },
            { word: "sea", translation: "بحر", emoji: "🌊" },
            { word: "sock", translation: "جورب", emoji: "🧦" },
            { word: "star", translation: "نجمة", emoji: "⭐" },
            { word: "ship", translation: "سفينة", emoji: "🚢" }
        ],
        T: [
            { word: "top", translation: "قمة", emoji: "🔝" },
            { word: "toy", translation: "لعبة", emoji: "🧸" },
            { word: "ten", translation: "عشرة", emoji: "🔟" },
            { word: "tree", translation: "شجرة", emoji: "🌳" },
            { word: "tea", translation: "شاي", emoji: "🍵" }
        ],
        U: [
            { word: "up", translation: "أعلى", emoji: "⬆️" },
            { word: "us", translation: "نحن", emoji: "👥" },
            { word: "urn", translation: "جرة", emoji: "⚱️" },
            { word: "use", translation: "يستخدم", emoji: "🛠️" },
            { word: "unit", translation: "وحدة", emoji: "1️⃣" }
        ],
        V: [
            { word: "van", translation: "شاحنة", emoji: "🚐" },
            { word: "vet", translation: "طبيب بيطري", emoji: "👨‍⚕️" },
            { word: "vase", translation: "مزهرية", emoji: "🏺" },
            { word: "vest", translation: "سترة", emoji: "🦺" },
            { word: "vine", translation: "كرمة", emoji: "🌿" }
        ],
        W: [
            { word: "web", translation: "شبكة", emoji: "🕸️" },
            { word: "wig", translation: "شعر مستعار", emoji: "🎭" },
            { word: "wolf", translation: "ذئب", emoji: "🐺" },
            { word: "wall", translation: "جدار", emoji: "🧱" },
            { word: "wave", translation: "موجة", emoji: "🌊" }
        ],
        X: [
            { word: "xray", translation: "أشعة", emoji: "🩻" },
            { word: "xmas", translation: "عيد الميلاد", emoji: "🎄" },
            { word: "xbox", translation: "إكس بوكس", emoji: "🎮" },
            { word: "xeno", translation: "غريب", emoji: "👽" },
            { word: "xyst", translation: "ممر", emoji: "🏛️" }
        ],
        Y: [
            { word: "yak", translation: "ثور التبت", emoji: "🐂" },
            { word: "yes", translation: "نعم", emoji: "👍" },
            { word: "yoyo", translation: "يويو", emoji: "🪀" },
            { word: "yard", translation: "فناء", emoji: "🏡" },
            { word: "yarn", translation: "خيط", emoji: "🧶" }
        ],
        Z: [
            { word: "zest", translation: "حماس", emoji: "✨" },
            { word: "zoo", translation: "حديقة حيوانات", emoji: "🐾" },
            { word: "zero", translation: "صفر", emoji: "0️⃣" },
            { word: "zone", translation: "منطقة", emoji: "🚧" },
            { word: "zen", translation: "هدوء", emoji: "🧘" }
        ]
    };

    const LETTER_DATA = {};

    LETTERS.forEach(letter => {
        const words = (SHORT_LETTER_WORDS[letter] || [])
            .filter(item => String(item.word || "").trim().length <= MAX_WORD_LENGTH)
            .slice(0, WORDS_PER_LETTER)
            .map(item => ({
                word: String(item.word || "").trim().toLowerCase(),
                translation: item.translation || item.word,
                emoji: item.emoji || "\uD83D\uDD24"
            }));

        LETTER_DATA[letter] = {
            words,
            quiz: [],
            type: ["A", "E", "I", "O", "U"].includes(letter) ? "\u062d\u0631\u0641 \u0645\u062a\u062d\u0631\u0643" : "\u062d\u0631\u0641 \u0633\u0627\u0643\u0646"
        };
    });

    window.LETTERS = LETTERS;
    window.WORDS_PER_LETTER = WORDS_PER_LETTER;
    window.MAX_WORD_LENGTH = MAX_WORD_LENGTH;
    window.LETTER_DATA = LETTER_DATA;
})(window);
