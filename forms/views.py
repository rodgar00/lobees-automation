import json
import requests

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from .models import FormResponse
from .serializers import Step1Serializer, Step2Serializer, Step3Serializer


N8N_WEBHOOK_FORM1 = "http://n8n.mpforall.com:5678/webhook-test/form1"
N8N_WEBHOOK_FORM2 = "http://n8n.mpforall.com:5678/webhook-test/form2"
N8N_WEBHOOK_FORM3 = "http://n8n.mpforall.com:5678/webhook-test/form3"
BASE_FORM_URL = "https://baleless-otha-soaked.ngrok-free.dev/form"


def send_to_n8n(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=5)
        print("N8N status:", response.status_code)
        print("N8N response:", response.text)
    except Exception as e:
        print("N8N error:", e)


def send_email(email, step):
    url = f"{BASE_FORM_URL}/step{step}/{email}/"
    send_mail(
        subject=f"Formulario paso {step}",
        message=f"Completa aquí: {url}",
        from_email="rodrigo.garcia@estudiante.epsum.school",
        recipient_list=[email],
    )


def get_or_create_lead(email, taskid=None):
    obj, created = FormResponse.objects.get_or_create(lead_email=email)

    if taskid and not obj.taskid:
        obj.taskid = taskid
        obj.save()

    return obj


def form_step1(request, lead_email):
    return render(request, "forms/step1.html", {"lead_email": lead_email})


@csrf_exempt
def submit_step1(request, lead_email):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    obj = get_or_create_lead(lead_email)

    serializer = Step1Serializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    for k, v in serializer.validated_data.items():
        setattr(obj, k, v)

    obj.current_step = 1
    obj.save()

    payload = {
        "lead_email": lead_email,
        "step": 1,
        "status": "pending",
        "data": serializer.validated_data,
        "taskid": obj.taskid
    }

    send_to_n8n(N8N_WEBHOOK_FORM1, payload)
    send_email(lead_email, 2)

    return JsonResponse({"ok": True, "next_step": 2, "taskid": obj.taskid})


def form_step2(request, lead_email):
    return render(request, "forms/step2.html", {"lead_email": lead_email})


@csrf_exempt
def submit_step2(request, lead_email):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    obj = get_object_or_404(FormResponse, lead_email=lead_email)
    if obj.current_step < 1:
        return JsonResponse({"error": "step1 not completed"}, status=400)

    serializer = Step2Serializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    for k, v in serializer.validated_data.items():
        setattr(obj, k, v)

    obj.current_step = 2
    obj.save()

    payload = {
        "lead_email": lead_email,
        "step": 2,
        "status": "pending",
        "data": serializer.validated_data,
        "taskid": obj.taskid
    }

    send_to_n8n(N8N_WEBHOOK_FORM2, payload)
    send_email(lead_email, 3)

    return JsonResponse({"ok": True, "next_step": 3, "taskid": obj.taskid})


def form_step3(request, lead_email):
    return render(request, "forms/step3.html", {"lead_email": lead_email})


@csrf_exempt
def submit_step3(request, lead_email):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    obj = get_object_or_404(FormResponse, lead_email=lead_email)
    if obj.current_step < 2:
        return JsonResponse({"error": "step2 not completed"}, status=400)

    serializer = Step3Serializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    for k, v in serializer.validated_data.items():
        setattr(obj, k, v)

    obj.current_step = 3
    obj.save()

    payload = {
        "lead_email": lead_email,
        "step": 3,
        "status": "completed",
        "data": serializer.validated_data,
        "taskid": obj.taskid
    }

    send_to_n8n(N8N_WEBHOOK_FORM3, payload)
    send_email(lead_email, 3)

    return JsonResponse({"ok": True, "completed": True, "taskid": obj.taskid})


@csrf_exempt
def send_form_email(request):
    if request.method != "POST":
        return JsonResponse({"error": "only POST"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON"}, status=400)

    email = data.get("lead_email")
    step = data.get("step")
    taskid = data.get("taskid")

    if not email or not step or not taskid:
        return JsonResponse({"error": "missing data"}, status=400)

    obj = get_or_create_lead(email, taskid)
    obj.current_step = step
    obj.save()

    send_email(email, step)

    return JsonResponse({
        "sent": True,
        "step": step,
        "taskid": obj.taskid
    })


def pending_leads(request):
    leads = FormResponse.objects.filter(current_step__lt=3)
    return JsonResponse({
        "data": [
            {"email": l.lead_email, "step": l.current_step, "taskid": l.taskid}
            for l in leads
        ]
    })