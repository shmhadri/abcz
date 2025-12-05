from django.shortcuts import render
from .models import Student, LetterProgress
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
