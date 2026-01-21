from django.shortcuts import render
from .models import Student, LetterProgress, TopGoalUnit
import random
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from django.db import models

@csrf_exempt
def save_progress(request):
    data = json.loads(request.body.decode("utf-8"))
    student_name = data.get("student")
    letter = data.get("letter")
    score = int(data.get("score"))

    student, _ = Student.objects.get_or_create(name=student_name)

    # الحرف السابق المطلوب إنجازه
    previous_letter = chr(ord(letter)-1) if letter != "A" else None

    if previous_letter:
        prev_record = LetterProgress.objects.filter(student=student, letter=previous_letter, passed=True).exists()
        if not prev_record:
            return JsonResponse({"error": "previous_letter_not_passed"}, status=400)

    lp, created = LetterProgress.objects.get_or_create(student=student, letter=letter)

    if score > lp.score:
        lp.score = score

    if score >= 14:   # النجاح
        lp.passed = True

    lp.save()

    return JsonResponse({"status": "ok", "passed": lp.passed})

@csrf_exempt
def speech_check(request):
    audio = request.FILES.get("audio")
    letter = request.POST.get("letter")

    # TODO: لاحقًا تربطه بـ Google STT أو Whisper API
    recognized = letter  
    accuracy = 100

    return JsonResponse({
        "recognized": recognized,
        "accuracy": accuracy,
        "correct": True
    })

def generate_certificate(request, student_id):
    student = Student.objects.get(id=student_id)

    # تحقق هل أكمل A–Z؟
    passed_count = LetterProgress.objects.filter(student=student, passed=True).count()
    if passed_count < 26:
        return HttpResponse("Not finished")

    template = get_template("phonics/certificate_template.html")
    html = template.render({"name": student.name, "date": datetime.now().date()})

    response = HttpResponse(content_type="application/pdf")
    pisa.CreatePDF(html, dest=response)
    return response

def index(request):
    return render(request, "leeters.HTML")

def leaderboard(request):
    data = Student.objects.all().annotate(
        total=models.Sum("letterprogress__score")
    ).order_by("-total")

    return render(request, "phonics/leaderboard.html", {"rows": data})

def letter_data_api(request, letter):
    from .models import Word, QuizQuestion

    words = Word.objects.filter(letter=letter.upper())
    quiz_questions = QuizQuestion.objects.filter(letter=letter.upper())

    data = {
        "letter": letter.upper(),
        "words": [
            {"word": w.word, "arabic": w.arabic, "emoji": w.emoji} for w in words
        ],
        "quiz": [
            {
                "question": q.question,
                "options": q.options,
                "correct_answer": q.correct_answer,
            }
            for q in quiz_questions
        ],
    }
    return JsonResponse(data)


# ============================================
# CVC Words Reading Views
# ============================================

def cvc_reading_view(request):
    """
    الصفحة الرئيسية لقراءة كلمات وجمل CVC
    """
    # التحقق من إتمام جميع الحروف (اختياري - يمكن التحقق في JavaScript)
    return render(request, "phonics/cvc_reading.html")


@csrf_exempt
def get_cvc_words_api(request):
    """
    API لجلب قائمة كلمات CVC
    """
    from .models import CVCWord
    
    words = CVCWord.objects.all().order_by('order')
    data = {
        'words': [
            {
                'id': w.id,
                'word': w.word,
                'arabic_meaning': w.arabic_meaning,
                'image_url': w.image_url,
                'emoji': w.emoji,
                'category': w.category,
                'word_family': w.word_family,
                'vowel_sound': w.vowel_sound,
                'difficulty_level': w.difficulty_level
            }
            for w in words
        ]
    }
    return JsonResponse(data)


@csrf_exempt
def get_cvc_sentences_api(request):
    """
    API لجلب قائمة جمل CVC
    """
    from .models import CVCSentence
    
    sentences = CVCSentence.objects.all().order_by('order', 'difficulty')
    data = [
        {
            'id': s.id,
            'sentence': s.sentence,
            'arabic_translation': s.arabic_translation,
            'difficulty': s.difficulty,
            'time_limit': s.time_limit,
            'category': s.category,
            'quiz_data': s.quiz_data,
            'emoji': s.emoji
        }
        for s in sentences
    ]
    
    return JsonResponse({'sentences': data})


