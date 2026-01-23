"""
Phonics App Views - SECURED & OPTIMIZED
Comprehensive security improvements:
- Removed csrf_exempt for internal APIs  
- Added proper error handling and validation
- Implemented get_object_or_404 for safety
- Added require_http_methods decorators
- Improved database query optimization
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt  # Only for external APIs
from django.template.loader import get_template
from django.db import models
from django.core.exceptions import ValidationError
from xhtml2pdf import pisa
from datetime import datetime
import json

from .models import (
    Student, LetterProgress, TopGoalUnit,
    CVCWord, CVCSentence, CVCStory, CVCProgress
)


# ============================================
# HELPER FUNCTIONS
# ============================================

def parse_json_safely(request):
    """
    Safely parse JSON from request body with error handling
    Returns (data, error_response)
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        return data, None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, JsonResponse(
            {'error': 'Invalid JSON format', 'details': str(e)},
            status=400
        )
    except Exception as e:
        return None, JsonResponse(
            {'error': 'Failed to parse request', 'details': str(e)},
            status=400
        )


def validate_score(score_str, min_val=0, max_val=100):
    """
    Validate and convert score to integer
    Returns (score, error_response)
    """
    try:
        score = int(score_str)
        if not (min_val <= score <= max_val):
            return None, JsonResponse(
                {'error': f'Score must be between {min_val} and {max_val}'},
                status=400
            )
        return score, None
    except (ValueError, TypeError):
        return None, JsonResponse(
            {'error': 'Invalid score format. Must be an integer.'},
            status=400
        )


# ============================================
# LETTER PROGRESS VIEWS (CSRF Protected)
# ============================================

@require_POST
def save_progress(request):
    """
    Save student letter progress with CSRF protection
    Expected JSON: {student, letter, score}
    """
    data, error = parse_json_safely(request)
    if error:
        return error
    
    # Validate required fields
    student_name = data.get("student")
    letter = data.get("letter")
    score_raw = data.get("score")
    
    if not all([student_name, letter, score_raw is not None]):
        return JsonResponse(
            {'error': 'Missing required fields: student, letter, score'},
            status=400
        )
    
    # Validate score
    score, error = validate_score(score_raw, min_val=0, max_val=20)
    if error:
        return error
    
    # Validate letter format
    if not (isinstance(letter, str) and len(letter) == 1 and letter.isalpha()):
        return JsonResponse(
            {'error': 'Letter must be a single alphabetic character'},
            status=400
        )
    
    letter = letter.upper()
    
    try:
        # Get or create student
        student, _ = Student.objects.get_or_create(name=student_name)
        
        # Check previous letter requirement
        if letter != "A":
            previous_letter = chr(ord(letter) - 1)
            prev_passed = LetterProgress.objects.filter(
                student=student,
                letter=previous_letter,
                passed=True
            ).exists()
            
            if not prev_passed:
                return JsonResponse({
                    "error": "previous_letter_not_passed",
                    "message": f"Please complete letter {previous_letter} first",
                    "required_letter": previous_letter
                }, status=400)
        
        # Get or create progress
        lp, created = LetterProgress.objects.get_or_create(
            student=student,
            letter=letter
        )
        
        # Update score if improved
        if score > lp.score:
            lp.score = score
        
        # Mark as passed if score >= 14
        if score >= 14:
            lp.passed = True
        
        lp.save()
        
        return JsonResponse({
            "status": "ok",
            "passed": lp.passed,
            "score": lp.score,
            "created": created
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Database error', 'details': str(e)},
            status=500
        )


@csrf_exempt  # External API - consider adding API key authentication
@require_POST
def speech_check(request):
    """
    Check pronunciation (placeholder for future Speech-to-Text integration)
    TODO: Integrate Google STT or Whisper API
    """
    try:
        audio = request.FILES.get("audio")
        letter = request.POST.get("letter", "").strip()
        
        if not letter:
            return JsonResponse({'error': 'Letter parameter required'}, status=400)
        
        # TODO: Implement actual speech recognition
        # For now, return mock data
        recognized = letter.upper()
        accuracy = 100
        
        return JsonResponse({
            "recognized": recognized,
            "accuracy": accuracy,
            "correct": True,
            "message": "Speech recognition will be implemented soon"
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Speech check failed', 'details': str(e)},
            status=500
        )


@require_GET
def generate_certificate(request, student_id):
    """
    Generate PDF certificate for students who completed A-Z
    """
    try:
        # Use get_object_or_404 for proper 404 handling
        student = get_object_or_404(Student, id=student_id)
        
        # Check if completed all 26 letters
        passed_count = LetterProgress.objects.filter(
            student=student,
            passed=True
        ).count()
        
        if passed_count < 26:
            return JsonResponse({
                'error': 'Certificate not available',
                'message': f'Complete all 26 letters first. Progress: {passed_count}/26',
                'progress': passed_count,
                'required': 26
            }, status=400)
        
        # Generate PDF
        template = get_template("phonics/certificate_template.html")
        context = {
            "name": student.name,
            "date": datetime.now().date(),
            "total_score": LetterProgress.objects.filter(
                student=student
            ).aggregate(models.Sum('score'))['score__sum'] or 0
        }
        html = template.render(context)
        
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="certificate_{student.name}.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return JsonResponse(
                {'error': 'PDF generation failed'},
                status=500
            )
        
        return response
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Certificate generation failed', 'details': str(e)},
            status=500
        )


