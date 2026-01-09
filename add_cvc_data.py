"""
سكريبت لإضافة بيانات CVC تجريبية
"""
from phonics.models import CVCWord, CVCSentence, CVCStory

# حذف البيانات القديمة
CVCWord.objects.all().delete()
CVCSentence.objects.all().delete()
CVCStory.objects.all().delete()

# ============================================
# إضافة 20 كلمة CVC
# ============================================
words_data = [
    {"word": "CAT", "arabic": "قطة", "category": "animals", "difficulty": 1, "order": 1, "image": "https://em-content.zobj.net/source/apple/391/cat_1f408.png"},
    {"word": "BAT", "arabic": "خفاش", "category": "animals", "difficulty": 1, "order": 2, "image": "https://em-content.zobj.net/source/apple/391/bat_1f987.png"},
    {"word": "RAT", "arabic": "فأر", "category": "animals", "difficulty": 1, "order": 3, "image": "https://em-content.zobj.net/source/apple/391/rat_1f400.png"},
    {"word": "MAT", "arabic": "سجادة", "category": "objects", "difficulty": 1, "order": 4, "image": "https://em-content.zobj.net/source/apple/391/door_1fa90.png"},
    {"word": "HAT", "arabic": "قبعة", "category": "clothes", "difficulty": 1, "order": 5, "image": "https://em-content.zobj.net/source/apple/391/top-hat_1f3a9.png"},
    
    {"word": "DOG", "arabic": "كلب", "category": "animals", "difficulty": 1, "order": 6, "image": "https://em-content.zobj.net/source/apple/391/dog_1f415.png"},
    {"word": "LOG", "arabic": "جذع شجرة", "category": "nature", "difficulty": 2, "order": 7, "image": "https://em-content.zobj.net/source/apple/391/wood_1fab5.png"},
    {"word": "FOG", "arabic": "ضباب", "category": "nature", "difficulty": 2, "order": 8, "image": "https://em-content.zobj.net/source/apple/391/fog_1f32b-fe0f.png"},
    
    {"word": "BIG", "arabic": "كبير", "category": "adjectives", "difficulty": 1, "order": 9, "image": "https://em-content.zobj.net/source/apple/391/elephant_1f418.png"},
    {"word": "PIG", "arabic": "خنزير", "category": "animals", "difficulty": 1, "order": 10, "image": "https://em-content.zobj.net/source/apple/391/pig_1f416.png"},
    
    {"word": "CUP", "arabic": "كوب", "category": "objects", "difficulty": 1, "order": 11, "image": "https://em-content.zobj.net/source/apple/391/teacup-without-handle_1f375.png"},
    {"word": "PUP", "arabic": "جرو", "category": "animals", "difficulty": 2, "order": 12, "image": "https://em-content.zobj.net/source/apple/391/dog-face_1f436.png"},
    
    {"word": "SUN", "arabic": "شمس", "category": "nature", "difficulty": 1, "order": 13, "image": "https://em-content.zobj.net/source/apple/391/sun_2600-fe0f.png"},
    {"word": "BUS", "arabic": "حافلة", "category": "vehicles", "difficulty": 1, "order": 14, "image": "https://em-content.zobj.net/source/apple/391/bus_1f68c.png"},
    {"word": "NUT", "arabic": "جوزة", "category": "food", "difficulty": 2, "order": 15, "image": "https://em-content.zobj.net/source/apple/391/peanuts_1f95c.png"},
    
    {"word": "BED", "arabic": "سرير", "category": "objects", "difficulty": 1, "order": 16, "image": "https://em-content.zobj.net/source/apple/391/bed_1f6cf-fe0f.png"},
    {"word": "RED", "arabic": "أحمر", "category": "colors", "difficulty": 1, "order": 17, "image": "https://em-content.zobj.net/source/apple/391/red-heart_2764-fe0f.png"},
    {"word": "PEN", "arabic": "قلم", "category": "objects", "difficulty": 1, "order": 18, "image": "https://em-content.zobj.net/source/apple/391/pen_1f58a-fe0f.png"},
    
    {"word": "TOP", "arabic": "قمة", "category": "objects", "difficulty": 2, "order": 19, "image": "https://em-content.zobj.net/source/apple/391/upwards-button_1f53c.png"},
    {"word": "POT", "arabic": "وعاء", "category": "objects", "difficulty": 2, "order": 20, "image": "https://em-content.zobj.net/source/apple/391/cooking_1f373.png"},
]