@csrf_exempt
def get_cvc_stories_api(request):
    """
    API لجلب قائمة قصص CVC
    """
    from .models import CVCStory
    
    stories = CVCStory.objects.all().order_by('order', 'difficulty')
    data = [
        {
            'id': s.id,
            'title': s.title,
            'content': s.content,
            'arabic_explanation': s.arabic_explanation,
            'image_url': s.image_url,
            'quiz_data': s.quiz_data,
            'difficulty': s.difficulty
        }
        for s in stories
    ]
    
    return JsonResponse({'stories': data})


@csrf_exempt
def save_cvc_progress_api(request):
    """
    API لحفظ تقدم الطالب في CVC
    """
    from .models import CVCProgress
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    data = json.loads(request.body.decode('utf-8'))
    student_name = data.get('student')
    progress_type = data.get('type')  # 'word', 'sentence', 'story'
    points = int(data.get('points', 0))
    reading_time = data.get('reading_time', None)
    
    # الحصول على الطالب أو إنشاؤه
    student, _ = Student.objects.get_or_create(name=student_name)
    
    # الحصول على تقدم CVC أو إنشاؤه
    cvc_progress, created = CVCProgress.objects.get_or_create(student=student)
    
    # تحديث التقدم حسب النوع
    if progress_type == 'word':
        cvc_progress.update_word_score(points)
    elif progress_type == 'sentence' and reading_time is not None:
        cvc_progress.update_sentence_score(points, float(reading_time))
    elif progress_type == 'story':
        cvc_progress.mark_story_complete()
    
    return JsonResponse({
        'status': 'ok',
        'total_score': cvc_progress.total_score,
        'words_completed': cvc_progress.words_completed,
        'sentences_completed': cvc_progress.sentences_completed,
        'stories_completed': cvc_progress.stories_completed
    })


@csrf_exempt
def check_cvc_pronunciation(request):
    """
    API للتحقق من نطق كلمة CVC
    ملاحظة: حالياً يرجع نتائج تجريبية. لاحقاً يمكن ربطه بـ Speech Recognition API
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    # في المستقبل: استخدام Google Speech-to-Text أو Whisper
    # حالياً: نتائج تجريبية
    target_word = request.POST.get('word', '').upper()
    
    # محاكاة التحقق
    accuracy = 85  # يمكن استخدام speech recognition لاحقاً
    is_correct = True
    
    return JsonResponse({
        'word': target_word,
        'accuracy': accuracy,
        'correct': is_correct,
        'message': 'رائع! نطق ممتاز' if accuracy >= 80 else 'جيد، حاول مرة أخرى'
    })

def top_goal_view(request):
    """
    عرض صفحة Top Goal 6 Unit 1 (التي هي Unit 5 في الكتاب)
    """
    # نفترض أننا نستخدم الوحدة رقم 1 للصف السادس (كما طلب المستخدم)
    # أو نبحث عن الوحدة التي أنشأناها بالعنوان
    unit = TopGoalUnit.objects.filter(grade="Top Goal 6").first()
    
    if not unit:
        # Fallback if DB not populated yet
        return render(request, "phonics/top_goal_6_unit_1.html", {"error": "Unit not found. Please run population script."})

    vocab = unit.vocabularies.all().order_by('order')
    sentences = unit.sentences.all().order_by('order')
    quizzes = unit.quizzes.all().order_by('order')
    
    # Serialize quizzes for JS
    quizzes_json = []
    for q in quizzes:
        quizzes_json.append({
            'id': q.id,
            'question': q.question_text,
            'options': q.options,
            'correct': q.correct_answer,
            'explanation': q.explanation_ar
        })
    
    context = {
        'unit': unit,
        'vocab': vocab,
        'sentences': sentences,
        'quizzes': quizzes,
        'quizzes_json': json.dumps(quizzes_json)
    }
    return render(request, "phonics/top_goal_6_unit_1.html", context)