# ============================================
# GENERAL VIEWS
# ============================================

@require_GET
def index(request):
    """Home page - letters overview"""
    return render(request, "letters.html")


@require_GET
def leaderboard(request):
    """Display student leaderboard ordered by total score"""
    try:
        # Optimized query with annotation
        students = Student.objects.annotate(
            total=models.Sum("letterprogress__score"),
            passed_letters=models.Count(
                "letterprogress",
                filter=models.Q(letterprogress__passed=True)
            )
        ).filter(
            total__isnull=False
        ).order_by("-total")[:50]  # Limit to top 50
        
        return render(request, "phonics/leaderboard.html", {"rows": students})
        
    except Exception as e:
        return render(request, "phonics/leaderboard.html", {
            "rows": [],
            "error": "Failed to load leaderboard"
        })


@require_GET
def letter_data_api(request, letter):
    """
    Get words and quiz questions for a specific letter
    NOTE: This function is currently disabled - Word and QuizQuestion models don't exist
    TODO: Implement using actual models or remove if not needed
    """
    return JsonResponse({
        'error': 'This endpoint is not yet implemented',
        'message': 'Word and QuizQuestion models need to be created first',
        'letter': letter.upper()
    }, status=501)  # 501 Not Implemented


# ============================================
# CVC READING VIEWS
# ============================================

@require_GET
def cvc_reading_view(request):
    """Main CVC reading page"""
    return render(request, "phonics/cvc_reading.html")


@require_GET
def get_cvc_words_api(request):
    """
    Get all CVC words - CSRF Protected (internal use only)
    """
    try:
        words = CVCWord.objects.all().order_by('order').only(
            'id', 'word', 'arabic_meaning', 'emoji', 'category',
            'word_family', 'vowel_sound', 'difficulty_level', 'image_url'
        )
        
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
            ],
            'count': words.count()
        }
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Failed to fetch CVC words', 'details': str(e)},
            status=500
        )


@require_GET
def get_cvc_sentences_api(request):
    """Get all CVC sentences"""
    try:
        sentences = CVCSentence.objects.all().order_by('order', 'difficulty').only(
            'id', 'sentence', 'arabic_translation', 'difficulty',
            'time_limit', 'category', 'quiz_data', 'emoji'
        )
        
        data = {
            'sentences': [
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
            ],
            'count': sentences.count()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Failed to fetch CVC sentences', 'details': str(e)},
            status=500
        )


@require_GET
def get_cvc_stories_api(request):
    """Get all CVC stories"""
    try:
        stories = CVCStory.objects.all().order_by('order', 'difficulty').only(
            'id', 'title', 'content', 'arabic_explanation',
            'image_url', 'quiz_data', 'difficulty'
        )
        
        data = {
            'stories': [
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
            ],
            'count': stories.count()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Failed to fetch CVC stories', 'details': str(e)},
            status=500
        )


