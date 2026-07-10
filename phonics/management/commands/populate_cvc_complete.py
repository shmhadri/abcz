from django.core.management.base import BaseCommand
from phonics.models import CVCWord, CVCSentence, CVCStory


class Command(BaseCommand):
    help = 'Populate CVC database with words (Safe), Pronouns, and Stories'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  Starting Clean CVC Database Population'))
        self.stdout.write(self.style.SUCCESS('  (Safe Content & Rich Stories)'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # First, clear existing CVC data
        self.stdout.write('Clearing existing CVC data...')
        CVCWord.objects.all().delete()
        CVCSentence.objects.all().delete()
        CVCStory.objects.all().delete()
        
        # ===== CVC WORDS =====
        words_data = [
            # ============================================
            # SHORT A WORDS
            # ============================================
            {"word": "cat", "arabic_meaning": "قطة", "category": "animals", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 1, "image_url": "", "emoji": "🐱"},
            {"word": "bat", "arabic_meaning": "مضرب/خفاش", "category": "objects", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 2, "image_url": "", "emoji": "🦇"},
            {"word": "rat", "arabic_meaning": "فأر", "category": "animals", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 3, "image_url": "", "emoji": "🐀"},
            {"word": "hat", "arabic_meaning": "قبعة", "category": "clothes", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 4, "image_url": "", "emoji": "🎩"},
            {"word": "mat", "arabic_meaning": "سجادة", "category": "objects", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 5, "image_url": "", "emoji": "🧘"},
            {"word": "sat", "arabic_meaning": "جلس (ماضي)", "category": "verbs", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 6, "image_url": "", "emoji": "🪑"},
            {"word": "fat", "arabic_meaning": "سمين", "category": "adjectives", "word_family": "at", "vowel_sound": "a", "difficulty_level": 1, "order": 7, "image_url": "", "emoji": "🍔"},
            
            {"word": "cab", "arabic_meaning": "سيارة أجرة", "category": "transport", "word_family": "ab", "vowel_sound": "a", "difficulty_level": 1, "order": 8, "image_url": "", "emoji": "🚕"},
            {"word": "lab", "arabic_meaning": "مختبر", "category": "places", "word_family": "ab", "vowel_sound": "a", "difficulty_level": 2, "order": 12, "image_url": "", "emoji": "🧪"},
            
            {"word": "dad", "arabic_meaning": "أب/والد", "category": "people", "word_family": "ad", "vowel_sound": "a", "difficulty_level": 1, "order": 16, "image_url": "", "emoji": "👨"},
            {"word": "sad", "arabic_meaning": "حزين", "category": "adjectives", "word_family": "ad", "vowel_sound": "a", "difficulty_level": 1, "order": 21, "image_url": "", "emoji": "😢"},
            
            {"word": "bag", "arabic_meaning": "حقيبة", "category": "objects", "word_family": "ag", "vowel_sound": "a", "difficulty_level": 1, "order": 22, "image_url": "", "emoji": "🎒"},
            {"word": "tag", "arabic_meaning": "بطاقة/علامة", "category": "objects", "word_family": "ag", "vowel_sound": "a", "difficulty_level": 1, "order": 26, "image_url": "", "emoji": "🏷️"},
            
            {"word": "jam", "arabic_meaning": "مربى", "category": "food", "word_family": "am", "vowel_sound": "a", "difficulty_level": 1, "order": 31, "image_url": "", "emoji": "🍯"},
            
            {"word": "can", "arabic_meaning": "يستطيع/علبة", "category": "objects", "word_family": "an", "vowel_sound": "a", "difficulty_level": 1, "order": 35, "image_url": "", "emoji": "🥫"},
            {"word": "fan", "arabic_meaning": "مروحة/مشجع", "category": "objects", "word_family": "an", "vowel_sound": "a", "difficulty_level": 1, "order": 36, "image_url": "", "emoji": "🪭"},
            {"word": "man", "arabic_meaning": "رجل", "category": "people", "word_family": "an", "vowel_sound": "a", "difficulty_level": 1, "order": 37, "image_url": "", "emoji": "👨"},
            {"word": "pan", "arabic_meaning": "مقلاة", "category": "kitchen", "word_family": "an", "vowel_sound": "a", "difficulty_level": 1, "order": 38, "image_url": "", "emoji": "🍳"},
            {"word": "van", "arabic_meaning": "شاحنة صغيرة", "category": "transport", "word_family": "an", "vowel_sound": "a", "difficulty_level": 1, "order": 41, "image_url": "", "emoji": "🚐"},
            
            {"word": "cap", "arabic_meaning": "قبعة", "category": "clothes", "word_family": "ap", "vowel_sound": "a", "difficulty_level": 1, "order": 42, "image_url": "", "emoji": "🧢"},
            {"word": "map", "arabic_meaning": "خريطة", "category": "objects", "word_family": "ap", "vowel_sound": "a", "difficulty_level": 1, "order": 44, "image_url": "", "emoji": "🗺️"},
            {"word": "nap", "arabic_meaning": "قيلولة", "category": "verbs", "word_family": "ap", "vowel_sound": "a", "difficulty_level": 1, "order": 45, "image_url": "", "emoji": "😴"},
            {"word": "tap", "arabic_meaning": "صنبور/نقر", "category": "objects", "word_family": "ap", "vowel_sound": "a", "difficulty_level": 1, "order": 47, "image_url": "", "emoji": "🚰"},

            # ============================================
            # SHORT E WORDS
            # ============================================
            {"word": "get", "arabic_meaning": "يحصل على", "category": "verbs", "word_family": "et", "vowel_sound": "e", "difficulty_level": 1, "order": 49, "image_url": "", "emoji": "🤲"},
            {"word": "jet", "arabic_meaning": "طائرة نفاثة", "category": "transport", "word_family": "et", "vowel_sound": "e", "difficulty_level": 2, "order": 50, "image_url": "", "emoji": "✈️"},
            {"word": "net", "arabic_meaning": "شبكة", "category": "objects", "word_family": "et", "vowel_sound": "e", "difficulty_level": 1, "order": 53, "image_url": "", "emoji": "🥅"},
            {"word": "pet", "arabic_meaning": "حيوان أليف", "category": "animals", "word_family": "et", "vowel_sound": "e", "difficulty_level": 1, "order": 54, "image_url": "", "emoji": "🐕"},
            {"word": "vet", "arabic_meaning": "طبيب بيطري", "category": "people", "word_family": "et", "vowel_sound": "e", "difficulty_level": 2, "order": 56, "image_url": "", "emoji": "⚕️"},
            {"word": "wet", "arabic_meaning": "مبلل", "category": "adjectives", "word_family": "et", "vowel_sound": "e", "difficulty_level": 1, "order": 57, "image_url": "", "emoji": "💧"},
            
            {"word": "hen", "arabic_meaning": "دجاجة", "category": "animals", "word_family": "en", "vowel_sound": "e", "difficulty_level": 1, "order": 60, "image_url": "", "emoji": "🐔"},
            {"word": "men", "arabic_meaning": "رجال", "category": "people", "word_family": "en", "vowel_sound": "e", "difficulty_level": 1, "order": 61, "image_url": "", "emoji": "👥"},
            {"word": "pen", "arabic_meaning": "قلم", "category": "school", "word_family": "en", "vowel_sound": "e", "difficulty_level": 1, "order": 62, "image_url": "", "emoji": "🖊️"},
            {"word": "ten", "arabic_meaning": "عشرة", "category": "numbers", "word_family": "en", "vowel_sound": "e", "difficulty_level": 1, "order": 63, "image_url": "", "emoji": "🔟"},
            
            {"word": "bed", "arabic_meaning": "سرير", "category": "furniture", "word_family": "ed", "vowel_sound": "e", "difficulty_level": 1, "order": 64, "image_url": "", "emoji": "🛏️"},
            {"word": "red", "arabic_meaning": "أحمر", "category": "colors", "word_family": "ed", "vowel_sound": "e", "difficulty_level": 1, "order": 66, "image_url": "", "emoji": "🔴"},

            # ============================================
            # SHORT I WORDS
            # ============================================
            {"word": "hit", "arabic_meaning": "ضرب", "category": "verbs", "word_family": "it", "vowel_sound": "i", "difficulty_level": 1, "order": 69, "image_url": "", "emoji": "👊"},
            {"word": "kit", "arabic_meaning": "مجموعة أدوات", "category": "objects", "word_family": "it", "vowel_sound": "i", "difficulty_level": 2, "order": 70, "image_url": "", "emoji": "🧰"},
            {"word": "pit", "arabic_meaning": "حفرة", "category": "places", "word_family": "it", "vowel_sound": "i", "difficulty_level": 2, "order": 72, "image_url": "", "emoji": "🕳️"},
            {"word": "sit", "arabic_meaning": "يجلس", "category": "verbs", "word_family": "it", "vowel_sound": "i", "difficulty_level": 1, "order": 73, "image_url": "", "emoji": "🪑"},
            
            {"word": "big", "arabic_meaning": "كبير", "category": "adjectives", "word_family": "ig", "vowel_sound": "i", "difficulty_level": 1, "order": 74, "image_url": "", "emoji": "🐘"},
            {"word": "dig", "arabic_meaning": "يحفر", "category": "verbs", "word_family": "ig", "vowel_sound": "i", "difficulty_level": 2, "order": 75, "image_url": "", "emoji": "⛏️"},
            {"word": "fig", "arabic_meaning": "تين", "category": "food", "word_family": "ig", "vowel_sound": "i", "difficulty_level": 2, "order": 76, "image_url": "", "emoji": "🍈"},
            {"word": "wig", "arabic_meaning": "شعر مستعار", "category": "objects", "word_family": "ig", "vowel_sound": "i", "difficulty_level": 2, "order": 79, "image_url": "", "emoji": "💇"},
            
            {"word": "bin", "arabic_meaning": "صندوق", "category": "objects", "word_family": "in", "vowel_sound": "i", "difficulty_level": 2, "order": 80, "image_url": "", "emoji": "🗑️"},
            {"word": "pin", "arabic_meaning": "دبوس", "category": "objects", "word_family": "in", "vowel_sound": "i", "difficulty_level": 1, "order": 83, "image_url": "", "emoji": "📍"},
            {"word": "tin", "arabic_meaning": "قصدير", "category": "objects", "word_family": "in", "vowel_sound": "i", "difficulty_level": 2, "order": 84, "image_url": "", "emoji": "🥫"},
            {"word": "win", "arabic_meaning": "يفوز", "category": "verbs", "word_family": "in", "vowel_sound": "i", "difficulty_level": 1, "order": 85, "image_url": "", "emoji": "🏆"},
            
            {"word": "lip", "arabic_meaning": "شفة", "category": "body", "word_family": "ip", "vowel_sound": "i", "difficulty_level": 1, "order": 86, "image_url": "", "emoji": "👄"},
            {"word": "tip", "arabic_meaning": "طرف/إكرامية", "category": "objects", "word_family": "ip", "vowel_sound": "i", "difficulty_level": 1, "order": 88, "image_url": "", "emoji": "💡"},
            {"word": "sip", "arabic_meaning": "يرشف", "category": "verbs", "word_family": "ip", "vowel_sound": "i", "difficulty_level": 2, "order": 89, "image_url": "", "emoji": "🥤"},

            # ============================================
            # SHORT O WORDS
            # ============================================
            {"word": "dot", "arabic_meaning": "نقطة", "category": "objects", "word_family": "ot", "vowel_sound": "o", "difficulty_level": 1, "order": 91, "image_url": "", "emoji": "⏺️"},
            {"word": "hot", "arabic_meaning": "حار", "category": "adjectives", "word_family": "ot", "vowel_sound": "o", "difficulty_level": 1, "order": 93, "image_url": "", "emoji": "🔥"},
            {"word": "pot", "arabic_meaning": "قدر", "category": "kitchen", "word_family": "ot", "vowel_sound": "o", "difficulty_level": 1, "order": 96, "image_url": "", "emoji": "🍲"},
            
            {"word": "dog", "arabic_meaning": "كلب", "category": "animals", "word_family": "og", "vowel_sound": "o", "difficulty_level": 1, "order": 98, "image_url": "", "emoji": "🐶"},
            {"word": "fog", "arabic_meaning": "ضباب", "category": "weather", "word_family": "og", "vowel_sound": "o", "difficulty_level": 2, "order": 99, "image_url": "", "emoji": "🌫️"},
            {"word": "log", "arabic_meaning": "جذع شجرة", "category": "nature", "word_family": "og", "vowel_sound": "o", "difficulty_level": 1, "order": 101, "image_url": "", "emoji": "🪵"},
            
            {"word": "hop", "arabic_meaning": "يقفز", "category": "verbs", "word_family": "op", "vowel_sound": "o", "difficulty_level": 1, "order": 102, "image_url": "", "emoji": "🐇"},
            {"word": "mop", "arabic_meaning": "ممسحة", "category": "objects", "word_family": "op", "vowel_sound": "o", "difficulty_level": 1, "order": 103, "image_url": "", "emoji": "🧹"},
            {"word": "top", "arabic_meaning": "قمة/أعلى", "category": "adjectives", "word_family": "op", "vowel_sound": "o", "difficulty_level": 1, "order": 104, "image_url": "", "emoji": "🔝"},
            
            {"word": "box", "arabic_meaning": "صندوق", "category": "objects", "word_family": "ox", "vowel_sound": "o", "difficulty_level": 1, "order": 105, "image_url": "", "emoji": "📦"},
            {"word": "fox", "arabic_meaning": "ثعلب", "category": "animals", "word_family": "ox", "vowel_sound": "o", "difficulty_level": 2, "order": 106, "image_url": "", "emoji": "🦊"},

            # ============================================
            # SHORT U WORDS
            # ============================================
            {"word": "bug", "arabic_meaning": "حشرة", "category": "animals", "word_family": "ug", "vowel_sound": "u", "difficulty_level": 1, "order": 108, "image_url": "", "emoji": "🐛"},
            {"word": "hug", "arabic_meaning": "عناق", "category": "actions", "word_family": "ug", "vowel_sound": "u", "difficulty_level": 1, "order": 110, "image_url": "", "emoji": "🤗"},
            {"word": "jug", "arabic_meaning": "إبريق", "category": "kitchen", "word_family": "ug", "vowel_sound": "u", "difficulty_level": 2, "order": 111, "image_url": "", "emoji": "🏺"},
            {"word": "mug", "arabic_meaning": "كوب", "category": "kitchen", "word_family": "ug", "vowel_sound": "u", "difficulty_level": 1, "order": 113, "image_url": "", "emoji": "☕"},
            {"word": "rug", "arabic_meaning": "سجادة صغيرة", "category": "objects", "word_family": "ug", "vowel_sound": "u", "difficulty_level": 1, "order": 114, "image_url": "", "emoji": "🧶"},
            
            {"word": "bun", "arabic_meaning": "كعكة", "category": "food", "word_family": "un", "vowel_sound": "u", "difficulty_level": 1, "order": 116, "image_url": "", "emoji": "🥯"},
            {"word": "fun", "arabic_meaning": "مرح", "category": "adjectives", "word_family": "un", "vowel_sound": "u", "difficulty_level": 1, "order": 117, "image_url": "", "emoji": "🎡"},
            {"word": "run", "arabic_meaning": "يجري", "category": "verbs", "word_family": "un", "vowel_sound": "u", "difficulty_level": 1, "order": 119, "image_url": "", "emoji": "🏃"},
            {"word": "sun", "arabic_meaning": "شمس", "category": "nature", "word_family": "un", "vowel_sound": "u", "difficulty_level": 1, "order": 120, "image_url": "", "emoji": "☀️"},
            
            {"word": "cut", "arabic_meaning": "يقطع", "category": "verbs", "word_family": "ut", "vowel_sound": "u", "difficulty_level": 1, "order": 122, "image_url": "", "emoji": "✂️"},
            {"word": "hut", "arabic_meaning": "كوخ", "category": "places", "word_family": "ut", "vowel_sound": "u", "difficulty_level": 2, "order": 123, "image_url": "", "emoji": "⛺"},
            {"word": "nut", "arabic_meaning": "جوزة", "category": "food", "word_family": "ut", "vowel_sound": "u", "difficulty_level": 1, "order": 124, "image_url": "", "emoji": "🥜"},
            
            {"word": "cub", "arabic_meaning": "شبل", "category": "animals", "word_family": "ub", "vowel_sound": "u", "difficulty_level": 2, "order": 125, "image_url": "", "emoji": "🐻"},
            {"word": "tub", "arabic_meaning": "حوض استحمام", "category": "bathroom", "word_family": "ub", "vowel_sound": "u", "difficulty_level": 1, "order": 128, "image_url": "", "emoji": "🛁"},
            {"word": "bus", "arabic_meaning": "حافلة", "category": "transport", "word_family": "us", "vowel_sound": "u", "difficulty_level": 1, "order": 130, "image_url": "", "emoji": "🚌"},

            # ============================================
            # PRONOUNS (New Category)
            # ============================================
            {"word": "I", "arabic_meaning": "أنا", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 200, "image_url": "", "emoji": "🙋‍♂️"},
            {"word": "He", "arabic_meaning": "هو", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 201, "image_url": "", "emoji": "👨"},
            {"word": "She", "arabic_meaning": "هي", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 202, "image_url": "", "emoji": "👩"},
            {"word": "It", "arabic_meaning": "هو/هي (لغير العاقل)", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 203, "image_url": "", "emoji": "📦"},
            {"word": "We", "arabic_meaning": "نحن", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 204, "image_url": "", "emoji": "👥"},
            {"word": "They", "arabic_meaning": "هم", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 205, "image_url": "", "emoji": "👨‍👩‍👧‍👦"},
            {"word": "You", "arabic_meaning": "أنت/أنتم", "category": "pronouns", "word_family": "", "vowel_sound": "", "difficulty_level": 1, "order": 206, "image_url": "", "emoji": "🫵"},
        ]
        
        # Create words
        created_words = 0
        for data in words_data:
            word, created = CVCWord.objects.get_or_create(
                word=data['word'],
                defaults=data
            )
            if created:
                created_words += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {word.word}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n📚 Created {created_words} new words!\n'))
        
        # ===== RICH THEMED STORIES (SAFE CONTENT) =====
        self.stdout.write('\nPopulating Rich Stories with Quizzes...')
        
        stories_data = [
            {
                "title": "The Fat Cat 🐱",
                "content": "The 🐱 [cat] is fat. The 🐱 [cat] sat on a 🧢 [mat]. Due to the 🐱 [cat], the 🧢 [mat] is now flat! The 🐱 [cat] saw a 🐀 [rat]. The 🐀 [rat] had a 🦇 [bat]. The 🐱 [cat] ran!",
                "arabic_explanation": "القطة سمينة. جلست القطة على المفرش. بسبب القطة، أصبح المفرش مسطحاً! رأت القطة فأراً. الفأر كان لديه مضرب. ركضت القطة!",
                "image_url": "",
                "difficulty": 1,
                "order": 1,
                "quiz_data": [
                    {
                        "question": "Who is fat? (من هو السمين؟)",
                        "options": ["The rat 🐀", "The cat 🐱", "The bat 🦇"],
                        "correct": 1,
                        "feedback_ar": "صحيح! القطة هي السمينة.",
                        "feedback_en": "Correct! The cat is fat."
                    },
                    {
                        "question": "Where did the cat sit? (أين جلست القطة؟)",
                        "options": ["On a hat 🎩", "On a mat 🧢", "On a bat 🦇"],
                        "correct": 1,
                        "feedback_ar": "ممتاز! جلست على السجادة (Mat).",
                        "feedback_en": "Great! Sat on a mat."
                    },
                    {
                        "question": "What did the rat have? (ماذا كان لدى الفأر؟)",
                        "options": ["A mat", "A bat 🦇", "A hat"],
                        "correct": 1,
                        "feedback_ar": "أحسنت! الفأر كان معه مضرب (Bat).",
                        "feedback_en": "Well done! The rat had a bat."
                    }
                ]
            },
            {
                "title": "Ben's Red Pen 🖊️",
                "content": "Ben has a 🖊️ [pen]. The 🖊️ [pen] is 🔴 [red]. Ben fed his 🐔 [hen]. The 🐔 [hen] was in a den. Ten 👦 [men] saw the 🐔 [hen]. The 🐔 [hen] laid an egg for Ben.",
                "arabic_explanation": "بن لديه قلم. القلم أحمر. بن أطعم دجاجته. الدجاجة كانت في العرين. عشرة رجال رأوا الدجاجة. الدجاجة باضت بيضة لبن.",
                "image_url": "",
                "difficulty": 2,
                "order": 2,
                "quiz_data": [
                    {
                        "question": "What color is the pen? (ما لون القلم؟)",
                        "options": ["Blue 🔵", "Red 🔴", "Green 🟢"],
                        "correct": 1,
                        "feedback_ar": "صحيح! القلم أحمر (Red).",
                        "feedback_en": "Correct! The pen is red."
                    },
                    {
                        "question": "Who did Ben feed? (من أطعم بن؟)",
                        "options": ["A dog 🐕", "A hen 🐔", "A fox 🦊"],
                        "correct": 1,
                        "feedback_ar": "ممتاز! أطعم الدجاجة (Hen).",
                        "feedback_en": "Great! He fed the hen."
                    }
                ]
            },
            {
                "title": "Run in the Sun ☀️",
                "content": "A 🐕 [dog] can run. It is 😃 [fun] to run in the ☀️ [sun]. The 🐕 [dog] saw a 🥯 [bun]. The 🐕 [dog] ate the 🥯 [bun]. Now the 🐕 [dog] sat in the ☀️ [sun].",
                "arabic_explanation": "الكلب يستطيع الركض. الركض في الشمس ممتع. الكلب رأى كعكة. أكل الكلب الكعكة. الآن جلس الكلب في الشمس.",
                "image_url": "",
                "difficulty": 2,
                "order": 3,
                "quiz_data": [
                    {
                        "question": "What did the dog do? (ماذا فعل الكلب؟)",
                        "options": ["Run 🏃", "Sleep 😴", "Cry 😢"],
                        "correct": 0,
                        "feedback_ar": "صحيح! الكلب ركض (Run).",
                        "feedback_en": "Correct! The dog can run."
                    },
                    {
                        "question": "What did he eat? (ماذا أكل؟)",
                        "options": ["A mat", "A bun 🥯", "A hat"],
                        "correct": 1,
                        "feedback_ar": "ممتاز! أكل كعكة (Bun).",
                        "feedback_en": "Great! He ate the bun."
                    }
                ]
            },
            {
                "title": "The Sad Dad 👨",
                "content": "The 👨 [dad] is 😢 [sad]. The 👨 [dad] lost his 🗒️ [pad]. The 👦 [lad] found the 🗒️ [pad]. Now the 👨 [dad] is not 😢 [sad]. He gave the 👦 [lad] a hug.",
                "arabic_explanation": "الأب حزين. الأب أضاع دفتره. الصبي وجد الدفتر. الآن الأب ليس حزيناً. أعطى الصبي عناقاً.",
                "image_url": "",
                "difficulty": 3,
                "order": 4,
                "quiz_data": [
                    {
                        "question": "Why was dad sad? (لماذا كان الأب حزيناً؟)",
                        "options": ["Lost his pad 🗒️", "Lost his cat 🐱", "It was hot 🔥"],
                        "correct": 0,
                        "feedback_ar": "صحيح! أضاع دفتره (Lost his pad).",
                        "feedback_en": "Correct! He lost his pad."
                    },
                    {
                        "question": "Who found the pad? (من وجد الدفتر؟)",
                        "options": ["A cat", "A lad 👦", "A rat"],
                        "correct": 1,
                        "feedback_ar": "ممتاز! الصبي (Lad) وجده.",
                        "feedback_en": "Great! The lad found it."
                    }
                ]
            },
            {
                "title": "Bug on a Rug 🐞",
                "content": "A 🐞 [bug] is in a 🏺 [jug]. The 🐞 [bug] is on a 🧶 [rug]. Give the 🐞 [bug] a 🤗 [hug]. The 🐞 [bug] dug in the mud. It is a fun 🐞 [bug]!",
                "arabic_explanation": "حشرة في إبريق. الحشرة على سجادة. عانق الحشرة. الحشرة حفرت في الطين. إنها حشرة ممتعة!",
                "image_url": "",
                "difficulty": 3,
                "order": 5,
                "quiz_data": [
                    {
                        "question": "Where is the bug? (أين الحشرة؟)",
                        "options": ["In a jug 🏺", "In a mug", "In a tub"],
                        "correct": 0,
                        "feedback_ar": "صحيح! في الإبريق (Jug).",
                        "feedback_en": "Correct! In a jug."
                    },
                    {
                        "question": "What did the bug do? (ماذا فعلت الحشرة؟)",
                        "options": ["Run", "Dug ⛏️", "Hug"],
                        "correct": 1,
                        "feedback_ar": "ممتاز! حفرت (Dug).",
                        "feedback_en": "Great! The bug dug."
                    }
                ]
            }
        ]
        
        created_stories = 0
        for data in stories_data:
            story, created = CVCStory.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                created_stories += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Story: {story.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n📚 Created {created_stories} rich stories!\n'))

        # ===== PRONOUN SENTENCES =====
        self.stdout.write('\nPopulating Pronoun Sentences with Quizzes...')
        
        sentences_data = [
            # I
            {"sentence": "I am happy.", "arabic_translation": "أنا سعيد.", "category": "pronouns", "emoji": "😀", "order": 1},
            {"sentence": "I like to read.", "arabic_translation": "أنا أحب القراءة.", "category": "pronouns", "emoji": "📖", "order": 2},
            {"sentence": "I see a cat.", "arabic_translation": "أنا أرى قطة.", "category": "pronouns", "emoji": "🐱", "order": 3, 
             "quiz_data": {"question": "What do I see?", "options": ["A dog", "A cat 🐱", "A rat"], "correct": 1, "feedback_ar": "أرى قطة!"}},
            
            # He
            {"sentence": "He runs fast.", "arabic_translation": "هو يركض بسرعة.", "category": "pronouns", "emoji": "🏃", "order": 4},
            {"sentence": "He has a red hat.", "arabic_translation": "هو لديه قبعة حمراء.", "category": "pronouns", "emoji": "🎩", "order": 5},
            {"sentence": "He is my dad.", "arabic_translation": "هو أبي.", "category": "pronouns", "emoji": "👨", "order": 6,
             "quiz_data": {"question": "Who is he?", "options": ["My dad 👨", "My cat", "My bag"], "correct": 0, "feedback_ar": "إنه أبي!"}},
            
            # She
            {"sentence": "She sings a song.", "arabic_translation": "هي تغني أغنية.", "category": "pronouns", "emoji": "🎤", "order": 7},
            {"sentence": "She has a big bag.", "arabic_translation": "هي لديها حقيبة كبيرة.", "category": "pronouns", "emoji": "👜", "order": 8},
            {"sentence": "She sits on a mat.", "arabic_translation": "هي تجلس على السجادة.", "category": "pronouns", "emoji": "🧘‍♀️", "order": 9,
             "quiz_data": {"question": "Where does she sit?", "options": ["On a hat", "On a mat 🧘‍♀️", "On a bat"], "correct": 1, "feedback_ar": "تجلس على السجادة!"}},
             
            # We/They/It
            {"sentence": "We play with a ball.", "arabic_translation": "نحن نلعب بالكرة.", "category": "pronouns", "emoji": "⚽", "order": 10},
            {"sentence": "They are my friends.", "arabic_translation": "هم أصدقائي.", "category": "pronouns", "emoji": "👫", "order": 11},
            {"sentence": "It is a cute dog.", "arabic_translation": "إنه كلب لطيف.", "category": "pronouns", "emoji": "🐶", "order": 12,
             "quiz_data": {"question": "What is it?", "options": ["A cat", "A dog 🐶", "A bag"], "correct": 1, "feedback_ar": "إنه كلب!"}},
        ]
        
        created_sentences = 0
        for data in sentences_data:
            sentence, created = CVCSentence.objects.get_or_create(
                sentence=data['sentence'],
                defaults=data
            )
            if created:
                created_sentences += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Sentence: {sentence.sentence}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🗣️ Created {created_sentences} sentences!\n'))

        # Final summary
        total_words = CVCWord.objects.count()
        total_stories = CVCStory.objects.count()
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS(f'🎉 Database Population Complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Total Words: {total_words}'))
        self.stdout.write(self.style.SUCCESS(f'   Total Stories: {total_stories}'))
        self.stdout.write('='*60)
