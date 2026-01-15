"""
Django management command to populate all CVC data (Words, Sentences, Stories)
Usage: python manage.py populate_all_cvc
"""

from django.core.management.base import BaseCommand
from phonics.models import CVCWord, CVCSentence, CVCStory


class Command(BaseCommand):
    help = 'Populate database with all CVC data (Words, Sentences, Stories)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 بدء إضافة جميع بيانات CVC...'))
        
        # ============================================
        # 1. إضافة الكلمات CVC Words
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📚 إضافة كلمات CVC...'))
        
        old_words = CVCWord.objects.count()
        CVCWord.objects.all().delete()
        self.stdout.write(f'✅ تم حذف {old_words} كلمة قديمة')
        
        words_data = [
            # -at family
            {"word": "CAT", "arabic": "قطة", "category": "animals", "difficulty": 1, "order": 1, "emoji": "🐱", "word_family": "at", "vowel": "a"},
            {"word": "BAT", "arabic": "خفاش", "category": "animals", "difficulty": 1, "order": 2, "emoji": "🦇", "word_family": "at", "vowel": "a"},
            {"word": "RAT", "arabic": "فأر", "category": "animals", "difficulty": 1, "order": 3, "emoji": "🐀", "word_family": "at", "vowel": "a"},
            {"word": "MAT", "arabic": "سجادة", "category": "objects", "difficulty": 1, "order": 4, "emoji": "🧘", "word_family": "at", "vowel": "a"},
            {"word": "HAT", "arabic": "قبعة", "category": "clothes", "difficulty": 1, "order": 5, "emoji": "🎩", "word_family": "at", "vowel": "a"},
            {"word": "FAT", "arabic": "سمين", "category": "adjectives", "difficulty": 1, "order": 6, "emoji": "🐘", "word_family": "at", "vowel": "a"},
            
            # -og family
            {"word": "DOG", "arabic": "كلب", "category": "animals", "difficulty": 1, "order": 7, "emoji": "🐕", "word_family": "og", "vowel": "o"},
            {"word": "LOG", "arabic": "جذع شجرة", "category": "nature", "difficulty": 2, "order": 8, "emoji": "🪵", "word_family": "og", "vowel": "o"},
            {"word": "FOG", "arabic": "ضباب", "category": "nature", "difficulty": 2, "order": 9, "emoji": "🌫️", "word_family": "og", "vowel": "o"},
            {"word": "HOG", "arabic": "خنزير بري", "category": "animals", "difficulty": 2, "order": 10, "emoji": "🐗", "word_family": "og", "vowel": "o"},
            
            # -ig family
            {"word": "BIG", "arabic": "كبير", "category": "adjectives", "difficulty": 1, "order": 11, "emoji": "📏", "word_family": "ig", "vowel": "i"},
            {"word": "PIG", "arabic": "خنزير", "category": "animals", "difficulty": 1, "order": 12, "emoji": "🐷", "word_family": "ig", "vowel": "i"},
            {"word": "DIG", "arabic": "يحفر", "category": "verbs", "difficulty": 2, "order": 13, "emoji": "⛏️", "word_family": "ig", "vowel": "i"},
            {"word": "WIG", "arabic": "باروكة", "category": "objects", "difficulty": 2, "order": 14, "emoji": "💇", "word_family": "ig", "vowel": "i"},
            
            # -un family  
            {"word": "SUN", "arabic": "شمس", "category": "nature", "difficulty": 1, "order": 15, "emoji": "☀️", "word_family": "un", "vowel": "u"},
            {"word": "RUN", "arabic": "يركض", "category": "verbs", "difficulty": 1, "order": 16, "emoji": "🏃", "word_family": "un", "vowel": "u"},
            {"word": "BUN", "arabic": "كعكة", "category": "food", "difficulty": 1, "order": 17, "emoji": "🥐", "word_family": "un", "vowel": "u"},
            {"word": "FUN", "arabic": "مرح", "category": "adjectives", "difficulty": 1, "order": 18, "emoji": "🎉", "word_family": "un", "vowel": "u"},
            
            # -ed family
            {"word": "BED", "arabic": "سرير", "category": "objects", "difficulty": 1, "order": 19, "emoji": "🛏️", "word_family": "ed", "vowel": "e"},
            {"word": "RED", "arabic": "أحمر", "category": "colors", "difficulty": 1, "order": 20, "emoji": "❤️", "word_family": "ed", "vowel": "e"},
            {"word": "FED", "arabic": "أطعم", "category": "verbs", "difficulty": 2, "order": 21, "emoji": "🍽️", "word_family": "ed", "vowel": "e"},
            
            # -en family
            {"word": "PEN", "arabic": "قلم", "category": "objects", "difficulty": 1, "order": 22, "emoji": "🖊️", "word_family": "en", "vowel": "e"},
            {"word": "TEN", "arabic": "عشرة", "category": "numbers", "difficulty": 1, "order": 23, "emoji": "🔟", "word_family": "en", "vowel": "e"},
            {"word": "HEN", "arabic": "دجاجة", "category": "animals", "difficulty": 1, "order": 24, "emoji": "🐓", "word_family": "en", "vowel": "e"},
            
            # -op family
            {"word": "TOP", "arabic": "قمة", "category": "objects", "difficulty": 2, "order": 25, "emoji": "🔝", "word_family": "op", "vowel": "o"},
            {"word": "HOP", "arabic": "يقفز", "category": "verbs", "difficulty": 2, "order": 26, "emoji": "🦘", "word_family": "op", "vowel": "o"},
            {"word": "MOP", "arabic": "ممسحة", "category": "objects", "difficulty": 2, "order": 27, "emoji": "🧹", "word_family": "op", "vowel": "o"},
            
            # -ot family
            {"word": "POT", "arabic": "وعاء", "category": "objects", "difficulty": 2, "order": 28, "emoji": "🍲", "word_family": "ot", "vowel": "o"},
            {"word": "HOT", "arabic": "حار", "category": "adjectives", "difficulty": 1, "order": 29, "emoji": "🔥", "word_family": "ot", "vowel": "o"},
            {"word": "DOT", "arabic": "نقطة", "category": "objects", "difficulty": 2, "order": 30, "emoji": "⚫", "word_family": "ot", "vowel": "o"},
            
            # Mixed
            {"word": "BUS", "arabic": "حافلة", "category": "vehicles", "difficulty": 1, "order": 31, "emoji": "🚌", "word_family": "us", "vowel": "u"},
            {"word": "CUP", "arabic": "كوب", "category": "objects", "difficulty": 1, "order": 32, "emoji": "☕", "word_family": "up", "vowel": "u"},
            {"word": "NUT", "arabic": "جوزة", "category": "food", "difficulty": 2, "order": 33, "emoji": "🥜", "word_family": "ut", "vowel": "u"},
            {"word": "BAG", "arabic": "حقيبة", "category": "objects", "difficulty": 1, "order": 34, "emoji": "🎒", "word_family": "ag", "vowel": "a"},
            {"word": "SIT", "arabic": "يجلس", "category": "verbs", "difficulty": 1, "order": 35, "emoji": "🪑", "word_family": "it", "vowel": "i"},
        ]
        
        for word_data in words_data:
            CVCWord.objects.create(
                word=word_data["word"],
                arabic_meaning=word_data["arabic"],
                category=word_data["category"],
                difficulty_level=word_data["difficulty"],
                order=word_data["order"],
                emoji=word_data["emoji"],
                word_family=word_data["word_family"],
                vowel_sound=word_data["vowel"]
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ تم إضافة {len(words_data)} كلمة CVC'))
        
        # ============================================
        # 2. إضافة الجمل CVC Sentences
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📝 إضافة جمل CVC...'))
        
        old_sentences = CVCSentence.objects.count()
        CVCSentence.objects.all().delete()
        self.stdout.write(f'✅ تم حذف {old_sentences} جملة قديمة')
        
        sentences_data = [
            {"sentence": "The cat sat on the mat.", "arabic": "القطة جلست على السجادة.", "difficulty": 1, "time": 30, "order": 1, "emoji": "🐱", "category": "cvc"},
            {"sentence": "A big dog ran to the log.", "arabic": "كلب كبير ركض إلى الجذع.", "difficulty": 1, "time": 30, "order": 2, "emoji": "🐕", "category": "cvc"},
            {"sentence": "I see a red pen on the bed.", "arabic": "أرى قلماً أحمراً على السرير.", "difficulty": 2, "time": 35, "order": 3, "emoji": "🖊️", "category": "cvc"},
            {"sentence": "The sun is hot.", "arabic": "الشمس حارة.", "difficulty": 1, "time": 20, "order": 4, "emoji": "☀️", "category": "cvc"},
            {"sentence": "A rat hid in a pot.", "arabic": "فأر اختبأ في وعاء.", "difficulty": 2, "time": 25, "order": 5, "emoji": "🐀", "category": "cvc"},
            {"sentence": "Put on your hat and get in the bus.", "arabic": "ضع قبعتك واركب الحافلة.", "difficulty": 3, "time": 40, "order": 6, "emoji": "🎩", "category": "cvc"},
            {"sentence": "The pig is big.", "arabic": "الخنزير كبير.", "difficulty": 1, "time": 20, "order": 7, "emoji": "🐷", "category": "cvc"},
            {"sentence": "I can see fog on the top.", "arabic": "أستطيع رؤية الضباب على القمة.", "difficulty": 3, "time": 35, "order": 8, "emoji": "🌫️", "category": "cvc"},
            {"sentence": "The hen is in the pen.", "arabic": "الدجاجة في الحظيرة.", "difficulty": 2, "time": 25, "order": 9, "emoji": "🐓", "category": "cvc"},
            {"sentence": "I run in the sun for fun.", "arabic": "أركض تحت الشمس للمرح.", "difficulty": 2, "time": 30, "order": 10, "emoji": "🏃", "category": "cvc"},
        ]
        
        for sent_data in sentences_data:
            CVCSentence.objects.create(
                sentence=sent_data["sentence"],
                arabic_translation=sent_data["arabic"],
                difficulty=sent_data["difficulty"],
                time_limit=sent_data["time"],
                order=sent_data["order"],
                emoji=sent_data["emoji"],
                category=sent_data["category"]
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ تم إضافة {len(sentences_data)} جملة CVC'))
        
        # ============================================
        # 3. إضافة القصص CVC Stories
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n📖 إضافة قصص CVC...'))
        
        old_stories = CVCStory.objects.count()
        CVCStory.objects.all().delete()
        self.stdout.write(f'✅ تم حذف {old_stories} قصة قديمة')
        
        stories_data = [
            {
                'title': '🐱 The Fat Cat',
                'content': '''Once upon a time, there was a [fat] 🐱 cat. 
The cat sat on a [mat]. 
The cat had a red [hat] 🎩.
The cat saw a [rat] 🐭 near the hat.
The rat ran fast! The cat sat back on the mat.''',
                'arabic_explanation': '''كان يا ما كان قطة سمينة 🐱
جلست القطة على السجادة
كان لدى القطة قبعة حمراء 🎩
رأت القطة فأراً 🐭 بالقرب من القبعة
هرب الفأر بسرعة! فجلست القطة مرة أخرى على السجادة''',
                'image_url': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400',
                'quiz_data': [
                    {
                        'question': 'Where did the cat sit?',
                        'question_ar': 'أين جلست القطة؟',
                        'options': ['On a mat', 'On a bed', 'On a chair', 'On a box'],
                        'correct': 0,
                        'feedback_ar': 'رائع! القطة جلست على السجادة',
                        'feedback_en': 'Great! The cat sat on a mat'
                    },
                    {
                        'question': 'What did the cat wear?',
                        'question_ar': 'ماذا ارتدت القطة؟',
                        'options': ['A coat', 'A hat', 'A bag', 'A scarf'],
                        'correct': 1,
                        'feedback_ar': 'ممتاز! القطة كانت ترتدي قبعة',
                        'feedback_en': 'Excellent! The cat wore a hat'
                    },
                ],
                'difficulty': 1,
                'order': 1
            },
            {
                'title': '☀️ A Fun Day',
                'content': '''The [sun] ☀️ is up. 
Tom can [run] 🏃 and have fun.
He runs to the [bus] 🚌 stop.
Tom has a [bun] 🥐 in his bag.
Tom sits in the bus and eats the bun. Yum! 😋''',
                'arabic_explanation': '''الشمس مشرقة ☀️
توم يستطيع الجري 🏃 والاستمتاع
يركض إلى محطة الحافلة 🚌
لدى توم كعكة 🥐 في حقيبته
يجلس توم في الحافلة ويأكل الكعكة. لذيذة! 😋''',
                'image_url': 'https://images.unsplash.com/photo-1544776193-352d25ca82cd?w=400',
                'quiz_data': [
                    {
                        'question': 'What is up in the sky?',
                        'question_ar': 'ماذا يوجد في السماء؟',
                        'options': ['The moon', 'The sun', 'A cloud', 'A star'],
                        'correct': 1,
                        'feedback_ar': 'صحيح! الشمس مشرقة',
                        'feedback_en': 'Correct! The sun is up'
                    },
                ],
                'difficulty': 1,
                'order': 2
            },
            {
                'title': '🐶 The Little Dog',
                'content': '''There is a little [dog] 🐶 named Max.
Max can [dig] ⛏️ in the mud.
Max dug a [big] hole.
Max found a [stick] 🪵 in the hole.
Max is happy! He wags his tail. 🐕''',
                'arabic_explanation': '''يوجد كلب صغير 🐶 اسمه ماكس
ماكس يستطيع الحفر ⛏️ في الطين
حفر ماكس حفرة كبيرة
وجد ماكس عصا 🪵 في الحفرة
ماكس سعيد! يهز ذيله 🐕''',
                'image_url': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400',
                'quiz_data': [],
                'difficulty': 1,
                'order': 3
            },
        ]
        
        for story_data in stories_data:
            CVCStory.objects.create(
                title=story_data['title'],
                content=story_data['content'],
                arabic_explanation=story_data['arabic_explanation'],
                image_url=story_data['image_url'],
                quiz_data=story_data['quiz_data'],
                difficulty=story_data['difficulty'],
                order=story_data['order']
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ تم إضافة {len(stories_data)} قصة CVC'))
        
        # النتيجة النهائية
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🎉 تم إضافة جميع بيانات CVC بنجاح!'))
        self.stdout.write(self.style.SUCCESS(f'📚 إجمالي الكلمات: {CVCWord.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'📝 إجمالي الجمل: {CVCSentence.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'📖 إجمالي القصص: {CVCStory.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*50))