@require_POST
def save_cvc_progress_api(request):
    """
    Save CVC progress with proper validation
    """
    data, error = parse_json_safely(request)
    if error:
        return error
    
    try:
        # Validate required fields
        student_name = data.get('student')
        progress_type = data.get('type')
        points_raw = data.get('points', 0)
        
        if not all([student_name, progress_type]):
            return JsonResponse(
                {'error': 'Missing required fields: student, type'},
                status=400
            )
        
        # Validate type
        valid_types = ['word', 'sentence', 'story']
        if progress_type not in valid_types:
            return JsonResponse(
                {'error': f'Invalid type. Must be one of: {valid_types}'},
                status=400
            )
        
        # Validate points
        points, error = validate_score(points_raw, min_val=0, max_val=1000)
        if error:
            return error
        
        # Get or create student
        student, _ = Student.objects.get_or_create(name=student_name)
        
        # Get or create CVC progress
        cvc_progress, created = CVCProgress.objects.get_or_create(student=student)
        
        # Update progress based on type
        if progress_type == 'word':
            cvc_progress.update_word_score(points)
        elif progress_type == 'sentence':
            reading_time = data.get('reading_time')
            if reading_time is not None:
                try:
                    reading_time = float(reading_time)
                    cvc_progress.update_sentence_score(points, reading_time)
                except (ValueError, TypeError):
                    return JsonResponse(
                        {'error': 'Invalid reading_time format. Must be a number.'},
                        status=400
                    )
            else:
                cvc_progress.update_sentence_score(points, 0.0)
        elif progress_type == 'story':
            cvc_progress.mark_story_complete()
        
        return JsonResponse({
            'status': 'ok',
            'total_score': cvc_progress.total_score,
            'words_completed': cvc_progress.words_completed,
            'sentences_completed': cvc_progress.sentences_completed,
            'stories_completed': cvc_progress.stories_completed,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Failed to save progress', 'details': str(e)},
            status=500
        )


@csrf_exempt  # External API - consider adding API key
@require_POST
def check_cvc_pronunciation(request):
    """
    Check CVC word pronunciation (placeholder)
    TODO: Integrate Speech Recognition API
    """
    try:
        target_word = request.POST.get('word', '').strip().upper()
        
        if not target_word:
            return JsonResponse({'error': 'Word parameter required'}, status=400)
        
        # Mock response - replace with actual speech recognition
        accuracy = 85
        is_correct = True
        
        return JsonResponse({
            'word': target_word,
            'accuracy': accuracy,
            'correct': is_correct,
            'message': 'رائع! نطق ممتاز' if accuracy >= 80 else 'جيد، حاول مرة أخرى'
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Pronunciation check failed', 'details': str(e)},
            status=500
        )


# ============================================
# TOP GOAL VIEWS
# ============================================

@require_GET
def top_goal_view(request):
    """
    Top Goal 6 Unit 1 view with optimized queries
    """
    try:
        # Optimized query with prefetch_related
        unit = TopGoalUnit.objects.filter(
            grade="Top Goal 6"
        ).prefetch_related(
            'vocabularies',
            'sentences',
            'quizzes'
        ).first()
        
        if not unit:
            return render(request, "phonics/top_goal_6_unit_1.html", {
                "error": "Unit not found. Please run: python manage.py populate_topgoal_unit5"
            })
        
        # Get related data (already prefetched)
        vocab = unit.vocabularies.all().order_by('order')
        sentences = unit.sentences.all().order_by('order')
        quizzes = unit.quizzes.all().order_by('order')
        
        # Serialize quizzes for JavaScript
        quizzes_json = [
            {
                'id': q.id,
                'question': q.question_text,
                'options': q.options,
                'correct': q.correct_answer,
                'explanation': q.explanation_ar
            }
            for q in quizzes
        ]
        
        context = {
            'unit': unit,
            'vocab': vocab,
            'sentences': sentences,
            'quizzes': quizzes,
            'quizzes_json': json.dumps(quizzes_json)
        }
        
        return render(request, "phonics/top_goal_6_unit_1.html", context)
        
    except Exception as e:
        return render(request, "phonics/top_goal_6_unit_1.html", {
            "error": "Failed to load unit data",
            "details": str(e)
        })