for word_data in words_data:
    CVCWord.objects.create(
        word=word_data["word"],
        arabic_meaning=word_data["arabic"],
        category=word_data["category"],
        difficulty_level=word_data["difficulty"],
        order=word_data["order"],
        image_url=word_data["image"]
    )

print(f"✅ تم إضافة {len(words_data)} كلمة CVC")

# ============================================
# إضافة جمل CVC
# ============================================
sentences_data = [
    {"sentence": "The cat sat on the mat.", "arabic": "القطة جلست على السجادة.", "difficulty": 1, "time": 30, "order": 1},
    {"sentence": "A big dog ran to the log.", "arabic": "كلب كبير ركض إلى الجذع.", "difficulty": 1, "time": 30, "order": 2},
    {"sentence": "I see a red pen on the bed.", "arabic": "أرى قلماً أحمراً على السرير.", "difficulty": 2, "time": 35, "order": 3},
    {"sentence": "The sun is hot.", "arabic": "الشمس حارة.", "difficulty": 1, "time": 20, "order": 4},
    {"sentence": "A rat hid in a pot.", "arabic": "فأر اختبأ في وعاء.", "difficulty": 2, "time": 25, "order": 5},
    {"sentence": "Put on your hat and get in the bus.", "arabic": "ضع قبعتك واركب الحافلة.", "difficulty": 3, "time": 40, "order": 6},
    {"sentence": "The pig is big.", "arabic": "الخنزير كبير.", "difficulty": 1, "time": 20, "order": 7},
    {"sentence": "I can see fog on the top.", "arabic": "أستطيع رؤية الضباب على القمة.", "difficulty": 3, "time": 35, "order": 8},
]

for sent_data in sentences_data:
    CVCSentence.objects.create(
        sentence=sent_data["sentence"],
        arabic_translation=sent_data["arabic"],
        difficulty=sent_data["difficulty"],
        time_limit=sent_data["time"],
        order=sent_data["order"]
    )

print(f"✅ تم إضافة {len(sentences_data)} جملة CVC")

# ============================================
# إضافة قصص CVC
# ============================================
stories_data = [
    {
        "title": "القطة والفأر",
        "content": "A cat ran. A rat hid. The cat sat. The rat is safe.",
        "arabic": "قطة ركضت. فأر اختبأ. القطة جلست. الفأر آمن الآن.",
        "image": "https://em-content.zobj.net/source/apple/391/cat-face_1f431.png",
        "difficulty": 1,
        "order": 1
    },
    {
        "title": "الكلب الكبير",
        "content": "I see a big dog. The dog can run. The dog sat on a log.",
        "arabic": "أرى كلباً كبيراً. الكلب يستطيع الركض. الكلب جلس على جذع.",
        "image": "https://em-content.zobj.net/source/apple/391/dog-face_1f436.png",
        "difficulty": 1,
        "order": 2
    },
    {
        "title": "يوم مشمس",
        "content": "The sun is hot. I put on my hat. I get in the bus. I go to the top.",
        "arabic": "الشمس حارة. أضع قبعتي. أركب الحافلة. أذهب إلى القمة.",
        "image": "https://em-content.zobj.net/source/apple/391/sun-with-face_1f31e.png",
        "difficulty": 2,
        "order": 3
    },
]

for story_data in stories_data:
    CVCStory.objects.create(
        title=story_data["title"],
        content=story_data["content"],
        arabic_explanation=story_data["arabic"],
        image_url=story_data["image"],
        difficulty=story_data["difficulty"],
        order=story_data["order"]
    )

print(f"✅ تم إضافة {len(stories_data)} قصة CVC")

print("\n🎉 تم إضافة جميع البيانات التجريبية بنجاح!")
