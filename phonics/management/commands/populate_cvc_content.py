# -*- coding: utf-8 -*-
"""
Management command لإضافة كلمات وجمل وقصص CVC مناسبة للثقافة العربية
تأكد من عدم وجود محتوى غير مناسب
"""
from django.core.management.base import BaseCommand
from phonics.models import CVCWord, CVCSentence, CVCStory


class Command(BaseCommand):
    help = 'إضافة محتوى CVC جديد متوافق مع الثقافة العربية'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إضافة محتوى CVC الجديد...\n'))
        
        # حذف البيانات القديمة (اختياري - احذف هذا السطر إن أردت الاحتفاظ بالبيانات القديمة)
        # CVCWord.objects.all().delete()
        # CVCSentence.objects.all().delete()
        # CVCStory.objects.all().delete()
        
        self.add_words()
        self.add_sentences()
        self.add_stories()
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم إضافة جميع البيانات بنجاح!'))

    def add_words(self):
        """إضافة كلمات CVC جديدة"""
        self.stdout.write('📝 إضافة الكلمات...')
        
        words_data = [
            # مجموعة الحيوانات - Animals
            {
                'word': 'cat', 
                'arabic_meaning': 'قط/قطة', 
                'category': 'animals',
                'emoji': '🐱',
                'word_family': 'at',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 1
            },
            {
                'word': 'bat', 
                'arabic_meaning': 'خفاش', 
                'category': 'animals',
                'emoji': '🦇',
                'word_family': 'at',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 2
            },
            {
                'word': 'rat', 
                'arabic_meaning': 'فأر', 
                'category': 'animals',
                'emoji': '🐭',
                'word_family': 'at',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 3
            },
            {
                'word': 'hen', 
                'arabic_meaning': 'دجاجة', 
                'category': 'animals',
                'emoji': '🐔',
                'word_family': 'en',
                'vowel_sound': 'e',
                'difficulty_level': 1,
                'order': 4
            },
            {
                'word': 'fox', 
                'arabic_meaning': 'ثعلب', 
                'category': 'animals',
                'emoji': '🦊',
                'word_family': 'ox',
                'vowel_sound': 'o',
                'difficulty_level': 2,
                'order': 5
            },
            {
                'word': 'ram', 
                'arabic_meaning': 'كبش', 
                'category': 'animals',
                'emoji': '🐏',
                'word_family': 'am',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 6
            },
            {
                'word': 'bug', 
                'arabic_meaning': 'حشرة', 
                'category': 'animals',
                'emoji': '🐛',
                'word_family': 'ug',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 7
            },
            
            # مجموعة الطعام - Food
            {
                'word': 'bun', 
                'arabic_meaning': 'كعكة', 
                'category': 'food',
                'emoji': '🍞',
                'word_family': 'un',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 10
            },
            {
                'word': 'nut', 
                'arabic_meaning': 'جوزة', 
                'category': 'food',
                'emoji': '🥜',
                'word_family': 'ut',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 11
            },
            {
                'word': 'jam', 
                'arabic_meaning': 'مربى', 
                'category': 'food',
                'emoji': '🍓',
                'word_family': 'am',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 12
            },
            
            # مجموعة الطبيعة - Nature
            {
                'word': 'sun', 
                'arabic_meaning': 'شمس', 
                'category': 'nature',
                'emoji': '☀️',
                'word_family': 'un',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 20
            },
            {
                'word': 'mud', 
                'arabic_meaning': 'طين', 
                'category': 'nature',
                'emoji': '🟤',
                'word_family': 'ud',
                'vowel_sound': 'u',
                'difficulty_level': 2,
                'order': 21
            },
            {
                'word': 'log', 
                'arabic_meaning': 'جذع شجرة', 
                'category': 'nature',
                'emoji': '🪵',
                'word_family': 'og',
                'vowel_sound': 'o',
                'difficulty_level': 2,
                'order': 22
            },
            {
                'word': 'web', 
                'arabic_meaning': 'شبكة', 
                'category': 'nature',
                'emoji': '🕸️',
                'word_family': 'eb',
                'vowel_sound': 'e',
                'difficulty_level': 2,
                'order': 23
            },
            
            # مجموعة الأدوات - Objects
            {
                'word': 'box', 
                'arabic_meaning': 'صندوق', 
                'category': 'objects',
                'emoji': '📦',
                'word_family': 'ox',
                'vowel_sound': 'o',
                'difficulty_level': 1,
                'order': 30
            },
            {
                'word': 'bag', 
                'arabic_meaning': 'حقيبة', 
                'category': 'objects',
                'emoji': '🎒',
                'word_family': 'ag',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 31
            },
            {
                'word': 'pen', 
                'arabic_meaning': 'قلم', 
                'category': 'objects',
                'emoji': '✏️',
                'word_family': 'en',
                'vowel_sound': 'e',
                'difficulty_level': 1,
                'order': 32
            },
            {
                'word': 'hat', 
                'arabic_meaning': 'قبعة', 
                'category': 'objects',
                'emoji': '🧢',
                'word_family': 'at',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 33
            },
            {
                'word': 'cup', 
                'arabic_meaning': 'كوب', 
                'category': 'objects',
                'emoji': '☕',
                'word_family': 'up',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 34
            },
            {
                'word': 'pan', 
                'arabic_meaning': 'مقلاة', 
                'category': 'objects',
                'emoji': '🍳',
                'word_family': 'an',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 35
            },
            {
                'word': 'pot', 
                'arabic_meaning': 'قدر', 
                'category': 'objects',
                'emoji': '🍲',
                'word_family': 'ot',
                'vowel_sound': 'o',
                'difficulty_level': 1,
                'order': 36
            },
            {
                'word': 'can', 
                'arabic_meaning': 'علبة', 
                'category': 'objects',
                'emoji': '🥫',
                'word_family': 'an',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 37
            },
            {
                'word': 'map', 
                'arabic_meaning': 'خريطة', 
                'category': 'objects',
                'emoji': '🗺️',
                'word_family': 'ap',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 38
            },
            {
                'word': 'net', 
                'arabic_meaning': 'شبكة', 
                'category': 'objects',
                'emoji': '🥅',
                'word_family': 'et',
                'vowel_sound': 'e',
                'difficulty_level': 2,
                'order': 39
            },
            
            # مجموعة الأفعال - Actions
            {
                'word': 'run', 
                'arabic_meaning': 'يجري', 
                'category': 'actions',
                'emoji': '🏃',
                'word_family': 'un',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 40
            },
            {
                'word': 'sit', 
                'arabic_meaning': 'يجلس', 
                'category': 'actions',
                'emoji': '🪑',
                'word_family': 'it',
                'vowel_sound': 'i',
                'difficulty_level': 1,
                'order': 41
            },
            {
                'word': 'hop', 
                'arabic_meaning': 'يقفز', 
                'category': 'actions',
                'emoji': '🦘',
                'word_family': 'op',
                'vowel_sound': 'o',
                'difficulty_level': 1,
                'order': 42
            },
            {
                'word': 'dig', 
                'arabic_meaning': 'يحفر', 
                'category': 'actions',
                'emoji': '⛏️',
                'word_family': 'ig',
                'vowel_sound': 'i',
                'difficulty_level': 2,
                'order': 43
            },
            {
                'word': 'hug', 
                'arabic_meaning': 'يعانق', 
                'category': 'actions',
                'emoji': '🤗',
                'word_family': 'ug',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 44
            },
            
            # كلمات إضافية
            {
                'word': 'mat', 
                'arabic_meaning': 'سجادة', 
                'category': 'objects',
                'emoji': '🧘',
                'word_family': 'at',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 50
            },
            {
                'word': 'bed', 
                'arabic_meaning': 'سرير', 
                'category': 'objects',
                'emoji': '🛏️',
                'word_family': 'ed',
                'vowel_sound': 'e',
                'difficulty_level': 1,
                'order': 51
            },
            {
                'word': 'van', 
                'arabic_meaning': 'شاحنة', 
                'category': 'objects',
                'emoji': '🚐',
                'word_family': 'an',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 52
            },
            {
                'word': 'ten', 
                'arabic_meaning': 'عشرة', 
                'category': 'numbers',
                'emoji': '🔟',
                'word_family': 'en',
                'vowel_sound': 'e',
                'difficulty_level': 1,
                'order': 53
            },
            {
                'word': 'top', 
                'arabic_meaning': 'قمة/أعلى', 
                'category': 'objects',
                'emoji': '⬆️',
                'word_family': 'op',
                'vowel_sound': 'o',
                'difficulty_level': 2,
                'order': 54
            },
            {
                'word': 'lot', 
                'arabic_meaning': 'كثير', 
                'category': 'other',
                'emoji': '📊',
                'word_family': 'ot',
                'vowel_sound': 'o',
                'difficulty_level': 2,
                'order': 55
            },
            {
                'word': 'den', 
                'arabic_meaning': 'وكر/كهف', 
                'category': 'nature',
                'emoji': '🏔️',
                'word_family': 'en',
                'vowel_sound': 'e',
                'difficulty_level': 2,
                'order': 56
            },
            {
                'word': 'fan', 
                'arabic_meaning': 'مروحة', 
                'category': 'objects',
                'emoji': '💨',
                'word_family': 'an',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 57
            },
            {
                'word': 'nap', 
                'arabic_meaning': 'قيلولة', 
                'category': 'actions',
                'emoji': '😴',
                'word_family': 'ap',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 58
            },
            {
                'word': 'get', 
                'arabic_meaning': 'يحصل على', 
                'category': 'actions',
                'emoji': '🎁',
                'word_family': 'et',
                'vowel_sound': 'e',
                'difficulty_level': 2,
                'order': 59
            },
            {
                'word': 'bad', 
                'arabic_meaning': 'سيء/مشاغب', 
                'category': 'other',
                'emoji': '😈',
                'word_family': 'ad',
                'vowel_sound': 'a',
                'difficulty_level': 2,
                'order': 60
            },
            {
                'word': 'sad', 
                'arabic_meaning': 'حزين', 
                'category': 'other',
                'emoji': '😢',
                'word_family': 'ad',
                'vowel_sound': 'a',
                'difficulty_level': 1,
                'order': 61
            },
            {
                'word': 'red', 
                'arabic_meaning': 'أحمر', 
                'category': 'colors',
                'emoji': '🔴',
                'word_family': 'ed',
                'vowel_sound': 'e',
                'difficulty_level': 1,
                'order': 62
            },
            {
                'word': 'big', 
                'arabic_meaning': 'كبير', 
                'category': 'other',
                'emoji': '🐘',
                'word_family': 'ig',
                'vowel_sound': 'i',
                'difficulty_level': 1,
                'order': 63
            },
            {
                'word': 'hot', 
                'arabic_meaning': 'حار', 
                'category': 'other',
                'emoji': '🌡️',
                'word_family': 'ot',
                'vowel_sound': 'o',
                'difficulty_level': 1,
                'order': 64
            },
            {
                'word': 'fun', 
                'arabic_meaning': 'مرح/متعة', 
                'category': 'other',
                'emoji': '🎉',
                'word_family': 'un',
                'vowel_sound': 'u',
                'difficulty_level': 1,
                'order': 65
            },
        ]
        
        for word_data in words_data:
            word_obj, created = CVCWord.objects.get_or_create(
                word=word_data['word'],
                defaults=word_data
            )
            if created:
                self.stdout.write(f'  ✓ {word_data["word"]} ({word_data["arabic_meaning"]})')
            else:
                # تحديث البيانات إذا كانت موجودة
                for key, value in word_data.items():
                    setattr(word_obj, key, value)
                word_obj.save()
                self.stdout.write(f'  ↻ {word_data["word"]} (تم التحديث)')

    def add_sentences(self):
        """إضافة جمل CVC جديدة"""
        self.stdout.write('\n📝 إضافة الجمل...')
        
        sentences_data = [
            # جمل عن الحيوانات
            {
                'sentence': 'A cat sat on a mat.',
                'arabic_translation': 'جلست قطة على سجادة.',
                'difficulty': 1,
                'time_limit': 20,
                'category': 'animals',
                'emoji': '🐱',
                'order': 1
            },
            {
                'sentence': 'The hen is in the pen.',
                'arabic_translation': 'الدجاجة في الحظيرة.',
                'difficulty': 1,
                'time_limit': 20,
                'category': 'animals',
                'emoji': '🐔',
                'order': 2
            },
            {
                'sentence': 'A fox ran in the sun.',
                'arabic_translation': 'ركض ثعلب تحت الشمس.',
                'difficulty': 2,
                'time_limit': 25,
                'category': 'animals',
                'emoji': '🦊',
                'order': 3
            },
            {
                'sentence': 'The rat hid in a box.',
                'arabic_translation': 'اختبأ الفأر في صندوق.',
                'difficulty': 1,
                'time_limit': 20,
                'category': 'animals',
                'emoji': '🐭',
                'order': 4
            },
            {
                'sentence': 'A bat can hop and run.',
                'arabic_translation': 'يستطيع الخفاش القفز والجري.',
                'difficulty': 2,
                'time_limit': 25,
                'category': 'animals',
                'emoji': '🦇',
                'order': 5
            },
            
            # جمل عن الطبيعة
            {
                'sentence': 'The sun is hot.',
                'arabic_translation': 'الشمس حارة.',
                'difficulty': 1,
                'time_limit': 15,
                'category': 'nature',
                'emoji': '☀️',
                'order': 10
            },
            {
                'sentence': 'A bug is on the log.',
                'arabic_translation': 'حشرة على جذع الشجرة.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'nature',
                'emoji': '🐛',
                'order': 11
            },
            {
                'sentence': 'We sat in the mud.',
                'arabic_translation': 'جلسنا في الطين.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'nature',
                'emoji': '🟤',
                'order': 12
            },
            
            # جمل عن الطعام
            {
                'sentence': 'Mom has a hot bun.',
                'arabic_translation': 'أمي لديها كعكة ساخنة.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'food',
                'emoji': '🍞',
                'order': 20
            },
            {
                'sentence': 'Dad cut a big nut.',
                'arabic_translation': 'أبي قطع جوزة كبيرة.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'food',
                'emoji': '🥜',
                'order': 21
            },
            {
                'sentence': 'I put jam in a can.',
                'arabic_translation': 'وضعت المربى في علبة.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'food',
                'emoji': '🍓',
                'order': 22
            },
            
            # جمل عن الأشياء
            {
                'sentence': 'The bag is on the bed.',
                'arabic_translation': 'الحقيبة على السرير.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'objects',
                'emoji': '🎒',
                'order': 30
            },
            {
                'sentence': 'I see a red hat.',
                'arabic_translation': 'أرى قبعة حمراء.',
                'difficulty': 1,
                'time_limit': 15,
                'category': 'objects',
                'emoji': '🧢',
                'order': 31
            },
            {
                'sentence': 'The pen is in the box.',
                'arabic_translation': 'القلم في الصندوق.',
                'difficulty': 1,
                'time_limit': 20,
                'category': 'objects',
                'emoji': '✏️',
                'order': 32
            },
            
            # جمل عن الأفعال
            {
                'sentence': 'We run and hop.',
                'arabic_translation': 'نحن نجري ونقفز.',
                'difficulty': 1,
                'time_limit': 15,
                'category': 'actions',
                'emoji': '🏃',
                'order': 40
            },
            {
                'sentence': 'Mom and Dad hug me.',
                'arabic_translation': 'أمي وأبي يعانقانني.',
                'difficulty': 2,
                'time_limit': 20,
                'category': 'actions',
                'emoji': '🤗',
                'order': 41
            },
            {
                'sentence': 'I sit on the mat.',
                'arabic_translation': 'أجلس على السجادة.',
                'difficulty': 1,
                'time_limit': 15,
                'category': 'actions',
                'emoji': '🪑',
                'order': 42
            },
        ]
        
        for sent_data in sentences_data:
            sent_obj, created = CVCSentence.objects.get_or_create(
                sentence=sent_data['sentence'],
                defaults=sent_data
            )
            if created:
                self.stdout.write(f'  ✓ {sent_data["sentence"][:40]}...')
            else:
                for key, value in sent_data.items():
                    setattr(sent_obj, key, value)
                sent_obj.save()
                self.stdout.write(f'  ↻ {sent_data["sentence"][:40]}... (تم التحديث)')

    def add_stories(self):
        """إضافة قصص CVC جديدة بالثقافة العربية"""
        self.stdout.write('\n📚 إضافة القصص...')
        
        stories_data = [
            {
                'title': 'Sam the Cat and the Hot Sun',
                'content': '''Sam is a tan cat. He sat on top of a big, hot van. The sun is up! It is a hot, hot day. Sam can see a lot of sand.

A big ram ran to him. "Hi Sam!" said the ram. "Let us sit in the den and get a fan. It is hot!"

Sam and the ram had fun. They had a nap in the den.''',
                'arabic_explanation': '''سام قط بني اللون. جلس على سطح شاحنة كبيرة وحارة. الشمس ساطعة! إنه يوم حار جداً. يستطيع سام رؤية الكثير من الرمال.

ركض كبش كبير نحوه. "مرحباً سام!" قال الكبش. "دعنا نجلس في الكهف ونأخذ مروحة. الجو حار!"

استمتع سام والكبش. أخذوا قيلولة في الكهف.''',
                'difficulty': 2,
                'order': 1
            },
            {
                'title': 'A Red Hat',
                'content': '''Pam has a red hat. She put it in a big bag. The bag is on a mat. A cat sat on the mat. The cat is a bad cat!

The cat got in the bag! The red hat is not in the bag! "Bad cat!" said Pam. "Get out!"

Pam can see the hat. It is on the cat! The cat ran and ran. But Pam got it. "My red hat!" Pam is glad.''',
                'arabic_explanation': '''لدى بام قبعة حمراء. وضعتها في حقيبة كبيرة. الحقيبة على سجادة. جلست قطة على السجادة. القطة مشاغبة!

دخلت القطة في الحقيبة! القبعة الحمراء ليست في الحقيبة! "قطة مشاغبة!" قالت بام. "اخرجي!"

استطاعت بام رؤية القبعة. إنها على القطة! ركضت القطة وركضت. لكن بام أمسكت بها. "قبعتي الحمراء!" بام سعيدة.''',
                'difficulty': 2,
                'order': 2
            },
            {
                'title': 'Fox Can Help',
                'content': '''A fox sat on a log. He can see a hen. The hen is sad. "I am in a jam!" said the hen. "I cannot get in my pen."

"I can help!" said the fox. The fox got a big box. The hen can hop on the box. Now the hen can get in the pen!

"You are the best!" said the hen. The fox is glad. They had a lot of fun.''',
                'arabic_explanation': '''جلس ثعلب على جذع شجرة. يستطيع رؤية دجاجة. الدجاجة حزينة. "أنا في مأزق!" قالت الدجاجة. "لا أستطيع الدخول إلى حظيرتي."

"أستطيع المساعدة!" قال الثعلب. أحضر الثعلب صندوقاً كبيراً. تستطيع الدجاجة القفز على الصندوق. الآن تستطيع الدجاجة الدخول إلى الحظيرة!

"أنت الأفضل!" قالت الدجاجة. الثعلب سعيد. استمتعوا كثيراً.''',
                'difficulty': 2,
                'order': 3
            },
            {
                'title': 'The Fun Run',
                'content': '''Ten kids run in the sun. It is a big fun run! Sam is in a red hat. Pam has a big bag. 

"I can run!" said Sam. "I can hop and run!" said Pam.

They run and run. The sun is hot, but it is fun. At the end, Mom and Dad hug Sam and Pam. "You did it!" they said.''',
                'arabic_explanation': '''عشرة أطفال يجرون تحت الشمس. إنه سباق مرح كبير! سام يرتدي قبعة حمراء. بام لديها حقيبة كبيرة.

"أستطيع الجري!" قال سام. "أستطيع القفز والجري!" قالت بام.

يجرون ويجرون. الشمس حارة، لكنه ممتع. في النهاية، أمي وأبي يعانقان سام وبام. "لقد نجحتم!" قالوا.''',
                'difficulty': 1,
                'order': 4
            },
        ]
        
        for story_data in stories_data:
            story_obj, created = CVCStory.objects.get_or_create(
                title=story_data['title'],
                defaults=story_data
            )
            if created:
                self.stdout.write(f'  ✓ {story_data["title"]}')
            else:
                for key, value in story_data.items():
                    setattr(story_obj, key, value)
                story_obj.save()
                self.stdout.write(f'  ↻ {story_data["title"]} (تم التحديث)')
