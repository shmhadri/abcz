// بيانات التطبيق
// --- Helper Functions for Safety ---
let warned = false;
function warnOnce(msg) {
  if (warned) return;
  warned = true;
  console.warn(msg);
}

function safeSetText(selector, value) {
  const el = document.querySelector(selector);
  if (!el) return false;
  el.textContent = value;
  return true;
}

function safeSetElementText(el, value) {
    if (!el) return false;
    el.textContent = value;
    return true;
}
// -----------------------------------

        const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
        
        // نظام إدارة الصوت البريطاني المحسن
        class BritishSoundManager {
            constructor() {
                this.sounds = new Map();
                this.currentSpeech = null;
                this.isSpeaking = false;
                this.audioQueue = [];
                this.isProcessing = false;
                this.britishVoices = [];
                this.currentBritishVoice = null;
            }
            
            async initialize() {
                if (window.speechSynthesis) {
                    // انتظر حتى تكون الأصوات متاحة
                    const loadVoices = () => {
                        const voices = window.speechSynthesis.getVoices();
                        this.britishVoices = voices.filter(voice => 
                            voice.lang.startsWith('en-GB') || 
                            voice.name.toLowerCase().includes('british') ||
                            voice.name.toLowerCase().includes('uk')
                        );
                        
                        // إذا لم نجد أصوات بريطانية، نبحث عن أي صوت ذكر إنجليزي
                        if (this.britishVoices.length === 0) {
                            this.britishVoices = voices.filter(voice => 
                                voice.lang.startsWith('en') && 
                                (voice.name.toLowerCase().includes('male') || 
                                 !voice.name.toLowerCase().includes('female'))
                            );
                        }
                        
                        // اختر أفضل صوت بريطاني
                        this.currentBritishVoice = this.britishVoices[0] || voices.find(v => v.lang.startsWith('en'));
                    };
                    
                    loadVoices();
                    window.speechSynthesis.onvoiceschanged = loadVoices;
                }
            }
            
            async speak(text, lang = 'en-GB') {
                if (!window.speechSynthesis || !this.isSpeakingEnabled) return;
                
                return new Promise((resolve) => {
                    // إلغاء أي كلام سابق
                    if (this.isSpeaking) {
                        window.speechSynthesis.cancel();
                    }
                    
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = lang;
                    utterance.rate = 0.9; // سرعة متوسطة
                    utterance.pitch = 1.0; // طبقة صوت طبيعية
                    utterance.volume = 1;
                    
                    // استخدام الصوت البريطاني
                    if (this.currentBritishVoice) {
                        utterance.voice = this.currentBritishVoice;
                    } else {
                        const voices = window.speechSynthesis.getVoices();
                        const britishVoice = voices.find(voice => 
                            voice.lang.startsWith('en-GB') || 
                            voice.name.toLowerCase().includes('british')
                        ) || voices.find(voice => 
                            voice.lang.startsWith('en') && 
                            voice.name.toLowerCase().includes('male')
                        );
                        
                        if (britishVoice) {
                            utterance.voice = britishVoice;
                        }
                    }
                    
                    utterance.onstart = () => {
                        this.isSpeaking = true;
                        this.currentSpeech = utterance;
                    };
                    
                    utterance.onend = () => {
                        this.isSpeaking = false;
                        this.currentSpeech = null;
                        resolve();
                    };
                    
                    utterance.onerror = () => {
                        this.isSpeaking = false;
                        this.currentSpeech = null;
                        resolve();
                    };
                    
                    setTimeout(() => {
                        window.speechSynthesis.speak(utterance);
                    }, 50);
                });
            }
            
            playSound(type) {
                if (!this.sounds.has(type)) {
                    this.createSound(type);
                }
                
                try {
                    const sound = this.sounds.get(type);
                    sound.currentTime = 0;
                    sound.play().catch(() => {});
                } catch (e) {}
            }
            
            createSound(type) {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                let frequency, duration;
                
                switch(type) {
                    case 'success':
                        frequency = [523.25, 659.25, 783.99]; // C5, E5, G5
                        duration = 0.5;
                        break;
                    case 'error':
                        frequency = [220, 180];
                        duration = 0.3;
                        break;
                    case 'click':
                        frequency = [440]; // A4
                        duration = 0.1;
                        break;
                    case 'win':
                        frequency = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
                        duration = 0.8;
                        break;
                    case 'fireworks':
                        frequency = [392, 523.25, 659.25, 784]; // G4, C5, E5, G5
                        duration = 1.0;
                        break;
                    default:
                        frequency = [440];
                        duration = 0.2;
                }
                
                oscillator.frequency.setValueAtTime(frequency[0], audioContext.currentTime);
                
                if (frequency.length > 1) {
                    frequency.forEach((freq, index) => {
                        oscillator.frequency.setValueAtTime(freq, audioContext.currentTime + (index * 0.15));
                    });
                }
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + duration);
                
                this.sounds.set(type, { oscillator, gainNode, audioContext });
            }
            
            stopAll() {
                if (this.isSpeaking) {
                    window.speechSynthesis.cancel();
                    this.isSpeaking = false;
                }
                
                this.sounds.forEach(sound => {
                    try {
                        sound.oscillator.stop();
                    } catch (e) {}
                });
                this.sounds.clear();
            }
        }

        // بيانات الحروف والكلمات المحسنة
        const LETTER_DATA = {};
        
        // تهيئة بيانات جميع الحروف
        LETTERS.forEach(letter => {
            let words = [];
            let emojis = [];
            let translations = [];
            
            switch(letter) {
                case 'A':
                    words = ["Apple", "Ant", "Airplane", "Arrow", "Astronaut", "Alligator"];
                    emojis = ["🍎", "🐜", "✈️", "🏹", "🧑‍🚀", "🐊"];
                    translations = ["تفاحة", "نملة", "طائرة", "سهم", "رائد فضاء", "تمساح"];
                    break;
                case 'B':
                    words = ["Ball", "Banana", "Butterfly", "Book", "Bear", "Bird"];
                    emojis = ["⚽", "🍌", "🦋", "📖", "🐻", "🐦"];
                    translations = ["كرة", "موزة", "فراشة", "كتاب", "دب", "طائر"];
                    break;
                case 'C':
                    words = ["Cat", "Car", "Cake", "Candle", "Crown", "Cloud"];
                    emojis = ["🐱", "🚗", "🍰", "🕯️", "👑", "☁️"];
                    translations = ["قطة", "سيارة", "كعكة", "شمعة", "تاج", "سحابة"];
                    break;
                case 'D':
                    words = ["Dog", "Duck", "Dolphin", "Door", "Diamond", "Drum"];
                    emojis = ["🐶", "🦆", "🐬", "🚪", "💎", "🥁"];
                    translations = ["كلب", "بطة", "دولفين", "باب", "ألماس", "طبل"];
                    break;
                case 'E':
                    words = ["Elephant", "Egg", "Eagle", "Earth", "Engine", "Eyes"];
                    emojis = ["🐘", "🥚", "🦅", "🌍", "🚂", "👀"];
                    translations = ["فيل", "بيضة", "نسر", "أرض", "محرك", "عيون"];
                    break;
                case 'F':
                    words = ["Fish", "Flower", "Frog", "Flag", "Fire", "Fox"];
                    emojis = ["🐟", "🌹", "🐸", "🚩", "🔥", "🦊"];
                    translations = ["سمكة", "زهرة", "ضفدع", "علم", "نار", "ثعلب"];
                    break;
                case 'G':
                    words = ["Goat", "Grapes", "Guitar", "Glasses", "Garden", "Gift"];
                    emojis = ["🐐", "🍇", "🎸", "👓", "🌳", "🎁"];
                    translations = ["ماعز", "عنب", "جيتار", "نظارات", "حديقة", "هدية"];
                    break;
                case 'H':
                    words = ["House", "Horse", "Hat", "Heart", "Hand", "Honey"];
                    emojis = ["🏠", "🐴", "🎩", "❤️", "✋", "🍯"];
                    translations = ["منزل", "حصان", "قبعة", "قلب", "يد", "عسل"];
                    break;
                case 'I':
                    words = ["Ice", "Igloo", "Insect", "Island", "Ice Cream", "Ink"];
                    emojis = ["🧊", "🧊", "🐛", "🏝️", "🍦", "🖋️"];
                    translations = ["جليد", "بيت جليدي", "حشرة", "جزيرة", "آيس كريم", "حبر"];
                    break;
                case 'J':
                    words = ["Juice", "Jellyfish", "Jacket", "Jar", "Jewel", "Jet"];
                    emojis = ["🧃", "🪼", "🧥", "🫙", "💎", "✈️"];
                    translations = ["عصير", "قنديل بحر", "سترة", "جرة", "جوهرة", "طائرة نفاثة"];
                    break;
                case 'K':
                    words = ["Key", "Kite", "Kangaroo", "King", "Kitchen", "Kitten"];
                    emojis = ["🔑", "🪁", "🦘", "🤴", "🍳", "🐱"];
                    translations = ["مفتاح", "طائرة ورقية", "كنغر", "ملك", "مطبخ", "هريرة"];
                    break;
                case 'L':
                    words = ["Lion", "Lemon", "Leaf", "Ladder", "Light", "Lamp"];
                    emojis = ["🦁", "🍋", "🍃", "🪜", "💡", "🪔"];
                    translations = ["أسد", "ليمون", "ورقة", "سلم", "ضوء", "مصباح"];
                    break;
                case 'M':
                    words = ["Monkey", "Moon", "Milk", "Mouse", "Mountain", "Music"];
                    emojis = ["🐒", "🌙", "🥛", "🐭", "⛰️", "🎵"];
                    translations = ["قرد", "قمر", "حليب", "فأر", "جبل", "موسيقى"];
                    break;
                case 'N':
                    words = ["Nest", "Nose", "Nut", "Night", "Nurse", "Numbers"];
                    emojis = ["🪹", "👃", "🥜", "🌙", "👩‍⚕️", "🔢"];
                    translations = ["عش", "أنف", "مكسرات", "ليل", "ممرضة", "أرقام"];
                    break;
                case 'O':
                    words = ["Orange", "Owl", "Octopus", "Ocean", "Onion", "Ostrich"];
                    emojis = ["🍊", "🦉", "🐙", "🌊", "🧅", "🦤"];
                    translations = ["برتقال", "بومة", "أخطبوط", "محيط", "بصل", "نعامة"];
                    break;
                case 'P':
                    words = ["Penguin", "Pizza", "Pencil", "Panda", "Pineapple", "Pear"];
                    emojis = ["🐧", "🍕", "✏️", "🐼", "🍍", "🍐"];
                    translations = ["بطريق", "بيتزا", "قلم رصاص", "باندا", "أناناس", "كمثرى"];
                    break;
                case 'Q':
                    words = ["Queen", "Quilt", "Question", "Quack", "Quarter", "Quiet"];
                    emojis = ["👸", "🛏️", "❓", "🦆", "🪙", "🤫"];
                    translations = ["ملكة", "لحاف", "سؤال", "صرخة بطة", "ربع", "هادئ"];
                    break;
                case 'R':
                    words = ["Rabbit", "Rainbow", "Robot", "Rose", "Rocket", "Ring"];
                    emojis = ["🐰", "🌈", "🤖", "🌹", "🚀", "💍"];
                    translations = ["أرنب", "قوس قزح", "روبوت", "وردة", "صاروخ", "خاتم"];
                    break;
                case 'S':
                    words = ["Sun", "Star", "Snake", "Spider", "Strawberry", "Ship"];
                    emojis = ["☀️", "⭐", "🐍", "🕷️", "🍓", "🚢"];
                    translations = ["شمس", "نجمة", "ثعبان", "عنكبوت", "فراولة", "سفينة"];
                    break;
                case 'T':
                    words = ["Tiger", "Tree", "Table", "Train", "Tomato", "Turtle"];
                    emojis = ["🐯", "🌳", "🪑", "🚂", "🍅", "🐢"];
                    translations = ["نمر", "شجرة", "طاولة", "قطار", "طماطم", "سلحفاة"];
                    break;
                case 'U':
                    words = ["Umbrella", "Unicorn", "Uniform", "Ukulele", "Up", "Under"];
                    emojis = ["☂️", "🦄", "👔", "🎵", "⬆️", "⬇️"];
                    translations = ["مظلة", "حصان وحيد القرن", "زي موحد", "عود", "أعلى", "تحت"];
                    break;
                case 'V':
                    words = ["Violin", "Volcano", "Vegetable", "Van", "Vase", "Vacuum"];
                    emojis = ["🎻", "🌋", "🥦", "🚐", "🏺", "🧹"];
                    translations = ["كمان", "بركان", "خضار", "شاحنة", "مزهرية", "مكنسة كهربائية"];
                    break;
                case 'W':
                    words = ["Watermelon", "Whale", "Wheel", "Wolf", "Window", "Watch"];
                    emojis = ["🍉", "🐋", "🛞", "🐺", "🪟", "⌚"];
                    translations = ["بطيخ", "حوت", "عجلة", "ذئب", "نافذة", "ساعة"];
                    break;
                case 'X':
                    words = ["Xylophone", "X-ray", "Xmas", "Box", "Six", "Fox"];
                    emojis = ["🎵", "📸", "🎄", "📦", "6️⃣", "🦊"];
                    translations = ["إكسيليفون", "أشعة إكس", "كريسماس", "صندوق", "ستة", "ثعلب"];
                    break;
                case 'Y':
                    words = ["Yoyo", "Yacht", "Yogurt", "Yellow", "Yak", "Yarn"];
                    emojis = ["🪀", "🚤", "🥛", "🟡", "🐂", "🧶"];
                    translations = ["يويو", "يخت", "زبادي", "أصفر", "ياك", "خيط"];
                    break;
                case 'Z':
                    words = ["Zebra", "Zoo", "Zero", "Zipper", "Zigzag", "Zoom"];
                    emojis = ["🦓", "🐅", "0️⃣", "🤐", "⚡", "🔍"];
                    translations = ["حمار وحشي", "حديقة حيوانات", "صفر", "سحاب", "متعرج", "تكبير"];
                    break;
                default:
                    words = ["Apple", "Ant", "Airplane", "Arrow", "Astronaut", "Alligator"];
                    emojis = ["🍎", "🐜", "✈️", "🏹", "🧑‍🚀", "🐊"];
                    translations = ["تفاحة", "نملة", "طائرة", "سهم", "رائد فضاء", "تمساح"];
            }
            
            LETTER_DATA[letter] = {
                words: words.map((word, index) => ({
                    word: word,
                    translation: translations[index] || word,
                    emoji: emojis[index] || "🔤",
                    sound: this.getLetterSound(letter)
                })),
                quiz: this.generateQuizForLetter(letter, words),
                sound: this.getLetterSound(letter),
                type: ["A", "E", "I", "O", "U"].includes(letter) ? "حرف متحرك" : "حرف ساكن"
            };
        });

        // مساعدات لبيانات الحروف
        function getLetterSound(letter) {
            const sounds = {
                'A': 'æ', 'B': 'b', 'C': 'k', 'D': 'd', 'E': 'e', 
                'F': 'f', 'G': 'g', 'H': 'h', 'I': 'ɪ', 'J': 'dʒ',
                'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'O': 'ɒ',
                'P': 'p', 'Q': 'kw', 'R': 'r', 'S': 's', 'T': 't',
                'U': 'ʌ', 'V': 'v', 'W': 'w', 'X': 'ks', 'Y': 'j', 'Z': 'z'
            };
            return sounds[letter] || 'æ';
        }

        function generateQuizForLetter(letter, words) {
            return [
                {
                    question: `ما هو الصوت الأساسي للحرف ${letter}؟`,
                    options: [
                        `/${getLetterSound(letter)}/ كما في ${words[0]}`,
                        "/ɑ:/ كما في Arm",
                        "/eɪ/ كما في Ace",
                        "/ɪ/ كما في Ink"
                    ],
                    correct: 0
                },
                {
                    question: `أي من هذه الكلمات تبدأ بالحرف ${letter}؟`,
                    options: [words[0], "Banana", "Cat", "Dog"],
                    correct: 0
                },
                {
                    question: `ما هو شكل الحرف ${letter} الصغير؟`,
                    options: [letter, letter.toLowerCase(), "α", letter.toLowerCase() + letter.toLowerCase()],
                    correct: 1
                },
                {
                    question: `أي من هذه الصور تبدأ بالحرف ${letter}؟`,
                    options: ["🍎", "🐶", "🏠", "🚗"],
                    correct: 0
                },
                {
                    question: `ما نوع الحرف ${letter}؟`,
                    options: [
                        "حرف متحرك (Vowel)",
                        "حرف ساكن (Consonant)",
                        "رقم",
                        "رمز"
                    ],
                    correct: ["A", "E", "I", "O", "U"].includes(letter) ? 0 : 1
                },
                {
                    question: `أي كلمة تحتوي على الحرف ${letter} في المنتصف؟`,
                    options: ["Cat", words[0], "Ant", "Egg"],
                    correct: 0
                }
            ];
        }

        // التطبيق الرئيسي المحسن
        class PhonicsGameLab {
            constructor() {
                this.currentLetterIndex = 0;
                this.currentQuizIndex = 0;
                this.quizScore = 0;
                this.writingScore = 0;
                this.wordsScore = 0;
                this.completedLetters = JSON.parse(localStorage.getItem('completedLetters')) || [];
                this.unlockedLetters = JSON.parse(localStorage.getItem('unlockedLetters')) || [0];
                this.studentName = localStorage.getItem('studentName') || '';
                this.currentGame = null;
                this.isNightMode = localStorage.getItem('nightMode') === 'true';
                this.gameInterval = null;
                this.gameTimeLeft = 60;
                this.soundEnabled = localStorage.getItem('soundEnabled') !== 'false';
                this.speechRecognition = null;
                this.isListening = false;
                this.micPermissionGranted = false;
                this.audioContext = null;
                this.analyser = null;
                this.microphone = null;
                this.audioStream = null;
                this.soundManager = new BritishSoundManager();
                this.soundManager.isSpeakingEnabled = this.soundEnabled;
                this.gameStats = {
                    successCount: 0,
                    totalAttempts: 0,
                    accuracy: 0,
                    difficulty: 1,
                    gameWins: 0
                };
                this.isPaused = false;
                this.touchControls = {
                    left: false,
                    right: false,
                    up: false,
                    down: false,
                    action: false
                };
                this.quizCompletedFlag = false;
                this.isAnswerSelected = false;
                this.currentQuizAnswer = null;
                this.quizTimeout = null;
                this.gameObjects = [];
                this.gameAnimationFrame = null;
                
                this.init();
            }
            
            init() {
                this.cacheDOM();
                this.bindEvents();
                this.renderLettersNav();
                this.loadLetter(this.currentLetterIndex);
                this.updateProgress();
                this.setupScrollTop();
                this.setupTheme();
                this.renderAchievements();
                this.setupLetterJumpMenu();
                
                if (this.studentName) {
                    document.getElementById('studentName').value = this.studentName;
                }
                
                if (this.completedLetters.length === LETTERS.length) {
                    this.showCompletionAnimation();
                }
                
                this.setupSpeechRecognition();
                this.setupAudioVisualizer();
                this.checkMicrophonePermission();
                this.setupTouchControls();
                
                // تهيئة مدير الصوت البريطاني
                this.soundManager.initialize();
                
                // تعطيل النسخ واللصق
                this.disableCopyPaste();
            }
            
            cacheDOM() {
                this.lettersNav = document.getElementById('lettersNav');
                this.currentLetterEl = document.getElementById('currentLetter');
                this.letterUpperEl = document.getElementById('letterUpper');
                this.letterLowerEl = document.getElementById('letterLower');
                this.letterForWordsEl = document.getElementById('letterForWords');
                this.wordsGrid = document.getElementById('wordsGrid');
                this.capitalWriting = document.getElementById('capitalWriting');
                this.smallWriting = document.getElementById('smallWriting');
                this.wordWritingList = document.getElementById('wordWritingList');
                this.quizQuestion = document.getElementById('quizQuestion');
                this.quizOptions = document.getElementById('quizOptions');
                this.questionNumberEl = document.getElementById('questionNumber');
                this.quizScoreEl = document.getElementById('quizScore');
                this.writingScoreEl = document.getElementById('writingScore');
                this.wordsScoreEl = document.getElementById('wordsScore');
                this.testScoreEl = document.getElementById('testScore');
                this.totalScoreEl = document.getElementById('totalScore');
                this.progressValueEl = document.getElementById('progressValue');
                this.progressBar = document.getElementById('progressBar');
                this.achievementsContainer = document.getElementById('achievementsContainer');
                this.quizNextBtn = document.getElementById('quizNextBtn');
                this.quizNavigation = document.getElementById('quizNavigation');
                
                this.playLetterBtn = document.getElementById('playLetter');
                this.letterInfoBtn = document.getElementById('letterInfo');
                this.resetLetterBtn = document.getElementById('resetLetter');
                this.prevLetterBtn = document.getElementById('prevLetter');
                this.finishLetterBtn = document.getElementById('finishLetter');
                this.studentNameInput = document.getElementById('studentName');
                this.themeToggle = document.getElementById('themeToggle');
                
                this.hamburger = document.querySelector('.hamburger');
                this.dropdownContent = document.querySelector('.dropdown-content');
                this.resetProgressBtn = document.getElementById('resetProgress');
                this.viewAllLettersBtn = document.getElementById('viewAllLetters');
                this.viewCertificateBtn = document.getElementById('viewCertificate');
                this.toggleSoundBtn = document.getElementById('toggleSound');
                this.testMicrophoneBtn = document.getElementById('testMicrophone');
                this.jumpToLetterBtn = document.getElementById('jumpToLetter');
                
                this.motivationModal = document.getElementById('motivationModal');
                this.gameModal = document.getElementById('gameModal');
                this.winModal = document.getElementById('winModal');
                this.certificateModal = document.getElementById('certificateModal');
                this.closeMotivationBtn = document.getElementById('closeMotivation');
                this.closeGameBtn = document.getElementById('closeGame');
                this.closeWinBtn = document.getElementById('closeWin');
                this.nextLetterBtn = document.getElementById('nextLetter');
                this.playGamesBtn = document.getElementById('playGames');
                this.motivationTitle = document.getElementById('motivationTitle');
                this.motivationSubtitle = document.getElementById('motivationSubtitle');
                this.motivationQuote = document.getElementById('motivationQuote');
                this.gamesGrid = document.getElementById('gamesGrid');
                
                this.gameCanvas = document.getElementById('gameCanvas');
                this.gameScoreEl = document.getElementById('gameScore');
                this.gameTimerEl = document.getElementById('gameTimer');
                this.gameTitle = document.getElementById('gameTitle');
                this.gameInstructions = document.getElementById('gameInstructions');
                this.touchControlsEl = document.getElementById('touchControls');
                this.gameControlsEl = document.getElementById('gameControls');
                this.restartGameBtn = document.getElementById('restartGame');
                this.pauseGameBtn = document.getElementById('pauseGame');
                this.backToSelectionBtn = document.getElementById('backToSelection');
                this.successCountEl = document.getElementById('successCount');
                this.difficultyLevelEl = document.getElementById('difficultyLevel');
                this.accuracyEl = document.getElementById('accuracy');
                this.gameStatsEl = document.getElementById('gameStats');
                
                this.winTitle = document.getElementById('winTitle');
                this.winSubtitle = document.getElementById('winSubtitle');
                this.winQuote = document.getElementById('winQuote');
                this.winAnimation = document.getElementById('winAnimation');
                this.finalScoreEl = document.getElementById('finalScore');
                this.finalTimeEl = document.getElementById('finalTime');
                this.finalAccuracyEl = document.getElementById('finalAccuracy');
                this.playAgainBtn = document.getElementById('playAgain');
                this.backToGamesBtn = document.getElementById('backToGames');
                
                this.certificateName = document.getElementById('certificateName');
                this.certificateDate = document.getElementById('certificateDate');
                this.printCertificateBtn = document.getElementById('printCertificate');
                this.closeCertificateBtn = document.getElementById('closeCertificate');
                
                this.completionAnimation = document.getElementById('completionAnimation');
                this.scrollTopBtn = document.getElementById('scrollTop');
                this.micStatus = document.getElementById('micStatus');
                this.micStatusText = document.getElementById('micStatusText');
                this.letterJumpMenu = document.getElementById('letterJumpMenu');
                this.toast = document.getElementById('toast');
            }
            
            bindEvents() {
                this.playLetterBtn.addEventListener('click', () => this.speakLetter());
                this.letterInfoBtn.addEventListener('click', () => this.showLetterInfo());
                this.resetLetterBtn.addEventListener('click', () => this.resetLetter());
                this.prevLetterBtn.addEventListener('click', () => this.previousLetter());
                this.finishLetterBtn.addEventListener('click', () => this.finishLetter());
                this.themeToggle.addEventListener('click', () => this.toggleTheme());
                
                this.hamburger.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.dropdownContent.classList.toggle('show');
                });
                
                this.resetProgressBtn.addEventListener('click', () => {
                    if (confirm('هل أنت متأكد من إعادة التقدم؟ سيتم حذف جميع إنجازاتك.')) {
                        localStorage.clear();
                        location.reload();
                    }
                    this.dropdownContent.classList.remove('show');
                });
                
                this.viewAllLettersBtn.addEventListener('click', () => {
                    document.getElementById('lettersNav').scrollIntoView({ behavior: 'smooth' });
                    this.dropdownContent.classList.remove('show');
                });
                
                this.jumpToLetterBtn.addEventListener('click', () => {
                    this.toggleLetterJumpMenu();
                    this.dropdownContent.classList.remove('show');
                });
                
                this.viewCertificateBtn.addEventListener('click', () => {
                    if (this.completedLetters.length === LETTERS.length) {
                        this.showCertificate();
                    } else {
                        alert('لم تكتمل جميع الحروف بعد!');
                    }
                    this.dropdownContent.classList.remove('show');
                });
                
                this.toggleSoundBtn.addEventListener('click', () => {
                    this.soundEnabled = !this.soundEnabled;
                    this.soundManager.isSpeakingEnabled = this.soundEnabled;
                    localStorage.setItem('soundEnabled', this.soundEnabled);
                    this.toggleSoundBtn.innerHTML = this.soundEnabled ? 
                        '🔊 إيقاف الصوت' : '🔇 تشغيل الصوت';
                    this.dropdownContent.classList.remove('show');
                });
                
                this.testMicrophoneBtn.addEventListener('click', () => {
                    this.testMicrophone();
                    this.dropdownContent.classList.remove('show');
                });
                
                document.addEventListener('click', (e) => {
                    if (!e.target.closest('.mobile-menu')) {
                        this.dropdownContent.classList.remove('show');
                    }
                    if (!e.target.closest('#letterJumpMenu') && !e.target.closest('#jumpToLetter')) {
                        this.letterJumpMenu.classList.remove('show');
                    }
                });
                
                this.studentNameInput.addEventListener('input', (e) => {
                    this.studentName = e.target.value;
                    localStorage.setItem('studentName', this.studentName);
                });
                
                this.closeMotivationBtn.addEventListener('click', () => this.motivationModal.style.display = 'none');
                this.closeGameBtn.addEventListener('click', () => this.closeGame());
                this.closeWinBtn.addEventListener('click', () => this.winModal.style.display = 'none');
                this.nextLetterBtn.addEventListener('click', () => this.nextLetter());
                this.playGamesBtn.addEventListener('click', () => this.showGames());
                this.closeCertificateBtn.addEventListener('click', () => this.certificateModal.style.display = 'none');
                this.printCertificateBtn.addEventListener('click', () => this.printCertificate());
                this.restartGameBtn.addEventListener('click', () => this.restartGame());
                this.pauseGameBtn.addEventListener('click', () => this.togglePause());
                this.backToSelectionBtn.addEventListener('click', () => this.backToGames());
                this.playAgainBtn.addEventListener('click', () => this.playAgain());
                this.backToGamesBtn.addEventListener('click', () => this.backToGames());
                
                this.gamesGrid.addEventListener('click', (e) => {
                    const gameCard = e.target.closest('.game-card');
                    if (gameCard && !gameCard.classList.contains('locked')) {
                        const gameType = gameCard.dataset.game;
                        this.startGame(gameType);
                    }
                });
                
                this.quizNextBtn.addEventListener('click', () => this.nextQuizQuestion());
                
                window.addEventListener('click', (e) => {
                    if (e.target === this.motivationModal) {
                        this.motivationModal.style.display = 'none';
                    }
                    if (e.target === this.gameModal) {
                        this.closeGame();
                    }
                    if (e.target === this.winModal) {
                        this.winModal.style.display = 'none';
                    }
                    if (e.target === this.certificateModal) {
                        this.certificateModal.style.display = 'none';
                    }
                });
                
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') {
                        this.closeGame();
                    }
                });
            }
            
            setupTheme() {
                if (this.isNightMode) {
                    document.body.classList.add('night-mode');
                    this.themeToggle.innerHTML = '<i class="fas fa-sun"></i><span>الوضع النهاري</span>';
                } else {
                    document.body.classList.remove('night-mode');
                    this.themeToggle.innerHTML = '<i class="fas fa-moon"></i><span>الوضع الليلي</span>';
                }
            }
            
            toggleTheme() {
                this.isNightMode = !this.isNightMode;
                localStorage.setItem('nightMode', this.isNightMode);
                this.setupTheme();
            }
            
            setupSpeechRecognition() {
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    this.speechRecognition = new SpeechRecognition();
                    this.speechRecognition.continuous = false;
                    this.speechRecognition.interimResults = false;
                    this.speechRecognition.lang = 'en-US';
                    this.speechRecognition.maxAlternatives = 1;
                    
                    this.speechRecognition.onstart = () => {
                        this.isListening = true;
                        this.showMicStatus('🎤 جاري الاستماع...', false);
                    };
                    
                    this.speechRecognition.onresult = (event) => {
                        const transcript = event.results[0][0].transcript.trim().toLowerCase();
                        this.showMicStatus('✅ تم الاستماع بنجاح!', false);
                        setTimeout(() => this.hideMicStatus(), 2000);
                        return transcript;
                    };
                    
                    this.speechRecognition.onerror = (event) => {
                        this.isListening = false;
                        let errorMessage = 'حدث خطأ في التعرف على الصوت';
                        
                        switch(event.error) {
                            case 'not-allowed':
                            case 'permission-denied':
                                errorMessage = 'لم يتم منح الإذن باستخدام الميكروفون';
                                this.micPermissionGranted = false;
                                break;
                            case 'no-speech':
                                errorMessage = 'لم يتم اكتشاف أي كلام';
                                break;
                            case 'audio-capture':
                                errorMessage = 'لا يوجد ميكروفون متاح';
                                break;
                            case 'network':
                                errorMessage = 'خطأ في الشبكة';
                                break;
                        }
                        
                        this.showMicStatus(`❌ ${errorMessage}`, true);
                    };
                    
                    this.speechRecognition.onend = () => {
                        this.isListening = false;
                    };
                } else {
                    this.showMicStatus('⚠️ المتصفح لا يدعم التعرف على الصوت', true);
                }
            }
            
            setupAudioVisualizer() {
                try {
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    this.analyser = this.audioContext.createAnalyser();
                    this.analyser.fftSize = 256;
                } catch (error) {
                    console.log('Audio context not supported:', error);
                }
            }
            
            async checkMicrophonePermission() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.micPermissionGranted = true;
                    stream.getTracks().forEach(track => track.stop());
                    this.showMicStatus('✅ المايكروفون جاهز للاستخدام', false);
                    setTimeout(() => this.hideMicStatus(), 3000);
                } catch (error) {
                    this.micPermissionGranted = false;
                    this.showMicStatus('❌ يرجى منح إذن المايكروفون', true);
                }
            }
            
            showMicStatus(message, isError = false) {
                if (!safeSetElementText(this.micStatusText, message)) {
                    warnOnce('Warning: micStatusText element not found');
                    return;
                }
                if (this.micStatus) {
                    this.micStatus.className = 'mic-status' + (isError ? ' error' : '');
                    this.micStatus.classList.add('show');
                }
            }
            
            hideMicStatus() {
                this.micStatus.classList.remove('show');
            }
            
            async testMicrophone() {
                if (!this.micPermissionGranted) {
                    if (!await this.requestMicrophonePermission()) {
                        return;
                    }
                }
                
                try {
                    this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        }
                    });
                    
                    this.showMicStatus('🎤 جاري اختبار المايكروفون...', false);
                    
                    if (this.audioContext) {
                        const source = this.audioContext.createMediaStreamSource(this.audioStream);
                        source.connect(this.analyser);
                        
                        const bufferLength = this.analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);
                        
                        const checkAudio = () => {
                            this.analyser.getByteFrequencyData(dataArray);
                            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                            
                            if (average > 10) {
                                this.showMicStatus('✅ المايكروفون يعمل بشكل ممتاز!', false);
                                setTimeout(() => {
                                    this.stopMicrophoneTest();
                                    this.showMicStatus('🎤 جاهز للاستخدام', false);
                                    setTimeout(() => this.hideMicStatus(), 2000);
                                }, 1000);
                            } else {
                                setTimeout(checkAudio, 100);
                            }
                        };
                        
                        setTimeout(() => {
                            this.showMicStatus('🎤 تحدث الآن...', false);
                            checkAudio();
                        }, 500);
                        
                        setTimeout(() => {
                            if (this.isListening) {
                                this.showMicStatus('⚠️ لم يتم اكتشاف صوت', true);
                                this.stopMicrophoneTest();
                            }
                        }, 5000);
                    }
                    
                } catch (error) {
                    this.showMicStatus('❌ فشل في الوصول إلى المايكروفون', true);
                }
            }
            
            stopMicrophoneTest() {
                if (this.audioStream) {
                    this.audioStream.getTracks().forEach(track => track.stop());
                    this.audioStream = null;
                }
            }
            
            async requestMicrophonePermission() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.micPermissionGranted = true;
                    stream.getTracks().forEach(track => track.stop());
                    this.showMicStatus('✅ تم منح إذن المايكروفون', false);
                    setTimeout(() => this.hideMicStatus(), 3000);
                    return true;
                } catch (error) {
                    this.showMicStatus('❌ لم يتم منح إذن المايكروفون', true);
                    return false;
                }
            }
            
            setupTouchControls() {
                const controlButtons = this.touchControlsEl.querySelectorAll('.control-btn');
                
                controlButtons.forEach(btn => {
                    const action = btn.dataset.action;
                    
                    btn.addEventListener('touchstart', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = true;
                        btn.style.transform = 'scale(0.95)';
                        this.soundManager.playSound('click');
                    });
                    
                    btn.addEventListener('touchend', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = false;
                        btn.style.transform = 'scale(1)';
                    });
                    
                    btn.addEventListener('touchcancel', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = false;
                        btn.style.transform = 'scale(1)';
                    });
                    
                    btn.addEventListener('mousedown', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = true;
                        btn.style.transform = 'scale(0.95)';
                        this.soundManager.playSound('click');
                    });
                    
                    btn.addEventListener('mouseup', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = false;
                        btn.style.transform = 'scale(1)';
                    });
                    
                    btn.addEventListener('mouseleave', (e) => {
                        e.preventDefault();
                        this.touchControls[action] = false;
                        btn.style.transform = 'scale(1)';
                    });
                });
                
                if (!('ontouchstart' in window || navigator.maxTouchPoints > 0)) {
                    this.touchControlsEl.style.display = 'none';
                }
            }
            
            setupLetterJumpMenu() {
                this.letterJumpMenu.innerHTML = '';
                
                LETTERS.forEach((letter, index) => {
                    const item = document.createElement('div');
                    item.className = 'letter-jump-item';
                    item.textContent = `${letter} - الحرف ${index + 1}`;
                    item.dataset.index = index;
                    
                    item.addEventListener('click', () => {
                        if (this.unlockedLetters.includes(index)) {
                            this.loadLetter(index);
                            this.letterJumpMenu.classList.remove('show');
                        } else {
                            alert('يجب إنهاء الحروف السابقة أولاً لفتح هذا الحرف');
                        }
                    });
                    
                    this.letterJumpMenu.appendChild(item);
                });
            }
            
            toggleLetterJumpMenu() {
                this.letterJumpMenu.classList.toggle('show');
            }
            
            renderLettersNav() {
                this.lettersNav.innerHTML = '';
                
                LETTERS.forEach((letter, index) => {
                    const tab = document.createElement('div');
                    tab.className = 'letter-tab';
                    tab.textContent = letter;
                    tab.dataset.index = index;
                    
                    if (index === this.currentLetterIndex) {
                        tab.classList.add('active');
                    }
                    
                    if (this.completedLetters.includes(index)) {
                        tab.classList.add('completed');
                    }
                    
                    if (!this.unlockedLetters.includes(index)) {
                        tab.classList.add('locked');
                    }
                    
                    tab.addEventListener('click', () => {
                        if (this.unlockedLetters.includes(index)) {
                            this.loadLetter(index);
                        } else {
                            alert('يجب إنهاء الحروف السابقة أولاً لفتح هذا الحرف');
                        }
                    });
                    
                    this.lettersNav.appendChild(tab);
                });
            }
            
            loadLetter(index) {
                this.currentLetterIndex = index;
                this.currentQuizIndex = 0;
                this.quizScore = 0;
                this.writingScore = 0;
                this.wordsScore = 0;
                this.quizCompletedFlag = false;
                this.isAnswerSelected = false;
                this.currentQuizAnswer = null;
                
                if (this.quizTimeout) {
                    clearTimeout(this.quizTimeout);
                    this.quizTimeout = null;
                }
                
                const letter = LETTERS[index];
                this.currentLetterEl.textContent = letter;
                this.letterUpperEl.textContent = letter;
                this.letterLowerEl.textContent = letter.toLowerCase();
                this.letterForWordsEl.textContent = letter;
                
                this.renderWordsGrid();
                this.renderWritingBoxes();
                this.renderWordWriting();
                this.renderQuiz();
                this.updateScores();
                this.renderLettersNav();
                this.updateProgress();
                this.renderAchievements();
                
                const quizContainer = document.querySelector('.quiz-container');
                if (quizContainer) {
                    quizContainer.classList.remove('quiz-completed');
                }
            }
            
            renderWordsGrid() {
                this.wordsGrid.innerHTML = '';
                const letterData = LETTER_DATA[LETTERS[this.currentLetterIndex]];
                
                letterData.words.forEach(wordData => {
                    const card = document.createElement('div');
                    card.className = 'word-card';
                    
                    card.innerHTML = `
                        <div class="word-emoji">${wordData.emoji}</div>
                        <div class="word-text">${wordData.word}</div>
                        <div class="word-ar">${wordData.translation}</div>
                        <div class="word-actions">
                            <button class="icon-btn play-word" title="استمع للنطق">
                                🔊
                            </button>
                            <button class="icon-btn mic-word" title="سجل نطقك">
                                🎤
                            </button>
                        </div>
                    `;
                    
                    const playBtn = card.querySelector('.play-word');
                    playBtn.addEventListener('click', () => {
                        this.speakText(wordData.word);
                    });
                    
                    const micBtn = card.querySelector('.mic-word');
                    micBtn.addEventListener('click', () => {
                        this.startSpeechRecognitionForWord(wordData.word, micBtn);
                    });
                    
                    this.wordsGrid.appendChild(card);
                });
            }
            
            renderWritingBoxes() {
                this.capitalWriting.innerHTML = '';
                this.smallWriting.innerHTML = '';
                
                const letter = LETTERS[this.currentLetterIndex];
                const lowerLetter = letter.toLowerCase();
                
                for (let i = 0; i < 10; i++) {
                    const box = document.createElement('input');
                    box.type = 'text';
                    box.className = 'writing-box';
                    box.maxLength = 1;
                    box.dataset.type = 'capital';
                    box.dataset.index = i;
                    box.placeholder = letter;
                    
                    // تعطيل النسخ واللصق
                    this.disableCopyPasteForElement(box);
                    
                    box.addEventListener('input', (e) => {
                        this.checkWritingBox(e.target, letter, true);
                    });
                    
                    box.addEventListener('focus', () => {
                        if ('ontouchstart' in window) {
                            setTimeout(() => {
                                box.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }, 100);
                        }
                    });
                    
                    this.capitalWriting.appendChild(box);
                }
                
                for (let i = 0; i < 10; i++) {
                    const box = document.createElement('input');
                    box.type = 'text';
                    box.className = 'writing-box';
                    box.maxLength = 1;
                    box.dataset.type = 'small';
                    box.dataset.index = i;
                    box.placeholder = lowerLetter;
                    
                    // تعطيل النسخ واللصق
                    this.disableCopyPasteForElement(box);
                    
                    box.addEventListener('input', (e) => {
                        this.checkWritingBox(e.target, lowerLetter, false);
                    });
                    
                    box.addEventListener('focus', () => {
                        if ('ontouchstart' in window) {
                            setTimeout(() => {
                                box.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }, 100);
                        }
                    });
                    
                    this.smallWriting.appendChild(box);
                }
            }
            
            checkWritingBox(box, expected, isCapital) {
                const userInput = box.value;
                
                // التحقق الدقيق من المطابقة
                if (userInput === expected) {
                    box.classList.add('correct');
                    box.classList.remove('incorrect');
                    this.soundManager.playSound('success');
                } else if (userInput !== '') {
                    box.classList.add('incorrect');
                    box.classList.remove('correct');
                    this.soundManager.playSound('error');
                    
                    // إظهار الرسالة المناسبة
                    if (isCapital && userInput.toLowerCase() === expected.toLowerCase()) {
                        this.showToast('الحرف الكبير يجب أن يكون كبيراً!', 2000);
                    } else if (!isCapital && userInput.toUpperCase() === expected.toUpperCase()) {
                        this.showToast('الحرف الصغير يجب أن يكون صغيراً!', 2000);
                    }
                } else {
                    box.classList.remove('correct', 'incorrect');
                }
                
                this.updateWritingScore();
            }
            
            updateWritingScore() {
                const capitalBoxes = this.capitalWriting.querySelectorAll('.writing-box');
                const smallBoxes = this.smallWriting.querySelectorAll('.writing-box');
                
                let correctCount = 0;
                
                capitalBoxes.forEach(box => {
                    if (box.classList.contains('correct')) {
                        correctCount++;
                    }
                });
                
                smallBoxes.forEach(box => {
                    if (box.classList.contains('correct')) {
                        correctCount++;
                    }
                });
                
                this.writingScore = correctCount;
                this.updateScores();
            }
            
            renderWordWriting() {
                this.wordWritingList.innerHTML = '';
                const letterData = LETTER_DATA[LETTERS[this.currentLetterIndex]];
                
                letterData.words.forEach((wordData, index) => {
                    const item = document.createElement('div');
                    item.className = 'word-writing-item';
                    
                    item.innerHTML = `
                        <div class="word-info">
                            <button class="icon-btn play-word-write" title="استمع للنطق">🔊</button>
                            <span class="word-text">${wordData.word}</span>
                        </div>
                        <div class="word-input-container">
                            <input type="text" class="word-input" data-word="${wordData.word}" placeholder="اكتب الكلمة...">
                            <button class="icon-btn mic-word-write" title="سجل نطقك">🎤</button>
                        </div>
                    `;
                    
                    const playBtn = item.querySelector('.play-word-write');
                    playBtn.addEventListener('click', () => {
                        this.speakText(wordData.word);
                    });
                    
                    const micBtn = item.querySelector('.mic-word-write');
                    const input = item.querySelector('.word-input');
                    
                    // تعطيل النسخ واللصق
                    this.disableCopyPasteForElement(input);
                    
                    micBtn.addEventListener('click', () => {
                        this.startSpeechRecognitionForWord(wordData.word, micBtn, input);
                    });
                    
                    input.addEventListener('input', (e) => {
                        this.checkWordInput(e.target, wordData.word);
                    });
                    
                    this.wordWritingList.appendChild(item);
                });
            }
            
            checkWordInput(input, expected) {
                const userInput = input.value;
                
                if (userInput === expected) {
                    input.classList.add('correct');
                    input.classList.remove('incorrect');
                    this.soundManager.playSound('success');
                } else if (userInput !== '') {
                    input.classList.add('incorrect');
                    input.classList.remove('correct');
                    this.soundManager.playSound('error');
                    
                    // التحقق من الحالة
                    if (userInput.toLowerCase() === expected.toLowerCase()) {
                        this.showToast('انتبه لحالة الحروف!', 2000);
                    }
                } else {
                    input.classList.remove('correct', 'incorrect');
                }
                
                this.updateWordsScore();
            }
            
            updateWordsScore() {
                const inputs = this.wordWritingList.querySelectorAll('.word-input');
                let correctCount = 0;
                
                inputs.forEach(input => {
                    if (input.classList.contains('correct')) {
                        correctCount++;
                    }
                });
                
                this.wordsScore = correctCount;
                this.updateScores();
            }
            
            renderQuiz() {
                const letterData = LETTER_DATA[LETTERS[this.currentLetterIndex]];
                
                if (this.currentQuizIndex >= 6) {
                    this.quizQuestion.textContent = "🎉 لقد أكملت جميع أسئلة الاختبار!";
                    this.quizOptions.innerHTML = '<div class="quiz-option" style="background-color: var(--success); color: white; cursor: default;">تم إكمال الاختبار بنجاح</div>';
                    this.questionNumberEl.textContent = "6";
                    this.quizScoreEl.textContent = this.quizScore;
                    
                    const quizContainer = document.querySelector('.quiz-container');
                    if (quizContainer) {
                        quizContainer.classList.add('quiz-completed');
                    }
                    
                    this.quizNavigation.style.display = 'none';
                    
                    return;
                }
                
                const quiz = letterData.quiz[this.currentQuizIndex];
                
                this.quizQuestion.textContent = quiz.question;
                this.quizOptions.innerHTML = '';
                this.questionNumberEl.textContent = this.currentQuizIndex + 1;
                this.quizScoreEl.textContent = this.quizScore;
                
                this.isAnswerSelected = false;
                this.currentQuizAnswer = null;
                
                this.quizNextBtn.disabled = true;
                this.quizNextBtn.style.opacity = '0.5';
                
                quiz.options.forEach((option, index) => {
                    const optionEl = document.createElement('div');
                    optionEl.className = 'quiz-option';
                    optionEl.textContent = option;
                    optionEl.dataset.index = index;
                    
                    optionEl.addEventListener('click', () => {
                        if (!this.isAnswerSelected) {
                            this.checkQuizAnswer(index, quiz.correct, optionEl);
                        }
                    });
                    
                    this.quizOptions.appendChild(optionEl);
                });
                
                this.quizNavigation.style.display = 'flex';
            }
            
            checkQuizAnswer(selected, correct, optionEl) {
                if (this.isAnswerSelected) return;
                
                this.isAnswerSelected = true;
                this.currentQuizAnswer = { selected, correct };
                
                const options = this.quizOptions.querySelectorAll('.quiz-option');
                
                if (selected === correct) {
                    optionEl.classList.add('correct');
                    this.quizScore++;
                    this.quizScoreEl.textContent = this.quizScore;
                    this.soundManager.playSound('success');
                } else {
                    optionEl.classList.add('incorrect');
                    options[correct].classList.add('correct');
                    this.soundManager.playSound('error');
                }
                
                options.forEach(opt => {
                    opt.style.pointerEvents = 'none';
                    opt.classList.add('disabled');
                });
                
                this.quizNextBtn.disabled = false;
                this.quizNextBtn.style.opacity = '1';
                
                // الانتقال التلقائي بعد 2 ثانية
                this.quizTimeout = setTimeout(() => {
                    this.nextQuizQuestion();
                }, 2000);
            }
            
            nextQuizQuestion() {
                if (this.quizTimeout) {
                    clearTimeout(this.quizTimeout);
                    this.quizTimeout = null;
                }
                
                if (this.currentQuizIndex < 5) {
                    this.currentQuizIndex++;
                    this.renderQuiz();
                } else {
                    this.currentQuizIndex = 6;
                    this.quizCompletedFlag = true;
                    this.showToast('🎉 لقد أكملت جميع أسئلة الاختبار!', 3000);
                    this.renderQuiz();
                }
            }
            
            updateScores() {
                this.writingScoreEl.textContent = `${this.writingScore}/20`;
                this.wordsScoreEl.textContent = `${this.wordsScore}/6`;
                this.testScoreEl.textContent = `${this.quizScore}/6`;
                
                const total = this.writingScore + this.wordsScore + this.quizScore;
                this.totalScoreEl.textContent = `${total}/32`;
                
                this.totalScoreEl.className = 'score-value';
                if (total >= 28) {
                    this.totalScoreEl.classList.add('high');
                } else if (total >= 20) {
                    this.totalScoreEl.classList.add('medium');
                } else {
                    this.totalScoreEl.classList.add('low');
                }
            }
            
            updateProgress() {
                const currentLetter = LETTERS[this.currentLetterIndex];
                this.progressValueEl.textContent = `الحرف ${currentLetter}`;
                
                const progress = ((this.currentLetterIndex + 1) / LETTERS.length) * 100;
                this.progressBar.style.width = `${progress}%`;
            }
            
            renderAchievements() {
                this.achievementsContainer.innerHTML = '';
                
                const achievements = [
                    { id: 'first-letter', icon: '🚀', name: 'الحرف الأول', description: 'إكمال أول حرف', unlocked: this.completedLetters.length >= 1 },
                    { id: 'five-letters', icon: '⭐', name: '5 حروف', description: 'إكمال 5 حروف', unlocked: this.completedLetters.length >= 5 },
                    { id: 'ten-letters', icon: '🏆', name: '10 حروف', description: 'إكمال 10 حروف', unlocked: this.completedLetters.length >= 10 },
                    { id: 'all-letters', icon: '👑', name: 'كل الحروف', description: 'إكمال جميع الحروف', unlocked: this.completedLetters.length === LETTERS.length }
                ];
                
                achievements.forEach(achievement => {
                    const badge = document.createElement('div');
                    badge.className = `achievement-badge ${achievement.unlocked ? '' : 'locked'}`;
                    badge.innerHTML = `
                        <span>${achievement.icon}</span>
                        <div class="tooltip">${achievement.name}<br>${achievement.description}</div>
                    `;
                    
                    this.achievementsContainer.appendChild(badge);
                });
            }
            
            showToast(message, duration = 3000) {
                // Suppress specific technical errors that might be safe to ignore or are already handled
                if (message && (
                    message.includes("Cannot set properties of null") || 
                    message.includes("setting 'textContent'") ||
                    message.includes("حدث خطأ أثناء تحميل الحرف")
                )) {
                    warnOnce('Suppressed toast error: ' + message);
                    return;
                }

                if (!safeSetElementText(this.toast, message)) {
                     warnOnce('Warning: toast element not found');
                     return;
                }
                this.toast.classList.add('show');
                
                setTimeout(() => {
                    this.toast.classList.remove('show');
                }, duration);
            }
            
            async speakLetter() {
                const letter = LETTERS[this.currentLetterIndex];
                await this.speakText(`The letter ${letter}, sound ${getLetterSound(letter)}`);
            }
            
            async speakText(text) {
                if (!this.soundEnabled) return;
                await this.soundManager.speak(text);
            }
            
            showLetterInfo() {
                const letter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[letter];
                
                const info = `
                    <div style="text-align: right; direction: rtl;">
                        <h3 style="color: var(--primary); margin-bottom: 15px;">معلومات عن الحرف ${letter}</h3>
                        <p><strong>النوع:</strong> ${letterData.type}</p>
                        <p><strong>الصوت الرئيسي:</strong> /${letterData.sound}/</p>
                        <p><strong>الحرف الكبير:</strong> ${letter}</p>
                        <p><strong>الحرف الصغير:</strong> ${letter.toLowerCase()}</p>
                        <p><strong>الكلمات الشائعة:</strong> ${letterData.words.map(w => w.word).join(', ')}</p>
                        <hr style="margin: 15px 0; border-color: var(--border);">
                        <p style="font-style: italic; color: var(--text-secondary);">
                            ${letter === 'A' || letter === 'E' || letter === 'I' || letter === 'O' || letter === 'U' ? 
                              'هذا حرف متحرك يمكن أن يكون له عدة أصوات حسب الكلمة.' : 
                              'هذا حرف ساكن له صوت أساسي.'}
                        </p>
                    </div>
                `;
                
                alert(info.replace(/<[^>]*>/g, ''));
            }
            
            async startSpeechRecognitionForWord(expectedWord, micButton, inputField = null) {
                if (!this.speechRecognition) {
                    this.showMicStatus('⚠️ المتصفح لا يدعم التعرف على الصوت', true);
                    return;
                }
                
                if (!this.micPermissionGranted) {
                    if (!await this.requestMicrophonePermission()) {
                        return;
                    }
                }
                
                micButton.classList.add('mic-active');
                micButton.disabled = true;
                
                this.speechRecognition.onresult = async (event) => {
                    const transcript = event.results[0][0].transcript.trim().toLowerCase();
                    const expected = expectedWord.toLowerCase();
                    
                    micButton.classList.remove('mic-active');
                    micButton.disabled = false;
                    
                    const similarity = this.calculateSimilarity(transcript, expected);
                    
                    if (similarity >= 0.7) {
                        if (inputField) {
                            inputField.value = expectedWord;
                            inputField.classList.add('correct');
                            inputField.classList.remove('incorrect');
                            this.updateWordsScore();
                        }
                        
                        micButton.textContent = '✅';
                        this.showMicStatus('🎉 نطق ممتاز!', false);
                        this.soundManager.playSound('success');
                        
                        setTimeout(() => {
                            micButton.textContent = '🎤';
                            this.hideMicStatus();
                        }, 2000);
                        
                        await this.speakText(expectedWord);
                    } else {
                        micButton.textContent = '❌';
                        this.showMicStatus(`⚠️ حاول مرة أخرى: ${expectedWord}`, true);
                        this.soundManager.playSound('error');
                        
                        setTimeout(() => {
                            micButton.textContent = '🎤';
                            this.hideMicStatus();
                        }, 3000);
                        
                        await this.speakText(expectedWord);
                    }
                };
                
                this.speechRecognition.onerror = (event) => {
                    micButton.classList.remove('mic-active');
                    micButton.disabled = false;
                    micButton.textContent = '🎤';
                    
                    if (event.error === 'no-speech') {
                        this.showMicStatus('⚠️ لم يتم اكتشاف أي كلام', true);
                    } else if (event.error === 'audio-capture') {
                        this.showMicStatus('❌ لا يوجد ميكروفون متاح', true);
                    } else {
                        this.showMicStatus('❌ حدث خطأ في التعرف على الصوت', true);
                    }
                    
                    setTimeout(() => this.hideMicStatus(), 3000);
                };
                
                try {
                    this.speechRecognition.start();
                } catch (error) {
                    micButton.classList.remove('mic-active');
                    micButton.disabled = false;
                    this.showMicStatus('❌ عذرًا، لا يمكن تشغيل الميكروفون', true);
                    setTimeout(() => this.hideMicStatus(), 3000);
                }
            }
            
            calculateSimilarity(str1, str2) {
                const longer = str1.length > str2.length ? str1 : str2;
                const shorter = str1.length > str2.length ? str2 : str1;
                
                if (longer.length === 0) return 1.0;
                
                const distance = this.levenshteinDistance(longer, shorter);
                return (longer.length - distance) / longer.length;
            }
            
            levenshteinDistance(str1, str2) {
                const matrix = [];
                
                for (let i = 0; i <= str2.length; i++) {
                    matrix[i] = [i];
                }
                
                for (let j = 0; j <= str1.length; j++) {
                    matrix[0][j] = j;
                }
                
                for (let i = 1; i <= str2.length; i++) {
                    for (let j = 1; j <= str1.length; j++) {
                        const cost = str1.charAt(j - 1) === str2.charAt(i - 1) ? 0 : 1;
                        matrix[i][j] = Math.min(
                            matrix[i - 1][j] + 1,
                            matrix[i][j - 1] + 1,
                            matrix[i - 1][j - 1] + cost
                        );
                    }
                }
                
                return matrix[str2.length][str1.length];
            }
            
            resetLetter() {
                if (confirm('هل تريد إعادة الحرف الحالي؟ سيتم مسح كل التقدم في هذا الحرف.')) {
                    this.loadLetter(this.currentLetterIndex);
                }
            }
            
            previousLetter() {
                if (this.currentLetterIndex > 0) {
                    this.loadLetter(this.currentLetterIndex - 1);
                }
            }
            
            finishLetter() {
                const totalScore = this.writingScore + this.wordsScore + this.quizScore;
                
                if (totalScore >= 20) {
                    if (!this.completedLetters.includes(this.currentLetterIndex)) {
                        this.completedLetters.push(this.currentLetterIndex);
                        localStorage.setItem('completedLetters', JSON.stringify(this.completedLetters));
                    }
                    
                    const nextIndex = this.currentLetterIndex + 1;
                    if (nextIndex < LETTERS.length && !this.unlockedLetters.includes(nextIndex)) {
                        this.unlockedLetters.push(nextIndex);
                        localStorage.setItem('unlockedLetters', JSON.stringify(this.unlockedLetters));
                    }
                    
                    if (this.completedLetters.length === LETTERS.length) {
                        this.showCertificate();
                        this.showCompletionAnimation();
                    } else {
                        this.showMotivationModal(totalScore);
                    }
                } else {
                    alert(`لم تحقق درجة النجاح بعد!\n\nدرجتك الحالية: ${totalScore}/32\nالحد الأدنى للنجاح: 20/32\n\nيرجى إكمال المزيد من التمارين.`);
                }
            }
            
            showMotivationModal(totalScore) {
                const letter = LETTERS[this.currentLetterIndex];
                const studentName = this.studentName || 'البطل';
                
                const fireQuotes = [
                    `🔥 ${studentName}، أنت نار في التعلم!`,
                    `🚀 ${studentName} يصعد إلى القمة بسرعة الصاروخ!`,
                    `👑 ملك/ملكة الحروف هو/هي ${studentName}!`,
                    `💫 براعة ${studentName} لا مثيل لها!`,
                    `🌟 ${studentName} يلمع كالنجوم في سماء التعلم!`,
                    `🏆 ${studentName} يحصد الجوائز واحدة تلو الأخرى!`,
                    `⚡ ${studentName} سريع التعلم كالبرق!`,
                    `🎯 ${studentName} يصيب الهدف في كل مرة!`
                ];
                
                const scoreQuotes = totalScore >= 30 ? [
                    `مذهل! ${studentName} حقق ${totalScore}/32!`,
                    `إتقان كامل! ${studentName} ممتاز!`,
                    `أداء خارق! ${studentName} في القمة!`
                ] : totalScore >= 25 ? [
                    `رائع! ${studentName} يحقق نتائج ممتازة!`,
                    `إنجاز كبير! ${studentName} يتقدم بثبات!`,
                    `ممتاز! ${studentName} على الطريق الصحيح!`
                ] : [
                    `جيد جداً! ${studentName} يكمل المهمة بنجاح!`,
                    `مثابرة رائعة! ${studentName} يستمر في التقدم!`,
                    `إنجاز مشرف! ${studentName} يبذل جهداً كبيراً!`
                ];
                
                const randomFireQuote = fireQuotes[Math.floor(Math.random() * fireQuotes.length)];
                const randomScoreQuote = scoreQuotes[Math.floor(Math.random() * scoreQuotes.length)];
                
                this.motivationTitle.textContent = "سلمت يابطل! ✨";
                this.motivationSubtitle.textContent = `لقد أتممت تعلم الحرف ${letter} بنجاح - ${randomScoreQuote}`;
                
                const quotes = [
                    "من جد وجد، ومن زرع حصد. استمر في التقدم!",
                    "العلم نور، والجهل ظلام. أنت تنير عقلك بالمعرفة!",
                    "كل حرف تتعلمه هو خطوة جديدة نحو إتقان اللغة الإنجليزية!",
                    "أنت مبدع! استمر في التعلم وسوف تصل إلى القمة!",
                    "الإصرار والعزيمة هما سر النجاح. أنت على الطريق الصحيح!",
                    "تعلم اللغة الإنجليزية يفتح لك أبواب العالم. استمر في التقدم!",
                    "النجاح هو مجموع الجهود الصغيرة المتكررة يومياً. أنت تفعلها بشكل رائع!",
                    "كلما تعلمت أكثر، كلما أصبحت أكثر ثقة. أنت رائع!"
                ];
                
                const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
                this.motivationQuote.textContent = `${randomFireQuote}\n${randomQuote}`;
                
                this.motivationModal.style.display = 'flex';
                this.soundManager.playSound('win');
            }
            
            showGames() {
                this.motivationModal.style.display = 'none';
                this.showGameSelection();
            }
            
            showGameSelection() {
                this.motivationModal.style.display = 'flex';
            }
            
            nextLetter() {
                this.motivationModal.style.display = 'none';
                
                const nextIndex = this.currentLetterIndex + 1;
                if (nextIndex < LETTERS.length) {
                    this.loadLetter(nextIndex);
                } else {
                    this.showCertificate();
                }
            }
            
            // ============ نظام الألعاب المحسن ============
            
            startGame(gameType) {
                this.motivationModal.style.display = 'none';
                this.gameModal.style.display = 'flex';
                this.currentGame = gameType;
                this.gameTimeLeft = 60;
                this.gameTimerEl.textContent = this.gameTimeLeft;
                this.gameScoreEl.textContent = '0';
                
                this.gameStats = {
                    successCount: 0,
                    totalAttempts: 0,
                    accuracy: 0,
                    difficulty: Math.floor(this.completedLetters.length / 5) + 1,
                    gameWins: 0
                };
                
                this.updateGameStats();
                this.setupGameControls();
                
                // تعيين تعليمات اللعبة
                const instructions = {
                    'carRace': '🏎️ تحكم في السيارة باستخدام الأسهم أو اللمس. تجنب الحروف الخاطئة واجمع الحروف الصحيحة!',
                    'racket': '🎾 حرك المضرب باستخدام الأسهم وارتد الكرة التي تحمل الحرف الصحيح!',
                    'fishing': '🎣 اصطد الأسماك التي تحمل الحرف الصحيح وتجنب الأسماك الخاطئة!',
                    'balloons': '🎈 فرقع البالونات التي تحمل الحرف الصحيح وتجنب البالونات الخاطئة!',
                    'memory': '🧠 ابحث عن البطاقات المتطابقة التي تحمل الحرف والكلمة المناسبة!',
                    'wordsearch': '🔍 ابحث عن الكلمات التي تبدأ بالحرف الحالي في الشبكة!',
                    'typing': '⌨️ اكتب الكلمات التي تظهر بسرعة قبل نفاد الوقت!',
                    'match': '🔤 اسحب الحروف إلى الكلمات المناسبة التي تبدأ بها!'
                };
                
                this.gameInstructions.textContent = instructions[gameType] || 'استمتع باللعبة!';
                this.gameTitle.textContent = `🎮 ${this.getGameName(gameType)} - الحرف ${LETTERS[this.currentLetterIndex]}`;
                
                // تهيئة اللعبة المناسبة
                this.initGame(gameType);
                
                // بدء المؤقت
                this.gameInterval = setInterval(() => {
                    if (!this.isPaused) {
                        this.gameTimeLeft--;
                        this.gameTimerEl.textContent = this.gameTimeLeft;
                        
                        if (this.gameTimeLeft <= 0) {
                            this.endGame();
                        }
                    }
                }, 1000);
            }
            
            getGameName(gameType) {
                const names = {
                    'carRace': 'سباق السيارات',
                    'racket': 'لعبة المضرب',
                    'fishing': 'اصطياد الحرف',
                    'balloons': 'لعبة البالونات',
                    'memory': 'لعبة الذاكرة',
                    'wordsearch': 'لعبة البحث',
                    'typing': 'الكتابة السريعة',
                    'match': 'لعبة المطابقة'
                };
                return names[gameType] || 'لعبة';
            }
            
            setupGameControls() {
                if (this.currentGame === 'carRace' || this.currentGame === 'racket') {
                    this.touchControlsEl.style.display = 'flex';
                } else {
                    this.touchControlsEl.style.display = 'none';
                }
            }
            
            updateGameStats() {
                this.successCountEl.textContent = this.gameStats.successCount;
                this.difficultyLevelEl.textContent = this.gameStats.difficulty;
                
                if (this.gameStats.totalAttempts > 0) {
                    this.gameStats.accuracy = Math.round((this.gameStats.successCount / this.gameStats.totalAttempts) * 100);
                } else {
                    this.gameStats.accuracy = 0;
                }
                
                this.accuracyEl.textContent = `${this.gameStats.accuracy}%`;
            }
            
            initGame(gameType) {
                const canvas = this.gameCanvas;
                const ctx = canvas.getContext('2d');
                
                const container = canvas.parentElement;
                canvas.width = container.clientWidth;
                canvas.height = container.clientHeight;
                
                // إلغاء أي أنيميشن سابق
                if (this.gameAnimationFrame) {
                    cancelAnimationFrame(this.gameAnimationFrame);
                }
                
                // تهيئة كائنات اللعبة
                this.gameObjects = [];
                
                switch(gameType) {
                    case 'carRace':
                        this.initCarRaceGame(ctx, canvas);
                        break;
                    case 'racket':
                        this.initRacketGame(ctx, canvas);
                        break;
                    case 'fishing':
                        this.initFishingGame(ctx, canvas);
                        break;
                    case 'balloons':
                        this.initBalloonsGame(ctx, canvas);
                        break;
                    case 'memory':
                        this.initMemoryGame(ctx, canvas);
                        break;
                    case 'wordsearch':
                        this.initWordSearchGame(ctx, canvas);
                        break;
                    case 'typing':
                        this.initTypingGame(ctx, canvas);
                        break;
                    case 'match':
                        this.initMatchGame(ctx, canvas);
                        break;
                    default:
                        this.initDefaultGame(ctx, canvas);
                }
            }
            
            initCarRaceGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                
                // كائن السيارة
                const car = {
                    x: canvas.width / 2 - 25,
                    y: canvas.height - 100,
                    width: 50,
                    height: 80,
                    speed: 5,
                    color: '#4361ee',
                    draw: function() {
                        ctx.fillStyle = this.color;
                        ctx.fillRect(this.x, this.y, this.width, this.height);
                        
                        // نوافذ السيارة
                        ctx.fillStyle = '#4cc9f0';
                        ctx.fillRect(this.x + 5, this.y + 10, 15, 20);
                        ctx.fillRect(this.x + 30, this.y + 10, 15, 20);
                        
                        // عجلات
                        ctx.fillStyle = '#1e293b';
                        ctx.fillRect(this.x - 5, this.y + 60, 10, 20);
                        ctx.fillRect(this.x + this.width - 5, this.y + 60, 10, 20);
                    },
                    move: function(direction) {
                        if (direction === 'left' && this.x > 0) {
                            this.x -= this.speed;
                        }
                        if (direction === 'right' && this.x < canvas.width - this.width) {
                            this.x += this.speed;
                        }
                    }
                };
                
                // كائنات الحروف (عقبات)
                const letters = [];
                const letterData = LETTER_DATA[currentLetter];
                const allLetters = LETTERS.filter(l => l !== currentLetter);
                
                for (let i = 0; i < 20; i++) {
                    const isCorrect = Math.random() > 0.5;
                    const letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                    
                    letters.push({
                        x: Math.random() * (canvas.width - 30),
                        y: -Math.random() * 1000,
                        width: 30,
                        height: 30,
                        speed: 2 + Math.random() * 2,
                        letter: letter,
                        isCorrect: isCorrect,
                        color: isCorrect ? '#4ade80' : '#ef4444',
                        draw: function() {
                            ctx.fillStyle = this.color;
                            ctx.fillRect(this.x, this.y, this.width, this.height);
                            ctx.fillStyle = 'white';
                            ctx.font = 'bold 20px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x + this.width/2, this.y + this.height/2);
                        },
                        update: function() {
                            this.y += this.speed;
                            if (this.y > canvas.height) {
                                this.y = -50;
                                this.x = Math.random() * (canvas.width - 30);
                            }
                            
                            // اكتشاف الاصطدام
                            if (this.y + this.height > car.y &&
                                this.y < car.y + car.height &&
                                this.x + this.width > car.x &&
                                this.x < car.x + car.width) {
                                
                                if (this.isCorrect) {
                                    this.gameStats.successCount++;
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 10;
                                    this.soundManager.playSound('success');
                                } else {
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = Math.max(0, parseInt(this.gameScoreEl.textContent) - 5);
                                    this.soundManager.playSound('error');
                                }
                                
                                this.updateGameStats();
                                this.y = -50;
                                this.x = Math.random() * (canvas.width - 30);
                            }
                        }
                    });
                }
                
                // دورة اللعبة
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية الطريق
                    ctx.fillStyle = '#475569';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // خطوط الطريق
                    ctx.fillStyle = '#f1f5f9';
                    for (let i = 0; i < canvas.height; i += 40) {
                        ctx.fillRect(canvas.width/2 - 5, i, 10, 20);
                    }
                    
                    // تحريك السيارة
                    if (this.touchControls.left) car.move('left');
                    if (this.touchControls.right) car.move('right');
                    
                    // رسم وتحديث الحروف
                    letters.forEach(letter => {
                        letter.update();
                        letter.draw();
                    });
                    
                    // رسم السيارة
                    car.draw();
                    
                    // استمرار الأنيميشن
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                // بدء اللعبة
                gameLoop();
                
                // إضافة مستمعي الأحداث للوحة المفاتيح
                const keyHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = true;
                    if (e.key === 'ArrowRight') this.touchControls.right = true;
                };
                
                const keyUpHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = false;
                    if (e.key === 'ArrowRight') this.touchControls.right = false;
                };
                
                document.addEventListener('keydown', keyHandler);
                document.addEventListener('keyup', keyUpHandler);
                
                // حفظ المستمعين للإزالة لاحقاً
                this.currentKeyHandlers = { keydown: keyHandler, keyup: keyUpHandler };
            }
            
            initRacketGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                const allLetters = LETTERS.filter(l => l !== currentLetter);
                
                // المضرب
                const racket = {
                    x: canvas.width / 2 - 50,
                    y: canvas.height - 30,
                    width: 100,
                    height: 20,
                    speed: 8,
                    color: '#f72585',
                    draw: function() {
                        ctx.fillStyle = this.color;
                        ctx.fillRect(this.x, this.y, this.width, this.height);
                        ctx.fillStyle = '#4cc9f0';
                        ctx.fillRect(this.x + 10, this.y + 5, this.width - 20, 10);
                    },
                    move: function(direction) {
                        if (direction === 'left' && this.x > 0) {
                            this.x -= this.speed;
                        }
                        if (direction === 'right' && this.x < canvas.width - this.width) {
                            this.x += this.speed;
                        }
                    }
                };
                
                // الكرة
                const ball = {
                    x: canvas.width / 2,
                    y: canvas.height / 2,
                    radius: 15,
                    speedX: 3,
                    speedY: 3,
                    letter: currentLetter,
                    color: '#4361ee',
                    draw: function() {
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        ctx.fillStyle = 'white';
                        ctx.font = 'bold 16px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(this.letter, this.x, this.y);
                    },
                    update: function() {
                        this.x += this.speedX;
                        this.y += this.speedY;
                        
                        // ارتداد من الجدران
                        if (this.x - this.radius < 0 || this.x + this.radius > canvas.width) {
                            this.speedX = -this.speedX;
                        }
                        if (this.y - this.radius < 0) {
                            this.speedY = -this.speedY;
                        }
                        
                        // ارتداد من المضرب
                        if (this.y + this.radius > racket.y &&
                            this.y - this.radius < racket.y + racket.height &&
                            this.x + this.radius > racket.x &&
                            this.x - this.radius < racket.x + racket.width) {
                            
                            this.speedY = -Math.abs(this.speedY);
                            this.gameStats.successCount++;
                            this.gameStats.totalAttempts++;
                            this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 5;
                            this.updateGameStats();
                            this.soundManager.playSound('success');
                            
                            // تغيير الحرف بشكل عشوائي
                            const isCorrect = Math.random() > 0.3;
                            this.letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                            this.color = isCorrect ? '#4ade80' : '#ef4444';
                        }
                        
                        // فقدان الكرة
                        if (this.y - this.radius > canvas.height) {
                            this.x = canvas.width / 2;
                            this.y = canvas.height / 2;
                            this.speedX = 3 * (Math.random() > 0.5 ? 1 : -1);
                            this.speedY = 3;
                            this.gameStats.totalAttempts++;
                            this.updateGameStats();
                            this.soundManager.playSound('error');
                        }
                    }
                };
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية الملعب
                    ctx.fillStyle = '#1e293b';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // شبكة الملعب
                    ctx.strokeStyle = '#475569';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([10, 10]);
                    ctx.beginPath();
                    ctx.moveTo(canvas.width/2, 0);
                    ctx.lineTo(canvas.width/2, canvas.height);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // تحريك المضرب
                    if (this.touchControls.left) racket.move('left');
                    if (this.touchControls.right) racket.move('right');
                    
                    // تحديث ورسم الكرة
                    ball.update();
                    ball.draw();
                    
                    // رسم المضرب
                    racket.draw();
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
                
                // مستمعي الأحداث للوحة المفاتيح
                const keyHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = true;
                    if (e.key === 'ArrowRight') this.touchControls.right = true;
                };
                
                const keyUpHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = false;
                    if (e.key === 'ArrowRight') this.touchControls.right = false;
                };
                
                document.addEventListener('keydown', keyHandler);
                document.addEventListener('keyup', keyUpHandler);
                
                this.currentKeyHandlers = { keydown: keyHandler, keyup: keyUpHandler };
            }
            
            initFishingGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const allLetters = LETTERS.filter(l => l !== currentLetter);
                
                // صنارة الصيد
                const fishingRod = {
                    x: canvas.width / 2,
                    y: 50,
                    length: 150,
                    angle: 0,
                    speed: 0.05,
                    hook: {
                        x: 0,
                        y: 0,
                        radius: 10,
                        hasFish: false,
                        fish: null
                    },
                    draw: function() {
                        // رسم القصبة
                        ctx.strokeStyle = '#8b5a2b';
                        ctx.lineWidth = 5;
                        ctx.beginPath();
                        ctx.moveTo(this.x, this.y);
                        ctx.lineTo(this.hook.x, this.hook.y);
                        ctx.stroke();
                        
                        // رسم الخطاف
                        ctx.fillStyle = this.hook.hasFish ? '#4ade80' : '#1e293b';
                        ctx.beginPath();
                        ctx.arc(this.hook.x, this.hook.y, this.hook.radius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        if (this.hook.hasFish && this.hook.fish) {
                            this.hook.fish.drawAt(this.hook.x, this.hook.y);
                        }
                    },
                    update: function() {
                        this.angle += this.speed;
                        this.hook.x = this.x + Math.sin(this.angle) * this.length;
                        this.hook.y = this.y + Math.cos(this.angle) * this.length * 0.8;
                        
                        // التحكم
                        if (this.touchControls.left) this.speed = -0.08;
                        else if (this.touchControls.right) this.speed = 0.08;
                        else this.speed = this.speed > 0 ? 0.05 : -0.05;
                    }
                };
                
                // الأسماك
                const fishes = [];
                for (let i = 0; i < 15; i++) {
                    const isCorrect = Math.random() > 0.5;
                    const letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                    
                    fishes.push({
                        x: Math.random() * canvas.width,
                        y: 200 + Math.random() * (canvas.height - 300),
                        width: 40,
                        height: 20,
                        speedX: (Math.random() - 0.5) * 2,
                        speedY: (Math.random() - 0.5) * 1,
                        letter: letter,
                        isCorrect: isCorrect,
                        color: isCorrect ? '#4cc9f0' : '#ef4444',
                        isCaught: false,
                        draw: function() {
                            if (this.isCaught) return;
                            
                            ctx.fillStyle = this.color;
                            ctx.beginPath();
                            ctx.ellipse(this.x, this.y, this.width/2, this.height/2, 0, 0, Math.PI * 2);
                            ctx.fill();
                            
                            // ذيل السمكة
                            ctx.beginPath();
                            ctx.moveTo(this.x - this.width/2, this.y);
                            ctx.lineTo(this.x - this.width, this.y - this.height/2);
                            ctx.lineTo(this.x - this.width, this.y + this.height/2);
                            ctx.closePath();
                            ctx.fill();
                            
                            // عين السمكة
                            ctx.fillStyle = 'white';
                            ctx.beginPath();
                            ctx.arc(this.x + this.width/3, this.y - 3, 3, 0, Math.PI * 2);
                            ctx.fill();
                            
                            // الحرف
                            ctx.fillStyle = 'white';
                            ctx.font = 'bold 14px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x + this.width/4, this.y);
                        },
                        drawAt: function(x, y) {
                            ctx.fillStyle = this.color;
                            ctx.beginPath();
                            ctx.arc(x, y, 15, 0, Math.PI * 2);
                            ctx.fill();
                            
                            ctx.fillStyle = 'white';
                            ctx.font = 'bold 16px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, x, y);
                        },
                        update: function() {
                            if (this.isCaught) return;
                            
                            this.x += this.speedX;
                            this.y += this.speedY;
                            
                            // ارتداد من الحواف
                            if (this.x < this.width/2 || this.x > canvas.width - this.width/2) {
                                this.speedX = -this.speedX;
                            }
                            if (this.y < 200 || this.y > canvas.height - 50) {
                                this.speedY = -this.speedY;
                            }
                            
                            // اكتشاف الاصطياد
                            const dx = this.x - fishingRod.hook.x;
                            const dy = this.y - fishingRod.hook.y;
                            const distance = Math.sqrt(dx * dx + dy * dy);
                            
                            if (distance < this.width/2 + fishingRod.hook.radius && !fishingRod.hook.hasFish) {
                                this.isCaught = true;
                                fishingRod.hook.hasFish = true;
                                fishingRod.hook.fish = this;
                                
                                if (this.isCorrect) {
                                    this.gameStats.successCount++;
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 10;
                                    this.soundManager.playSound('success');
                                } else {
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = Math.max(0, parseInt(this.gameScoreEl.textContent) - 5);
                                    this.soundManager.playSound('error');
                                }
                                
                                this.updateGameStats();
                                
                                // إعادة السمكة بعد ثانية
                                setTimeout(() => {
                                    this.isCaught = false;
                                    fishingRod.hook.hasFish = false;
                                    fishingRod.hook.fish = null;
                                    this.x = Math.random() * canvas.width;
                                    this.y = 200 + Math.random() * (canvas.height - 300);
                                    const isCorrect = Math.random() > 0.5;
                                    this.letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                                    this.isCorrect = isCorrect;
                                    this.color = isCorrect ? '#4cc9f0' : '#ef4444';
                                }, 1000);
                            }
                        }
                    });
                }
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية البحر
                    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                    gradient.addColorStop(0, '#4cc9f0');
                    gradient.addColorStop(1, '#3a0ca3');
                    ctx.fillStyle = gradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // سطح الماء
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                    for (let i = 0; i < canvas.width; i += 20) {
                        ctx.beginPath();
                        ctx.arc(i, 50 + Math.sin(Date.now()/1000 + i/50) * 10, 8, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    
                    // تحديث ورسم الصنارة
                    fishingRod.update();
                    fishingRod.draw();
                    
                    // تحديث ورسم الأسماك
                    fishes.forEach(fish => {
                        fish.update();
                        fish.draw();
                    });
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
                
                // مستمعي الأحداث
                const keyHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = true;
                    if (e.key === 'ArrowRight') this.touchControls.right = true;
                };
                
                const keyUpHandler = (e) => {
                    if (e.key === 'ArrowLeft') this.touchControls.left = false;
                    if (e.key === 'ArrowRight') this.touchControls.right = false;
                };
                
                document.addEventListener('keydown', keyHandler);
                document.addEventListener('keyup', keyUpHandler);
                
                this.currentKeyHandlers = { keydown: keyHandler, keyup: keyUpHandler };
            }
            
            initBalloonsGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const allLetters = LETTERS.filter(l => l !== currentLetter);
                
                // البالونات
                const balloons = [];
                for (let i = 0; i < 20; i++) {
                    const isCorrect = Math.random() > 0.5;
                    const letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                    const colors = ['#f72585', '#4361ee', '#4cc9f0', '#4ade80', '#f59e0b'];
                    
                    balloons.push({
                        x: Math.random() * canvas.width,
                        y: canvas.height + Math.random() * 100,
                        radius: 20 + Math.random() * 20,
                        speed: 1 + Math.random() * 2,
                        color: colors[Math.floor(Math.random() * colors.length)],
                        letter: letter,
                        isCorrect: isCorrect,
                        popped: false,
                        popTime: 0,
                        draw: function() {
                            if (this.popped) {
                                // رسم تأثير الفرقعة
                                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                                for (let i = 0; i < 8; i++) {
                                    const angle = (i / 8) * Math.PI * 2;
                                    const distance = this.radius * 1.5;
                                    ctx.beginPath();
                                    ctx.arc(
                                        this.x + Math.cos(angle) * distance,
                                        this.y + Math.sin(angle) * distance,
                                        5,
                                        0,
                                        Math.PI * 2
                                    );
                                    ctx.fill();
                                }
                                return;
                            }
                            
                            // البالون
                            ctx.fillStyle = this.color;
                            ctx.beginPath();
                            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                            ctx.fill();
                            
                            // الخط
                            ctx.strokeStyle = this.color;
                            ctx.lineWidth = 2;
                            ctx.beginPath();
                            ctx.moveTo(this.x, this.y + this.radius);
                            ctx.lineTo(this.x, this.y + this.radius + 30);
                            ctx.stroke();
                            
                            // الحرف
                            ctx.fillStyle = 'white';
                            ctx.font = `bold ${this.radius/2}px Arial`;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x, this.y);
                        },
                        update: function() {
                            if (this.popped) {
                                this.popTime++;
                                if (this.popTime > 30) {
                                    this.reset();
                                }
                                return;
                            }
                            
                            this.y -= this.speed;
                            
                            if (this.y < -this.radius) {
                                this.reset();
                            }
                        },
                        reset: function() {
                            this.x = Math.random() * canvas.width;
                            this.y = canvas.height + Math.random() * 100;
                            this.popped = false;
                            this.popTime = 0;
                            const isCorrect = Math.random() > 0.5;
                            this.letter = isCorrect ? currentLetter : allLetters[Math.floor(Math.random() * allLetters.length)];
                            this.isCorrect = isCorrect;
                        },
                        checkClick: function(mouseX, mouseY) {
                            if (this.popped) return false;
                            
                            const dx = mouseX - this.x;
                            const dy = mouseY - this.y;
                            const distance = Math.sqrt(dx * dx + dy * dy);
                            
                            if (distance < this.radius) {
                                this.popped = true;
                                
                                if (this.isCorrect) {
                                    this.gameStats.successCount++;
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 10;
                                    this.soundManager.playSound('success');
                                } else {
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = Math.max(0, parseInt(this.gameScoreEl.textContent) - 5);
                                    this.soundManager.playSound('error');
                                }
                                
                                this.updateGameStats();
                                return true;
                            }
                            return false;
                        }
                    });
                }
                
                // مستمع النقر
                const clickHandler = (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    balloons.forEach(balloon => {
                        balloon.checkClick(mouseX, mouseY);
                    });
                };
                
                canvas.addEventListener('click', clickHandler);
                this.currentClickHandler = clickHandler;
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية السماء
                    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                    gradient.addColorStop(0, '#4cc9f0');
                    gradient.addColorStop(1, '#4895ef');
                    ctx.fillStyle = gradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // سحب
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                    for (let i = 0; i < 5; i++) {
                        const x = (Date.now()/1000 * 20 + i * 100) % (canvas.width + 200) - 100;
                        ctx.beginPath();
                        ctx.arc(x, 100 + i * 30, 40, 0, Math.PI * 2);
                        ctx.arc(x + 30, 90 + i * 30, 35, 0, Math.PI * 2);
                        ctx.arc(x + 60, 100 + i * 30, 40, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    
                    // تحديث ورسم البالونات
                    balloons.forEach(balloon => {
                        balloon.update();
                        balloon.draw();
                    });
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
            
            initMemoryGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                
                // إنشاء البطاقات
                const cards = [];
                const cardWidth = 80;
                const cardHeight = 100;
                const padding = 10;
                const cols = 4;
                const rows = 3;
                
                // بيانات البطاقات (حرف وكلمة)
                const cardData = [];
                for (let i = 0; i < 6; i++) {
                    cardData.push({
                        type: 'letter',
                        value: currentLetter,
                        pairId: i
                    });
                    cardData.push({
                        type: 'word',
                        value: letterData.words[i % letterData.words.length].word,
                        pairId: i
                    });
                }
                
                // خلط البطاقات
                cardData.sort(() => Math.random() - 0.5);
                
                // إنشاء كائنات البطاقات
                for (let i = 0; i < rows; i++) {
                    for (let j = 0; j < cols; j++) {
                        const index = i * cols + j;
                        if (index >= cardData.length) break;
                        
                        cards.push({
                            x: j * (cardWidth + padding) + (canvas.width - (cols * (cardWidth + padding) - padding)) / 2,
                            y: i * (cardHeight + padding) + 50,
                            width: cardWidth,
                            height: cardHeight,
                            data: cardData[index],
                            flipped: false,
                            matched: false,
                            flipTime: 0,
                            draw: function() {
                                // خلفية البطاقة
                                ctx.fillStyle = this.flipped || this.matched ? '#ffffff' : '#4361ee';
                                ctx.fillRect(this.x, this.y, this.width, this.height);
                                
                                // حدود البطاقة
                                ctx.strokeStyle = this.matched ? '#4ade80' : '#1e293b';
                                ctx.lineWidth = 2;
                                ctx.strokeRect(this.x, this.y, this.width, this.height);
                                
                                if (this.flipped || this.matched) {
                                    // محتوى البطاقة
                                    ctx.fillStyle = '#1e293b';
                                    ctx.font = this.data.type === 'letter' ? 'bold 40px Arial' : 'bold 16px Arial';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    
                                    const text = this.data.type === 'letter' ? this.data.value : this.data.value;
                                    const lines = this.data.type === 'word' ? this.wrapText(ctx, text, this.width - 20) : [text];
                                    
                                    lines.forEach((line, idx) => {
                                        ctx.fillText(
                                            line,
                                            this.x + this.width/2,
                                            this.y + this.height/2 + (idx - (lines.length-1)/2) * 20
                                        );
                                    });
                                    
                                    // نوع البطاقة
                                    ctx.fillStyle = '#475569';
                                    ctx.font = '12px Arial';
                                    ctx.fillText(
                                        this.data.type === 'letter' ? 'الحرف' : 'الكلمة',
                                        this.x + this.width/2,
                                        this.y + 15
                                    );
                                } else {
                                    // وجه البطاقة الخلفي
                                    ctx.fillStyle = '#3a0ca3';
                                    ctx.font = 'bold 24px Arial';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    ctx.fillText('?', this.x + this.width/2, this.y + this.height/2);
                                }
                            },
                            wrapText: function(ctx, text, maxWidth) {
                                const words = text.split(' ');
                                const lines = [];
                                let currentLine = words[0];
                                
                                for (let i = 1; i < words.length; i++) {
                                    const word = words[i];
                                    const width = ctx.measureText(currentLine + " " + word).width;
                                    if (width < maxWidth) {
                                        currentLine += " " + word;
                                    } else {
                                        lines.push(currentLine);
                                        currentLine = word;
                                    }
                                }
                                lines.push(currentLine);
                                return lines;
                            },
                            contains: function(x, y) {
                                return x >= this.x && x <= this.x + this.width &&
                                       y >= this.y && y <= this.y + this.height;
                            }
                        });
                    }
                }
                
                let firstCard = null;
                let secondCard = null;
                let canFlip = true;
                
                // مستمع النقر
                const clickHandler = (e) => {
                    if (!canFlip) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    const clickedCard = cards.find(card => 
                        !card.matched && !card.flipped && card.contains(mouseX, mouseY)
                    );
                    
                    if (!clickedCard) return;
                    
                    clickedCard.flipped = true;
                    this.soundManager.playSound('click');
                    
                    if (!firstCard) {
                        firstCard = clickedCard;
                    } else if (!secondCard) {
                        secondCard = clickedCard;
                        canFlip = false;
                        
                        this.gameStats.totalAttempts++;
                        
                        // التحقق من التطابق
                        if (firstCard.data.pairId === secondCard.data.pairId) {
                            firstCard.matched = true;
                            secondCard.matched = true;
                            this.gameStats.successCount++;
                            this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 20;
                            this.soundManager.playSound('success');
                            
                            // التحقق من اكتمال اللعبة
                            if (cards.every(card => card.matched)) {
                                setTimeout(() => {
                                    this.showWinGame();
                                }, 500);
                            }
                        } else {
                            this.soundManager.playSound('error');
                            setTimeout(() => {
                                firstCard.flipped = false;
                                secondCard.flipped = false;
                            }, 1000);
                        }
                        
                        setTimeout(() => {
                            firstCard = null;
                            secondCard = null;
                            canFlip = true;
                            this.updateGameStats();
                        }, 1000);
                    }
                };
                
                canvas.addEventListener('click', clickHandler);
                this.currentClickHandler = clickHandler;
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية
                    ctx.fillStyle = '#f8fafc';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // عنوان
                    ctx.fillStyle = '#1e293b';
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`لعبة الذاكرة - الحرف ${currentLetter}`, canvas.width/2, 10);
                    
                    // رسم البطاقات
                    cards.forEach(card => card.draw());
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
            
            initWordSearchGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                const words = letterData.words.map(w => w.word.toUpperCase());
                
                // إنشاء شبكة كلمات
                const gridSize = 10;
                const cellSize = 30;
                const grid = [];
                
                // تهيئة الشبكة بالحروف العشوائية
                for (let i = 0; i < gridSize; i++) {
                    grid[i] = [];
                    for (let j = 0; j < gridSize; j++) {
                        grid[i][j] = LETTERS[Math.floor(Math.random() * LETTERS.length)];
                    }
                }
                
                // وضع الكلمات في الشبكة
                const placedWords = [];
                words.forEach(word => {
                    let placed = false;
                    let attempts = 0;
                    
                    while (!placed && attempts < 100) {
                        const direction = Math.floor(Math.random() * 3); // 0: أفقياً، 1: عمودياً، 2: قطرياً
                        const row = Math.floor(Math.random() * gridSize);
                        const col = Math.floor(Math.random() * gridSize);
                        
                        if (this.canPlaceWord(grid, word, row, col, direction)) {
                            this.placeWord(grid, word, row, col, direction);
                            placedWords.push({
                                word: word,
                                row: row,
                                col: col,
                                direction: direction,
                                found: false
                            });
                            placed = true;
                        }
                        attempts++;
                    }
                });
                
                // كائنات واجهة المستخدم
                const cells = [];
                let selectedCells = [];
                
                for (let i = 0; i < gridSize; i++) {
                    for (let j = 0; j < gridSize; j++) {
                        cells.push({
                            row: i,
                            col: j,
                            x: j * cellSize + 50,
                            y: i * cellSize + 50,
                            size: cellSize,
                            letter: grid[i][j],
                            selected: false,
                            draw: function() {
                                // خلفية الخلية
                                ctx.fillStyle = this.selected ? '#4cc9f0' : '#ffffff';
                                ctx.fillRect(this.x, this.y, this.size, this.size);
                                
                                // حدود الخلية
                                ctx.strokeStyle = '#cbd5e1';
                                ctx.lineWidth = 1;
                                ctx.strokeRect(this.x, this.y, this.size, this.size);
                                
                                // الحرف
                                ctx.fillStyle = '#1e293b';
                                ctx.font = 'bold 20px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                ctx.fillText(this.letter, this.x + this.size/2, this.y + this.size/2);
                            },
                            contains: function(x, y) {
                                return x >= this.x && x <= this.x + this.size &&
                                       y >= this.y && y <= this.y + this.size;
                            }
                        });
                    }
                }
                
                let isDragging = false;
                let startCell = null;
                
                // مستمعي أحداث الماوس
                const mouseDownHandler = (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    startCell = cells.find(cell => cell.contains(mouseX, mouseY));
                    if (startCell) {
                        isDragging = true;
                        selectedCells = [startCell];
                        startCell.selected = true;
                    }
                };
                
                const mouseMoveHandler = (e) => {
                    if (!isDragging || !startCell) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    const currentCell = cells.find(cell => cell.contains(mouseX, mouseY));
                    if (currentCell && currentCell !== startCell) {
                        // تحديد الخلايا بين startCell و currentCell
                        selectedCells = this.getCellsBetween(startCell, currentCell, cells);
                        
                        // تحديث حالة التحديد
                        cells.forEach(cell => {
                            cell.selected = selectedCells.includes(cell);
                        });
                    }
                };
                
                const mouseUpHandler = (e) => {
                    if (!isDragging || selectedCells.length < 2) {
                        cells.forEach(cell => cell.selected = false);
                        isDragging = false;
                        startCell = null;
                        return;
                    }
                    
                    // استخراج الكلمة المحددة
                    const selectedWord = selectedCells.map(cell => cell.letter).join('');
                    
                    // التحقق من الكلمات
                    let foundWord = null;
                    for (const placedWord of placedWords) {
                        if (!placedWord.found && selectedWord === placedWord.word) {
                            foundWord = placedWord;
                            break;
                        }
                    }
                    
                    if (foundWord) {
                        foundWord.found = true;
                        this.gameStats.successCount++;
                        this.gameStats.totalAttempts++;
                        this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 15;
                        this.soundManager.playSound('success');
                        
                        // تلوين الخلايا التي تحتوي على الكلمة
                        const wordCells = this.getWordCells(foundWord, cells, gridSize, cellSize);
                        wordCells.forEach(cell => {
                            cell.selected = true;
                            // تغيير اللون للإشارة إلى العثور على الكلمة
                            ctx.fillStyle = '#4ade80';
                            ctx.fillRect(cell.x, cell.y, cell.size, cell.size);
                        });
                        
                        // التحقق من اكتمال جميع الكلمات
                        if (placedWords.every(w => w.found)) {
                            setTimeout(() => {
                                this.showWinGame();
                            }, 1000);
                        }
                    } else {
                        this.gameStats.totalAttempts++;
                        this.soundManager.playSound('error');
                    }
                    
                    // إعادة تعيين
                    setTimeout(() => {
                        cells.forEach(cell => cell.selected = false);
                        this.updateGameStats();
                    }, 1000);
                    
                    isDragging = false;
                    startCell = null;
                    selectedCells = [];
                };
                
                canvas.addEventListener('mousedown', mouseDownHandler);
                canvas.addEventListener('mousemove', mouseMoveHandler);
                canvas.addEventListener('mouseup', mouseUpHandler);
                
                // حفظ المستمعين
                this.currentMouseHandlers = {
                    mousedown: mouseDownHandler,
                    mousemove: mouseMoveHandler,
                    mouseup: mouseUpHandler
                };
                
                // للشاشات التي تعمل باللمس
                canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    mouseDownHandler(e.touches[0]);
                });
                
                canvas.addEventListener('touchmove', (e) => {
                    e.preventDefault();
                    mouseMoveHandler(e.touches[0]);
                });
                
                canvas.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    mouseUpHandler(e.changedTouches[0]);
                });
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية
                    ctx.fillStyle = '#f8fafc';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // عنوان
                    ctx.fillStyle = '#1e293b';
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`لعبة البحث عن الكلمات - الحرف ${currentLetter}`, canvas.width/2, 10);
                    
                    // قائمة الكلمات
                    ctx.fillStyle = '#475569';
                    ctx.font = 'bold 16px Arial';
                    ctx.textAlign = 'left';
                    placedWords.forEach((word, i) => {
                        const status = word.found ? '✅' : '🔍';
                        ctx.fillText(`${status} ${word.word}`, 50, 400 + i * 25);
                    });
                    
                    // رسم الشبكة
                    cells.forEach(cell => cell.draw());
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
            
            canPlaceWord(grid, word, row, col, direction) {
                const wordLength = word.length;
                
                // التحقق من حدود الشبكة
                switch(direction) {
                    case 0: // أفقياً
                        if (col + wordLength > grid[0].length) return false;
                        break;
                    case 1: // عمودياً
                        if (row + wordLength > grid.length) return false;
                        break;
                    case 2: // قطرياً
                        if (row + wordLength > grid.length || col + wordLength > grid[0].length) return false;
                        break;
                }
                
                // التحقق من عدم التعارض مع الحروف الموجودة
                for (let i = 0; i < wordLength; i++) {
                    let r = row, c = col;
                    
                    switch(direction) {
                        case 0: c = col + i; break;
                        case 1: r = row + i; break;
                        case 2: r = row + i; c = col + i; break;
                    }
                    
                    if (grid[r][c] !== '.' && grid[r][c] !== word[i]) {
                        return false;
                    }
                }
                
                return true;
            }
            
            placeWord(grid, word, row, col, direction) {
                for (let i = 0; i < word.length; i++) {
                    let r = row, c = col;
                    
                    switch(direction) {
                        case 0: c = col + i; break;
                        case 1: r = row + i; break;
                        case 2: r = row + i; c = col + i; break;
                    }
                    
                    grid[r][c] = word[i];
                }
            }
            
            getCellsBetween(startCell, endCell, allCells) {
                const cells = [startCell];
                
                // تحديد الاتجاه
                const rowDiff = endCell.row - startCell.row;
                const colDiff = endCell.col - startCell.col;
                
                // التأكد من أن الخلايا على خط مستقيم
                if (rowDiff !== 0 && colDiff !== 0 && Math.abs(rowDiff) !== Math.abs(colDiff)) {
                    return cells;
                }
                
                const rowStep = rowDiff === 0 ? 0 : rowDiff / Math.abs(rowDiff);
                const colStep = colDiff === 0 ? 0 : colDiff / Math.abs(colDiff);
                
                let currentRow = startCell.row + rowStep;
                let currentCol = startCell.col + colStep;
                
                while ((rowStep === 0 || (rowStep > 0 ? currentRow <= endCell.row : currentRow >= endCell.row)) &&
                       (colStep === 0 || (colStep > 0 ? currentCol <= endCell.col : currentCol >= endCell.col))) {
                    
                    const cell = allCells.find(c => c.row === currentRow && c.col === currentCol);
                    if (cell) {
                        cells.push(cell);
                    }
                    
                    currentRow += rowStep;
                    currentCol += colStep;
                }
                
                return cells;
            }
            
            getWordCells(placedWord, allCells, gridSize, cellSize) {
                const cells = [];
                const { word, row, col, direction } = placedWord;
                
                for (let i = 0; i < word.length; i++) {
                    let r = row, c = col;
                    
                    switch(direction) {
                        case 0: c = col + i; break;
                        case 1: r = row + i; break;
                        case 2: r = row + i; c = col + i; break;
                    }
                    
                    const cell = allCells.find(cell => cell.row === r && cell.col === c);
                    if (cell) {
                        cells.push(cell);
                    }
                }
                
                return cells;
            }
            
            initTypingGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                const words = letterData.words.map(w => w.word);
                
                // كلمات تسقط من الأعلى
                const fallingWords = [];
                const wordSpeed = 2;
                let currentInput = '';
                let gameActive = true;
                
                // إنشاء كلمات جديدة
                const createWord = () => {
                    const word = words[Math.floor(Math.random() * words.length)];
                    fallingWords.push({
                        word: word,
                        x: Math.random() * (canvas.width - 200) + 100,
                        y: -50,
                        speed: wordSpeed + Math.random() * 2,
                        typed: '',
                        completed: false
                    });
                };
                
                // إنشاء الكلمة الأولى
                createWord();
                
                // مستمعي لوحة المفاتيح
                const keyHandler = (e) => {
                    if (!gameActive) return;
                    
                    if (e.key.length === 1 && e.key.match(/[a-zA-Z]/)) {
                        currentInput += e.key.toLowerCase();
                        this.soundManager.playSound('click');
                        
                        // التحقق من الكلمات
                        fallingWords.forEach(fallingWord => {
                            if (!fallingWord.completed && 
                                currentInput.toLowerCase() === fallingWord.word.toLowerCase().substring(0, currentInput.length)) {
                                fallingWord.typed = currentInput;
                                
                                if (currentInput.toLowerCase() === fallingWord.word.toLowerCase()) {
                                    fallingWord.completed = true;
                                    this.gameStats.successCount++;
                                    this.gameStats.totalAttempts++;
                                    this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 10;
                                    this.soundManager.playSound('success');
                                    currentInput = '';
                                    this.updateGameStats();
                                }
                            }
                        });
                    } else if (e.key === 'Backspace') {
                        currentInput = currentInput.slice(0, -1);
                    } else if (e.key === 'Enter') {
                        currentInput = '';
                    }
                };
                
                document.addEventListener('keydown', keyHandler);
                this.currentKeyHandler = keyHandler;
                
                const gameLoop = () => {
                    if (!gameActive) return;
                    
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية
                    ctx.fillStyle = '#0f172a';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // عنوان
                    ctx.fillStyle = '#f1f5f9';
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`الكتابة السريعة - الحرف ${currentLetter}`, canvas.width/2, 10);
                    
                    // تعليمات
                    ctx.fillStyle = '#cbd5e1';
                    ctx.font = '16px Arial';
                    ctx.fillText('اكتب الكلمات قبل وصولها للأسفل!', canvas.width/2, 40);
                    
                    // إدخال المستخدم
                    ctx.fillStyle = '#4cc9f0';
                    ctx.font = 'bold 20px Arial';
                    ctx.fillText(`الإدخال: ${currentInput}`, canvas.width/2, 70);
                    
                    // تحديث ورسم الكلمات
                    fallingWords.forEach((fallingWord, index) => {
                        // تحديث الموضع
                        fallingWord.y += fallingWord.speed;
                        
                        // إذا وصلت للأسفل ولم تكتمل
                        if (fallingWord.y > canvas.height - 50 && !fallingWord.completed) {
                            this.gameStats.totalAttempts++;
                            fallingWords.splice(index, 1);
                            this.updateGameStats();
                            this.soundManager.playSound('error');
                        }
                        
                        // إذا أكملت وخرجت من الشاشة
                        if (fallingWord.y > canvas.height) {
                            fallingWords.splice(index, 1);
                        }
                        
                        // رسم الكلمة
                        const gradient = ctx.createLinearGradient(
                            fallingWord.x - 50, fallingWord.y,
                            fallingWord.x + 50, fallingWord.y + 30
                        );
                        
                        if (fallingWord.completed) {
                            gradient.addColorStop(0, '#4ade80');
                            gradient.addColorStop(1, '#22c55e');
                        } else {
                            gradient.addColorStop(0, '#f72585');
                            gradient.addColorStop(1, '#4361ee');
                        }
                        
                        ctx.fillStyle = gradient;
                        ctx.font = 'bold 24px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        
                        // الكلمة الكاملة
                        ctx.fillText(fallingWord.word, fallingWord.x, fallingWord.y);
                        
                        // الجزء المطبوع
                        if (fallingWord.typed) {
                            ctx.fillStyle = '#4cc9f0';
                            ctx.fillText(
                                fallingWord.typed,
                                fallingWord.x,
                                fallingWord.y
                            );
                        }
                    });
                    
                    // إنشاء كلمات جديدة بشكل دوري
                    if (Math.random() < 0.02 && fallingWords.length < 5) {
                        createWord();
                    }
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
            
            initMatchGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                
                // العناصر المراد مطابقتها
                const letters = [];
                const words = [];
                const matches = [];
                
                // إنشاء الحروف
                for (let i = 0; i < 6; i++) {
                    letters.push({
                        id: i,
                        letter: currentLetter,
                        x: 100,
                        y: 100 + i * 60,
                        width: 50,
                        height: 50,
                        dragging: false,
                        matched: false,
                        draw: function() {
                            ctx.fillStyle = this.matched ? '#4ade80' : '#4361ee';
                            ctx.fillRect(this.x, this.y, this.width, this.height);
                            
                            ctx.fillStyle = 'white';
                            ctx.font = 'bold 30px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x + this.width/2, this.y + this.height/2);
                        },
                        contains: function(x, y) {
                            return x >= this.x && x <= this.x + this.width &&
                                   y >= this.y && y <= this.y + this.height;
                        }
                    });
                }
                
                // إنشاء الكلمات
                letterData.words.forEach((wordData, i) => {
                    if (i < 6) {
                        words.push({
                            id: i,
                            word: wordData.word,
                            translation: wordData.translation,
                            x: canvas.width - 200,
                            y: 100 + i * 60,
                            width: 150,
                            height: 50,
                            matched: false,
                            draw: function() {
                                ctx.fillStyle = this.matched ? '#4ade80' : '#f59e0b';
                                ctx.fillRect(this.x, this.y, this.width, this.height);
                                
                                ctx.fillStyle = 'white';
                                ctx.font = 'bold 18px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                
                                const lines = this.wrapText(ctx, this.word, this.width - 20);
                                lines.forEach((line, idx) => {
                                    ctx.fillText(
                                        line,
                                        this.x + this.width/2,
                                        this.y + this.height/2 + (idx - (lines.length-1)/2) * 20
                                    );
                                });
                                
                                // الترجمة
                                ctx.fillStyle = '#cbd5e1';
                                ctx.font = '12px Arial';
                                ctx.fillText(this.translation, this.x + this.width/2, this.y + this.height + 15);
                            },
                            wrapText: function(ctx, text, maxWidth) {
                                const words = text.split(' ');
                                const lines = [];
                                let currentLine = words[0];
                                
                                for (let i = 1; i < words.length; i++) {
                                    const word = words[i];
                                    const width = ctx.measureText(currentLine + " " + word).width;
                                    if (width < maxWidth) {
                                        currentLine += " " + word;
                                    } else {
                                        lines.push(currentLine);
                                        currentLine = word;
                                    }
                                }
                                lines.push(currentLine);
                                return lines;
                            },
                            contains: function(x, y) {
                                return x >= this.x && x <= this.x + this.width &&
                                       y >= this.y && y <= this.y + this.height;
                            }
                        });
                    }
                });
                
                let draggedLetter = null;
                let offsetX = 0, offsetY = 0;
                
                // مستمعي أحداث الماوس
                const mouseDownHandler = (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    // البحث عن حرف يتم سحبه
                    for (const letter of letters) {
                        if (!letter.matched && letter.contains(mouseX, mouseY)) {
                            draggedLetter = letter;
                            draggedLetter.dragging = true;
                            offsetX = mouseX - letter.x;
                            offsetY = mouseY - letter.y;
                            break;
                        }
                    }
                };
                
                const mouseMoveHandler = (e) => {
                    if (!draggedLetter) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    draggedLetter.x = mouseX - offsetX;
                    draggedLetter.y = mouseY - offsetY;
                };
                
                const mouseUpHandler = (e) => {
                    if (!draggedLetter) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    // البحث عن تطابق
                    let matchedWord = null;
                    for (const word of words) {
                        if (!word.matched && word.contains(mouseX, mouseY)) {
                            // التحقق من أن الكلمة تبدأ بالحرف
                            if (word.word.startsWith(draggedLetter.letter)) {
                                matchedWord = word;
                                break;
                            }
                        }
                    }
                    
                    if (matchedWord) {
                        // تطابق ناجح
                        draggedLetter.matched = true;
                        matchedWord.matched = true;
                        
                        // إبقاء الحرف في مكان الكلمة
                        draggedLetter.x = matchedWord.x - 60;
                        draggedLetter.y = matchedWord.y;
                        
                        // إضافة خط للتوصيل
                        matches.push({
                            fromX: draggedLetter.x + draggedLetter.width,
                            fromY: draggedLetter.y + draggedLetter.height/2,
                            toX: matchedWord.x,
                            toY: matchedWord.y + matchedWord.height/2
                        });
                        
                        this.gameStats.successCount++;
                        this.gameStats.totalAttempts++;
                        this.gameScoreEl.textContent = parseInt(this.gameScoreEl.textContent) + 10;
                        this.soundManager.playSound('success');
                        
                        // التحقق من اكتمال جميع التطابقات
                        if (letters.every(l => l.matched)) {
                            setTimeout(() => {
                                this.showWinGame();
                            }, 1000);
                        }
                    } else {
                        // إعادة الحرف لمكانه الأصلي
                        const originalIndex = letters.findIndex(l => l.id === draggedLetter.id);
                        draggedLetter.x = 100;
                        draggedLetter.y = 100 + originalIndex * 60;
                        this.soundManager.playSound('error');
                    }
                    
                    draggedLetter.dragging = false;
                    draggedLetter = null;
                    this.updateGameStats();
                };
                
                canvas.addEventListener('mousedown', mouseDownHandler);
                canvas.addEventListener('mousemove', mouseMoveHandler);
                canvas.addEventListener('mouseup', mouseUpHandler);
                
                // حفظ المستمعين
                this.currentMouseHandlers = {
                    mousedown: mouseDownHandler,
                    mousemove: mouseMoveHandler,
                    mouseup: mouseUpHandler
                };
                
                // للشاشات التي تعمل باللمس
                canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    mouseDownHandler(e.touches[0]);
                });
                
                canvas.addEventListener('touchmove', (e) => {
                    e.preventDefault();
                    mouseMoveHandler(e.touches[0]);
                });
                
                canvas.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    mouseUpHandler(e.changedTouches[0]);
                });
                
                const gameLoop = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // خلفية
                    ctx.fillStyle = '#f8fafc';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // عنوان
                    ctx.fillStyle = '#1e293b';
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`لعبة المطابقة - الحرف ${currentLetter}`, canvas.width/2, 10);
                    
                    // تعليمات
                    ctx.fillStyle = '#475569';
                    ctx.font = '16px Arial';
                    ctx.fillText('اسحب الحرف إلى الكلمة التي تبدأ به', canvas.width/2, 40);
                    
                    // رسم خطوط التوصيل
                    ctx.strokeStyle = '#4cc9f0';
                    ctx.lineWidth = 3;
                    matches.forEach(match => {
                        ctx.beginPath();
                        ctx.moveTo(match.fromX, match.fromY);
                        ctx.lineTo(match.toX, match.toY);
                        ctx.stroke();
                    });
                    
                    // رسم الكلمات
                    words.forEach(word => word.draw());
                    
                    // رسم الحروف
                    letters.forEach(letter => letter.draw());
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
            
            initDefaultGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                
                this.gameTitle.textContent = '🎮 لعبة تعليمية';
                this.gameInstructions.textContent = 'هذه لعبة افتراضية. استمتع!';
                
                ctx.fillStyle = '#4361ee';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = 'white';
                ctx.font = 'bold 24px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`لعبة ${this.getGameName(this.currentGame)}`, canvas.width / 2, canvas.height / 2 - 30);
                ctx.fillText(`الحرف ${currentLetter}`, canvas.width / 2, canvas.height / 2 + 30);
            }
            
            showWinGame() {
                this.closeGame();
                this.showWinModal();
            }
            
            showWinModal() {
                const score = parseInt(this.gameScoreEl.textContent);
                const timeLeft = this.gameTimeLeft;
                const accuracy = this.gameStats.accuracy;
                
                this.finalScoreEl.textContent = score;
                this.finalTimeEl.textContent = timeLeft;
                this.finalAccuracyEl.textContent = `${accuracy}%`;
                
                // رسائل تحفيزية
                const winMessages = [
                    "سلمت يابطل! 🔥 أنت نجم المستقبل!",
                    "مذهل! مهاراتك لا تصدق! ✨",
                    "إتقان رائع! أنت بطل الحروف! 🏆",
                    "أداء متميز! تستحق كل التقدير! ⭐",
                    "براعة فائقة! أنت متعلم ممتاز! 💫"
                ];
                
                const fireworkEmojis = ["🎆", "🎇", "✨", "🌟", "💥", "🔥", "⭐", "⚡"];
                
                this.winTitle.textContent = winMessages[Math.floor(Math.random() * winMessages.length)];
                this.winSubtitle.textContent = `حققت ${score} نقطة بدقة ${accuracy}%`;
                this.winAnimation.textContent = fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)] + 
                                               fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)] + 
                                               fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)];
                
                this.winModal.style.display = 'flex';
                this.soundManager.playSound('fireworks');
            }
            
            endGame() {
                clearInterval(this.gameInterval);
                
                const canvas = this.gameCanvas;
                const ctx = canvas.getContext('2d');
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                gradient.addColorStop(0, '#4cc9f0');
                gradient.addColorStop(1, '#4895ef');
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = 'white';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('انتهى الوقت!', canvas.width / 2, canvas.height / 2 - 30);
                ctx.font = '24px Arial';
                ctx.fillText(`النقاط النهائية: ${this.gameScoreEl.textContent}`, canvas.width / 2, canvas.height / 2 + 30);
                
                const finalScore = parseInt(this.gameScoreEl.textContent);
                let message = 'حاول مرة أخرى!';
                if (finalScore >= 50) message = 'مذهل! أداء رائع!';
                else if (finalScore >= 30) message = 'جيد جداً!';
                else if (finalScore >= 15) message = 'ليس سيئاً!';
                
                ctx.font = '20px Arial';
                ctx.fillText(message, canvas.width / 2, canvas.height / 2 + 70);
                
                this.soundManager.playSound('success');
            }
            
            closeGame() {
                this.gameModal.style.display = 'none';
                clearInterval(this.gameInterval);
                
                if (this.gameAnimationFrame) {
                    cancelAnimationFrame(this.gameAnimationFrame);
                    this.gameAnimationFrame = null;
                }
                
                // إزالة مستمعي الأحداث
                if (this.currentKeyHandlers) {
                    document.removeEventListener('keydown', this.currentKeyHandlers.keydown);
                    document.removeEventListener('keyup', this.currentKeyHandlers.keyup);
                    this.currentKeyHandlers = null;
                }
                
                if (this.currentClickHandler) {
                    this.gameCanvas.removeEventListener('click', this.currentClickHandler);
                    this.currentClickHandler = null;
                }
                
                if (this.currentKeyHandler) {
                    document.removeEventListener('keydown', this.currentKeyHandler);
                    this.currentKeyHandler = null;
                }
                
                if (this.currentMouseHandlers) {
                    this.gameCanvas.removeEventListener('mousedown', this.currentMouseHandlers.mousedown);
                    this.gameCanvas.removeEventListener('mousemove', this.currentMouseHandlers.mousemove);
                    this.gameCanvas.removeEventListener('mouseup', this.currentMouseHandlers.mouseup);
                    this.currentMouseHandlers = null;
                }
                
                const canvas = this.gameCanvas;
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                this.isPaused = false;
                this.pauseGameBtn.innerHTML = '<span>⏸️</span> إيقاف';
            }
            
            togglePause() {
                this.isPaused = !this.isPaused;
                this.pauseGameBtn.innerHTML = this.isPaused ? 
                    '<span>▶️</span> استمرار' : 
                    '<span>⏸️</span> إيقاف';
            }
            
            restartGame() {
                this.closeGame();
                setTimeout(() => {
                    this.startGame(this.currentGame);
                }, 100);
            }
            
            playAgain() {
                this.winModal.style.display = 'none';
                this.restartGame();
            }
            
            backToGames() {
                this.winModal.style.display = 'none';
                this.closeGame();
                this.motivationModal.style.display = 'flex';
            }
            
            showCertificate() {
                const studentName = this.studentName || 'الطالب المتميز';
                const currentDate = new Date().toLocaleDateString('ar-EG', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                this.certificateName.textContent = studentName;
                this.certificateDate.textContent = `تم منح هذه الشهادة في: ${currentDate}`;
                
                this.certificateModal.style.display = 'flex';
                this.soundManager.playSound('win');
            }
            
            printCertificate() {
                const printContent = this.certificateModal.innerHTML;
                const originalContent = document.body.innerHTML;
                
                document.body.innerHTML = printContent;
                window.print();
                document.body.innerHTML = originalContent;
                
                this.bindEvents();
            }
            
            showCompletionAnimation() {
                for (let i = 0; i < 150; i++) {
                    const confetti = document.createElement('div');
                    confetti.className = 'confetti';
                    confetti.style.left = Math.random() * 100 + 'vw';
                    confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                    confetti.style.animationDelay = Math.random() * 5 + 's';
                    confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 70%, 60%)`;
                    
                    this.completionAnimation.appendChild(confetti);
                }
                
                setTimeout(() => {
                    this.completionAnimation.innerHTML = '';
                }, 7000);
            }
            
            setupScrollTop() {
                window.addEventListener('scroll', () => {
                    if (window.pageYOffset > 300) {
                        this.scrollTopBtn.classList.add('visible');
                    } else {
                        this.scrollTopBtn.classList.remove('visible');
                    }
                });
                
                this.scrollTopBtn.addEventListener('click', () => {
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                });
            }
            
            // ============ منع النسخ واللصق ============
            
            disableCopyPaste() {
                // منع النقر الأيمن
                document.addEventListener('contextmenu', (e) => {
                    if (e.target.classList.contains('writing-box') || 
                        e.target.classList.contains('word-input')) {
                        e.preventDefault();
                        this.showToast('لا يسمح بالنسخ في هذا التمرين', 2000);
                    }
                });
                
                // منع السحب
                document.addEventListener('dragstart', (e) => {
                    if (e.target.classList.contains('writing-box') || 
                        e.target.classList.contains('word-input')) {
                        e.preventDefault();
                    }
                });
            }
            
            disableCopyPasteForElement(element) {
                element.addEventListener('copy', (e) => {
                    e.preventDefault();
                    this.showToast('لا يسمح بالنسخ في هذا التمرين', 2000);
                });
                
                element.addEventListener('paste', (e) => {
                    e.preventDefault();
                    this.showToast('لا يسمح باللصق في هذا التمرين', 2000);
                });
                
                element.addEventListener('cut', (e) => {
                    e.preventDefault();
                    this.showToast('لا يسمح بالقص في هذا التمرين', 2000);
                });
                
                // منع السحب والإفلات
                element.addEventListener('dragstart', (e) => {
                    e.preventDefault();
                });
                
                element.addEventListener('drop', (e) => {
                    e.preventDefault();
                    this.showToast('لا يسمح بالسحب والإفلات في هذا التمرين', 2000);
                });
            }
        }

        // بدء التطبيق عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', () => {
            new PhonicsGameLab();
        });