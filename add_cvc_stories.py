"""
Script to populate CVC Stories with professional bilingual content and quizzes.
Run: python add_cvc_stories.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_project.settings')
django.setup()

from phonics.models import CVCStory
import json

def create_stories():
    """إنشاء قصص CVC احترافية مع ترجمة واختبارات"""
    
    # حذف القصص القديمة
    CVCStory.objects.all().delete()
    print("✅ تم حذف القصص القديمة")
    
    stories = [
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
            'quiz_data': json.dumps([
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
                {
                    'question': 'What did the cat see?',
                    'question_ar': 'ماذا رأت القطة؟',
                    'options': ['A dog', 'A rat', 'A bird', 'A fish'],
                    'correct': 1,
                    'feedback_ar': 'أحسنت! رأت القطة فأراً',
                    'feedback_en': 'Well done! The cat saw a rat'
                }
            ]),
            'difficulty': 'easy',
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
            'quiz_data': json.dumps([
                {
                    'question': 'What is up in the sky?',
                    'question_ar': 'ماذا يوجد في السماء؟',
                    'options': ['The moon', 'The sun', 'A cloud', 'A star'],
                    'correct': 1,
                    'feedback_ar': 'صحيح! الشمس مشرقة',
                    'feedback_en': 'Correct! The sun is up'
                },
                {
                    'question': 'Where does Tom run?',
                    'question_ar': 'إلى أين يجري توم؟',
                    'options': ['To school', 'To the park', 'To the bus stop', 'To home'],
                    'correct': 2,
                    'feedback_ar': 'ممتاز! يجري إلى محطة الحافلة',
                    'feedback_en': 'Great! He runs to the bus stop'
                },
                {
                    'question': 'What does Tom eat?',
                    'question_ar': 'ماذا يأكل توم؟',
                    'options': ['A cake', 'A bun', 'An apple', 'A sandwich'],
                    'correct': 1,
                    'feedback_ar': 'رائع! يأكل كعكة',
                    'feedback_en': 'Wonderful! He eats a bun'
                }
            ]),
            'difficulty': 'easy',
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
            'quiz_data': json.dumps([
                {
                    'question': 'What is the dog\'s name?',
                    'question_ar': 'ما اسم الكلب؟',
                    'options': ['Sam', 'Max', 'Bob', 'Rex'],
                    'correct': 1,
                    'feedback_ar': 'صحيح! اسم الكلب ماكس',
                    'feedback_en': 'Correct! The dog\'s name is Max'
                },
                {
                    'question': 'What can Max dig in?',
                    'question_ar': 'فيم يحفر ماكس؟',
                    'options': ['Sand', 'Mud', 'Snow', 'Water'],
                    'correct': 1,
                    'feedback_ar': 'أحسنت! يحفر في الطين',
                    'feedback_en': 'Well done! He digs in the mud'
                },
                {
                    'question': 'What did Max find?',
                    'question_ar': 'ماذا وجد ماكس؟',
                    'options': ['A bone', 'A ball', 'A stick', 'A toy'],
                    'correct': 2,
                    'feedback_ar': 'ممتاز! وجد عصا',
                    'feedback_en': 'Excellent! He found a stick'
                }
            ]),
            'difficulty': 'easy',
            'order': 3
        },
        {
            'title': '🎒 The Red Bag',
            'content': '''This is a red [bag] 🎒.
In the bag, there is a [pen] 🖊️.
There is also a [map] 🗺️ and a [cap] 🧢.
I put my bag on my [lap].
I am ready for my trip! ✈️''',
            'arabic_explanation': '''هذه حقيبة حمراء 🎒
في الحقيبة يوجد قلم 🖊️
يوجد أيضاً خريطة 🗺️ وقبعة 🧢
أضع حقيبتي على حجري
أنا مستعد لرحلتي! ✈️''',
            'image_url': 'https://images.unsplash.com/photo-1577733966973-d680bffd2e80?w=400',
            'quiz_data': json.dumps([
                {
                    'question': 'What color is the bag?',
                    'question_ar': 'ما لون الحقيبة؟',
                    'options': ['Blue', 'Red', 'Green', 'Yellow'],
                    'correct': 1,
                    'feedback_ar': 'رائع! الحقيبة حمراء',
                    'feedback_en': 'Great! The bag is red'
                },
                {
                    'question': 'What is in the bag?',
                    'question_ar': 'ماذا في الحقيبة؟',
                    'options': ['A book', 'A pen', 'A phone', 'A cup'],
                    'correct': 1,
                    'feedback_ar': 'صحيح! يوجد قلم',
                    'feedback_en': 'Correct! There is a pen'
                },
                {
                    'question': 'Where is the person going?',
                    'question_ar': 'إلى أين يذهب الشخص؟',
                    'options': ['On a trip', 'To bed', 'To the park', 'To school'],
                    'correct': 0,
                    'feedback_ar': 'ممتاز! ذاهب في رحلة',
                    'feedback_en': 'Excellent! Going on a trip'
                }
            ]),
            'difficulty': 'easy',
            'order': 4
        },
        {
            'title': '🦊 The Fox and the Box',
            'content': '''There is a [fox] 🦊 in the woods.
The fox sees a [box] 📦.
The fox jumps on top of the box.
Inside the box is a [sock] 🧦!
The fox puts on the sock and looks funny! 😄''',
            'arabic_explanation': '''يوجد ثعلب 🦊 في الغابة
يرى الثعلب صندوقاً 📦
يقفز الثعلب فوق الصندوق
داخل الصندوق جورب 🧦!
يرتدي الثعلب الجورب ويبدو مضحكاً! 😄''',
            'image_url': 'https://images.unsplash.com/photo-1460999158988-6f0380f81f4d?w=400',
            'quiz_data': json.dumps([
                {
                    'question': 'Where is the fox?',
                    'question_ar': 'أين الثعلب؟',
                    'options': ['In the city', 'In the woods', 'In a house', 'On a farm'],
                    'correct': 1,
                    'feedback_ar': 'صحيح! في الغابة',
                    'feedback_en': 'Correct! In the woods'
                },
                {
                    'question': 'What does the fox see?',
                    'question_ar': 'ماذا يرى الثعلب؟',
                    'options': ['A bag', 'A box', 'A ball', 'A book'],
                    'correct': 1,
                    'feedback_ar': 'أحسنت! يرى صندوقاً',
                    'feedback_en': 'Well done! He sees a box'
                },
                {
                    'question': 'What is inside the box?',
                    'question_ar': 'ماذا يوجد داخل الصندوق؟',
                    'options': ['A hat', 'A shoe', 'A sock', 'A glove'],
                    'correct': 2,
                    'feedback_ar': 'ممتاز! يوجد جورب',
                    'feedback_en': 'Excellent! There is a sock'
                }
            ]),
            'difficulty': 'medium',
            'order': 5
        },
        {
            'title': '🌙 Bed Time',
            'content': '''It is night. The moon 🌙 is up.
Sam is in his [bed] 🛏️.
He has a [red] teddy bear 🧸.
Sam [said] "Good night" to his bear.
Sam closes his eyes and goes to sleep. 😴''',
            'arabic_explanation': '''حل الليل. القمر 🌙 مشرق
سام في سريره 🛏️
لديه دب أحمر 🧸
قال سام "تصبح على خير" لدبه
يغمض سام عينيه وينام 😴''',
            'image_url': 'https://images.unsplash.com/photo-1540518614846-7eded433c457?w=400',
            'quiz_data': json.dumps([
                {
                    'question': 'When is it?',
                    'question_ar': 'متى يحدث هذا؟',
                    'options': ['Morning', 'Afternoon', 'Night', 'Noon'],
                    'correct': 2,
                    'feedback_ar': 'صحيح! في الليل',
                    'feedback_en': 'Correct! It is night'
                },
                {
                    'question': 'What does Sam have?',
                    'question_ar': 'ماذا لدى سام؟',
                    'options': ['A car', 'A teddy bear', 'A ball', 'A book'],
                    'correct': 1,
                    'feedback_ar': 'رائع! لديه دب',
                    'feedback_en': 'Great! He has a teddy bear'
                },
                {
                    'question': 'What color is the bear?',
                    'question_ar': 'ما لون الدب؟',
                    'options': ['Blue', 'Red', 'Brown', 'White'],
                    'correct': 1,
                    'feedback_ar': 'ممتاز! الدب أحمر',
                    'feedback_en': 'Excellent! The bear is red'
                }
            ]),
            'difficulty': 'easy',
            'order': 6
        }
    ]
    
    # إنشاء القصص
    created_count = 0
    for story_data in stories:
        story, created = CVCStory.objects.get_or_create(
            title=story_data['title'],
            defaults=story_data
        )
        if created:
            created_count += 1
            print(f"✅ تم إنشاء القصة: {story.title}")
        else:
            print(f"ℹ️  القصة موجودة بالفعل: {story.title}")
    
    print(f"\n🎉 تم إنشاء {created_count} قصة جديدة!")
    print(f"📚 إجمالي القصص في قاعدة البيانات: {CVCStory.objects.count()}")

if __name__ == '__main__':ِِ
    create_stories()
