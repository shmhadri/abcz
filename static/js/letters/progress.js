(function (window) {
    "use strict";

    class LettersProgressSystem {
            resolveCurrentUserIdentifier() {
                const globalIdentifier = this.detectUserIdentifierFromGlobals();
                if (globalIdentifier) {
                    return globalIdentifier;
                }

                const domIdentifier = this.detectUserIdentifierFromDOM();
                if (domIdentifier) {
                    return domIdentifier;
                }

                const storedEmail = this.normalizeIdentifier(localStorage.getItem('studentEmail'));
                if (storedEmail) {
                    return storedEmail;
                }

                return this.getOrCreateAnonymousId();
            }

            detectUserIdentifierFromGlobals() {
                const idCandidates = [
                    window.currentUserId,
                    window.currentUserID,
                    window.userId,
                    window.userID,
                    window.studentId,
                    window.studentID,
                    window.phonicsUserId,
                    window.PHONICS_USER_ID,
                    window.PHONICS_STUDENT_ID
                ];

                for (const candidate of idCandidates) {
                    const normalized = this.normalizeIdentifier(candidate);
                    if (normalized) {
                        return normalized;
                    }
                }

                const emailCandidates = [
                    window.currentUserEmail,
                    window.userEmail,
                    window.studentEmail,
                    window.phonicsUserEmail,
                    window.PHONICS_USER_EMAIL
                ];

                for (const candidate of emailCandidates) {
                    const normalized = this.normalizeIdentifier(candidate);
                    if (normalized) {
                        return normalized;
                    }
                }

                return '';
            }

            detectUserIdentifierFromDOM() {
                const metaId = document.querySelector('meta[name="phonics-user-id"], meta[name="current-user-id"], meta[name="user-id"]');
                if (metaId && metaId.content) {
                    const normalizedMetaId = this.normalizeIdentifier(metaId.content);
                    if (normalizedMetaId) {
                        return normalizedMetaId;
                    }
                }

                const metaEmail = document.querySelector('meta[name="phonics-user-email"], meta[name="current-user-email"], meta[name="user-email"]');
                if (metaEmail && metaEmail.content) {
                    const normalizedMetaEmail = this.normalizeIdentifier(metaEmail.content);
                    if (normalizedMetaEmail) {
                        return normalizedMetaEmail;
                    }
                }

                const candidateElements = [
                    document.querySelector('[data-phonics-user-id]'),
                    document.querySelector('[data-user-id]'),
                    document.querySelector('[data-student-id]'),
                    document.querySelector('[data-phonics-user-email]'),
                    document.querySelector('[data-user-email]'),
                    document.querySelector('[data-student-email]'),
                    document.body,
                    document.getElementById('phonicsApp'),
                    document.getElementById('app')
                ].filter(Boolean);

                const datasetKeys = [
                    'phonicsUserId',
                    'userId',
                    'userid',
                    'studentId',
                    'student',
                    'accountId',
                    'phonicsUserEmail',
                    'userEmail',
                    'email',
                    'studentEmail'
                ];

                const attributeKeys = [
                    'data-phonics-user-id',
                    'data-user-id',
                    'data-student-id',
                    'data-phonics-user-email',
                    'data-user-email',
                    'data-student-email'
                ];

                for (const element of candidateElements) {
                    if (!element) continue;

                    const dataset = element.dataset || {};
                    for (const key of datasetKeys) {
                        const camelKey = key.replace(/-([a-z])/g, (_, char) => char.toUpperCase());
                        const value = dataset[camelKey] ?? dataset[key] ?? dataset[key.toLowerCase()];
                        const normalized = this.normalizeIdentifier(value);
                        if (normalized) {
                            return normalized;
                        }
                    }

                    if (element.getAttribute) {
                        for (const attr of attributeKeys) {
                            const value = element.getAttribute(attr);
                            const normalized = this.normalizeIdentifier(value);
                            if (normalized) {
                                return normalized;
                            }
                        }
                    }
                }

                return '';
            }

            normalizeIdentifier(value) {
                if (value === undefined || value === null) {
                    return '';
                }

                const str = String(value).trim();
                if (!str) {
                    return '';
                }

                return str.toLowerCase().replace(/[^a-z0-9@._-]+/g, '_');
            }

            getProgressKey(identifier = null) {
                const normalized = this.normalizeIdentifier(identifier ?? this.userIdentifier);
                const finalId = normalized || this.getOrCreateAnonymousId();
                return `${this.PROGRESS_KEY_PREFIX}_${finalId}`;
            }

            getOrCreateAnonymousId() {
                const existingAnonymousId = localStorage.getItem(this.ANONYMOUS_ID_KEY);
                const normalizedExisting = this.normalizeIdentifier(existingAnonymousId);
                if (normalizedExisting) {
                    return normalizedExisting;
                }

                const newAnonymousId = `anon_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
                localStorage.setItem(this.ANONYMOUS_ID_KEY, newAnonymousId);
                return this.normalizeIdentifier(newAnonymousId);
            }

            refreshUserIdentifier() {
                const resolvedIdentifier = this.resolveCurrentUserIdentifier();
                if (!resolvedIdentifier || resolvedIdentifier === this.userIdentifier) {
                    return;
                }

                this.userIdentifier = resolvedIdentifier;
                this.progressStorageKey = this.getProgressKey();
                this.progress = this.loadProgressState();
                this.syncProgressDerivedState();

                const currentLetter = this.progress.currentLetter || 'A';
                const indexToLoad = LETTERS.indexOf(currentLetter) >= 0 ? LETTERS.indexOf(currentLetter) : 0;

                this.loadLetter(indexToLoad);
            }

            createInitialProgressState() {
                const lettersState = {};

                LETTERS.forEach((letter, index) => {
                    lettersState[letter] = {
                        unlocked: index === 0,
                        completed: false,
                        exercisesCompleted: false,
                        score: 0,
                        games: {
                            match: false,
                            balloons: false,
                            memory: false
                        },
                        // NEW: Add detailed exercise state
                        exercises: {
                            writing: {
                                capital: {}, // { 0: 'A', 1: 'a', ... }
                                small: {}
                            },
                            words: {}, // { 'apple': 'apple', 'ant': 'ant', ... }
                            quiz: {
                                answers: {}, // { 0: 1, 1: 2, ... }
                                score: 0,
                                completed: false
                            }
                        }
                    };
                });

                return {
                    currentLetter: 'A',
                    letters: lettersState,
                    // NEW: Add user profile info to the main progress object
                    profile: {
                        name: '',
                        school: '',
                        phone: '',
                        parentPhone: ''
                    }
                };
            }

            loadProgressState() {
                try {
                    const stored = localStorage.getItem(this.progressStorageKey);
                    if (stored) {
                        const parsed = JSON.parse(stored);
                        if (parsed && parsed.letters) {
                            // Ensure all letters exist in parsed data
                            LETTERS.forEach(letter => {
                                if (!parsed.letters[letter]) {
                                    // If a letter is missing, create its initial state
                                    parsed.letters[letter] = this.createInitialProgressState().letters[letter];
                                } else {
                                    // Ensure games object exists and is structured correctly
                                    parsed.letters[letter].games = Object.assign(
                                        { match: false, balloons: false, memory: false },
                                        parsed.letters[letter].games || {}
                                    );
                                    // Migrate old 'matching' game key
                                    if (parsed.letters[letter].games.matching === true && parsed.letters[letter].games.match !== true) {
                                        parsed.letters[letter].games.match = true;
                                    }
                                    delete parsed.letters[letter].games.matching;

                                    // NEW: Ensure exercises structure exists
                                    if (!parsed.letters[letter].exercises) {
                                        parsed.letters[letter].exercises = this.createInitialProgressState().letters[letter].exercises;
                                    } else {
                                        // Ensure all sub-structures exist
                                        parsed.letters[letter].exercises.writing = parsed.letters[letter].exercises.writing || { capital: {}, small: {} };
                                        parsed.letters[letter].exercises.words = parsed.letters[letter].exercises.words || {};
                                        parsed.letters[letter].exercises.quiz = parsed.letters[letter].exercises.quiz || { answers: {}, score: 0, completed: false };
                                    }
                                }
                            });

                            if (!parsed.currentLetter || !LETTERS.includes(parsed.currentLetter)) {
                                parsed.currentLetter = 'A';
                            }
                            
                            // NEW: Ensure profile object exists
                            if (!parsed.profile) {
                                parsed.profile = this.createInitialProgressState().profile;
                            }

                            const migrated = this.applyLegacyProgress(parsed);
                            localStorage.setItem(this.progressStorageKey, JSON.stringify(migrated));
                            return migrated;
                        }
                    }
                } catch (error) {
                    console.warn('Failed to parse stored phonics progress. Resetting progress state.', error);
                }

                const initialState = this.createInitialProgressState();
                const migratedState = this.applyLegacyProgress(initialState);
                localStorage.setItem(this.progressStorageKey, JSON.stringify(migratedState));
                return migratedState;
            }

            applyLegacyProgress(progress) {
                if (!progress || progress._legacyMigrated) {
                    return progress;
                }

                try {
                    const legacyUnlocked = JSON.parse(localStorage.getItem('unlockedLetters') || '[]');
                    const legacyCompleted = JSON.parse(localStorage.getItem('completedLetters') || '[]');
                    const legacyGames = JSON.parse(localStorage.getItem('passedGames') || '{}');
                    const legacyCurrentIndex = parseInt(localStorage.getItem('currentLetterIndex'), 10);
                    const legacyLetterProgress = JSON.parse(localStorage.getItem('letterProgress') || '{}'); // Load old detailed progress

                    if (!Number.isNaN(legacyCurrentIndex) && LETTERS[legacyCurrentIndex]) {
                        progress.currentLetter = LETTERS[legacyCurrentIndex];
                    }


                    legacyUnlocked.forEach(index => {
                        const letter = LETTERS[index];
                        if (!letter) return;
                        const entry = this.ensureLetterRecordWithProgress(progress, letter);
                        entry.unlocked = true;
                    });

                    legacyCompleted.forEach(index => {
                        const letter = LETTERS[index];
                        if (!letter) return;
                        const entry = this.ensureLetterRecordWithProgress(progress, letter);
                        entry.completed = true;
                    });

                    Object.keys(legacyGames || {}).forEach(key => {
                        if (!key) return;
                        const normalizedLetter = key.toUpperCase();
                        if (!LETTERS.includes(normalizedLetter)) {
                            return;
                        }
                        const entry = this.ensureLetterRecordWithProgress(progress, normalizedLetter);
                        const gamesList = legacyGames[key] || [];
                        gamesList.forEach(game => {
                            if (!game) return;
                            const normalized = game === 'matching' ? 'match' : game.toLowerCase();
                            if (entry.games[normalized] === undefined) {
                                entry.games[normalized] = true;
                            } else {
                                entry.games[normalized] = true;
                            }
                        });
                    });

                    // NEW: Migrate detailed exercise progress from letterProgress
                    Object.keys(legacyLetterProgress).forEach(letter => {
                        if (!LETTERS.includes(letter)) return;
                        const entry = this.ensureLetterRecordWithProgress(progress, letter);
                        const oldData = legacyLetterProgress[letter];

                        if (oldData.writingBoxes) {
                            entry.exercises.writing.capital = oldData.writingBoxes.capital || {};
                            entry.exercises.writing.small = oldData.writingBoxes.small || {};
                        }
                        if (oldData.wordInputs) {
                            entry.exercises.words = oldData.wordInputs || {};
                        }
                        if (oldData.scores) {
                            entry.exercises.quiz.score = oldData.scores.quiz || 0;
                        }
                        if (oldData.quizCompleted) {
                            entry.exercises.quiz.completed = true;
                        }
                    });

                } catch (error) {
                    console.warn('Legacy progress migration failed:', error);
                }

                progress._legacyMigrated = true;
                // Clear all old keys
                localStorage.removeItem('currentLetterIndex');
                localStorage.removeItem('completedLetters');
                localStorage.removeItem('unlockedLetters');
                localStorage.removeItem('passedGames');
                localStorage.removeItem('phonicsUserId');
                localStorage.removeItem('letterProgress'); // Remove the old detailed progress key

                return progress;
            }

            ensureLetterRecordWithProgress(progress, letter) {
                // Ensure letters object exists
                if (!progress || typeof progress !== 'object') {
                    console.error('Invalid progress object');
                    return null;
                }
                if (!progress.letters) {
                    progress.letters = {};
                }
                
                // Initialize if missing
                if (!progress.letters[letter]) {
                    progress.letters[letter] = {
                        unlocked: letter === 'A',
                        completed: false,
                        exercisesCompleted: false,
                        score: 0,
                        games: { match: false, balloons: false, memory: false },
                        exercises: {
                            writing: { capital: {}, small: {} },
                            words: {},
                            quiz: { answers: {}, score: 0, completed: false }
                        }
                    };
                }
                
                const record = progress.letters[letter];
                
                // Repair structure for existing records - DEEP CHECK
                if (!record.games) record.games = { match: false, balloons: false, memory: false };
                if (!record.exercises) record.exercises = {};
                
                if (!record.exercises.writing) record.exercises.writing = { capital: {}, small: {} };
                if (!record.exercises.writing.capital) record.exercises.writing.capital = {};
                if (!record.exercises.writing.small) record.exercises.writing.small = {};
                
                if (!record.exercises.words) record.exercises.words = {};
                
                if (!record.exercises.quiz) record.exercises.quiz = { answers: {}, score: 0, completed: false };
                if (!record.exercises.quiz.answers) record.exercises.quiz.answers = {};
                
                // Fix legacy field name if present
                if (record.games.matching === true && record.games.match !== true) {
                    record.games.match = true;
                    delete record.games.matching;
                }

                return record;
            }

            saveProgressState() {
                localStorage.setItem(this.progressStorageKey, JSON.stringify(this.progress));
            }

            commitProgressUpdate() {
                this.syncProgressDerivedState();
                this.saveProgressState();
            }

            syncProgressDerivedState() {
                this.completedLetters = [];
                this.unlockedLetters = [];
                this.passedGames = {};

                LETTERS.forEach((letter, index) => {
                    const data = (this.progress.letters && this.progress.letters[letter]) || {};
                    const games = data.games || {};
                    const exercisesDone = data.exercisesCompleted === true;
                    const scoreReached = (data.score || 0) >= this.REQUIRED_SCORE;
                    const gamesCompleted = (this.requiredGames || []).every(game => games[game] === true);
                    const fullyCompleted = exercisesDone && scoreReached && gamesCompleted;

                    if (data.unlocked) {
                        this.unlockedLetters.push(index);
                    }

                    if (fullyCompleted) {
                        this.completedLetters.push(index);
                    }

                    if (data.completed !== fullyCompleted) {
                        data.completed = fullyCompleted;
                    }

                    const completedGames = Object.keys(games).filter(game => games[game]);
                    if (completedGames.length > 0) {
                        this.passedGames[letter] = completedGames;
                    }
                });
            }

            isLetterUnlocked(letter) {
                const data = this.progress.letters[letter];
                return !!(data && data.unlocked);
            }

            ensureLetterRecord(letter) {
                return this.ensureLetterRecordWithProgress(this.progress, letter);
            }

            markLetterCompleted(letter) {
                const entry = this.ensureLetterRecord(letter);
                if (!entry.completed) {
                    entry.completed = true;
                    this.commitProgressUpdate();
                }
                this.postProgressToBackend(letter, entry.score || this.getCurrentLetterTotalScore());
            }

            getCSRFToken() {
                const match = document.cookie.match(/(?:^|;)\s*csrftoken=([^;]+)/);
                return match ? decodeURIComponent(match[1]) : '';
            }

            normalizeScoreForBackend(frontendScore) {
                const safeScore = Math.max(0, Math.min(Number(frontendScore) || 0, this.REQUIRED_SCORE));
                return Math.round((safeScore / this.REQUIRED_SCORE) * 20);
            }

            postProgressToBackend(letter, frontendScore) {
                const student = (this.studentName || this.userIdentifier || 'Guest').trim();
                const score = this.normalizeScoreForBackend(frontendScore);

                fetch('/api/save-progress/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ student, letter, score })
                })
                .then(response => {
                    if (!response.ok) {
                        console.warn('Progress save failed:', response.status);
                    }
                })
                .catch(error => console.warn('Progress save error:', error));
            }

            markGameCompleted(letter, gameName) {
                const entry = this.ensureLetterRecord(letter);
                if (entry.games[gameName] !== true) {
                    entry.games[gameName] = true;
                    this.commitProgressUpdate();
                }
            }

            unlockLetter(letter) {
                const entry = this.ensureLetterRecord(letter);
                if (!entry.unlocked) {
                    entry.unlocked = true;
                    this.commitProgressUpdate();
                }
            }

            getMissingRequiredGames(letter) {
                const entry = this.ensureLetterRecord(letter);
                return this.requiredGames.filter(game => entry.games[game] !== true);
            }

            isLetterCompleted(letter) {
                const entry = this.ensureLetterRecord(letter);
                const games = entry.games || {};
                const passedExercises = entry.exercisesCompleted === true;
                const passedScore = (entry.score || 0) >= this.REQUIRED_SCORE;
                const passedGames = this.requiredGames.every(game => games[game] === true);
                return passedExercises && passedScore && passedGames;
            }

            updateLetterExerciseProgress(letter) {
                const entry = this.ensureLetterRecord(letter);
                const totalScore = this.getCurrentLetterTotalScore();
                const exercisesCompleted = this.areExercisesCompleted();
                const games = entry.games || {};
                const fullyCompleted = exercisesCompleted && totalScore >= this.REQUIRED_SCORE && (this.requiredGames || []).every(game => games[game] === true);

                const needsUpdate = entry.exercisesCompleted !== exercisesCompleted || (entry.score || 0) !== totalScore || entry.completed !== fullyCompleted;

                if (needsUpdate) {
                    entry.exercisesCompleted = exercisesCompleted;
                    entry.score = totalScore;
                    entry.completed = fullyCompleted;
                    this.commitProgressUpdate();
                }
            }

            areExercisesCompleted() {
                const letter = this.progress.currentLetter;
                if (!letter) return false;
                
                const staticData = LETTER_DATA[letter];
                const letterProgress = this.ensureLetterRecord(letter);

                // Check Writing (Capital + Small)
                const capitalCorrect = Object.keys(letterProgress.exercises.writing.capital || {}).length;
                const smallCorrect = Object.keys(letterProgress.exercises.writing.small || {}).length;
                const totalWriting = capitalCorrect + smallCorrect;
                const maxWritingScore = 20; // 10 capital + 10 small
                const writingComplete = totalWriting >= maxWritingScore;

                // Check Words
                const wordsCorrect = Object.keys(letterProgress.exercises.words || {}).length;
                const maxWordScore = staticData ? staticData.words.length : 10;
                const wordsComplete = wordsCorrect >= maxWordScore;

                // Check Quiz (Completed all questions, regardless of score)
                const answeredCount = Object.keys(letterProgress.exercises.quiz.answers || {}).length;
                const quizLength = staticData ? staticData.quiz.length : 6;
                const quizComplete = this.quizCompletedFlag === true || answeredCount >= quizLength;

                return writingComplete && wordsComplete && quizComplete;
            }

            getCurrentLetterTotalScore() {
                return this.writingScore + this.wordsScore + this.quizScore;
            }
            

            resetLetter() {
                if (confirm('هل تريد إعادة الحرف الحالي؟ سيتم مسح كل التقدم في هذا الحرف.')) {
                    const letter = LETTERS[this.currentLetterIndex];
                    const fresh = this.createInitialProgressState().letters[letter];
                    fresh.unlocked = true;
                    this.progress.letters[letter] = fresh;
                    this.quizScore = 0;
                    this.currentQuizIndex = 0;
                    this.quizCompletedFlag = false;
                    this.commitProgressUpdate();
                    this.loadLetter(this.currentLetterIndex);
                }
            }
            

    }

    function getCSRFToken() {
        const match = document.cookie.match(/(?:^|;)\s*csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    }

    function postProgress(letter, score, student) {
        return fetch("/api/save-progress/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                letter,
                score,
                student: student || localStorage.getItem("studentName") || localStorage.getItem("phonicsAnonymousId") || "Guest"
            })
        })
        .then(res => res.json())
        .then(result => {
            console.log("Saved:", result);
            return result;
        });
    }

    window.installLettersProgressSystem = function installLettersProgressSystem(GameClass) {
        if (!GameClass || !GameClass.prototype) return;
        Object.getOwnPropertyNames(LettersProgressSystem.prototype).forEach(name => {
            if (name !== "constructor") {
                GameClass.prototype[name] = LettersProgressSystem.prototype[name];
            }
        });
    };

    window.getCSRFToken = getCSRFToken;
    window.postProgress = postProgress;
})(window);
