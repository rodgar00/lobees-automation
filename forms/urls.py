from django.urls import path
from . import views

urlpatterns = [
    path('step1/<str:lead_email>/', views.form_step1),
    path('step1/submit/<str:lead_email>/', views.submit_step1),

    path('step2/<str:lead_email>/', views.form_step2),
    path('step2/submit/<str:lead_email>/', views.submit_step2),

    path('step3/<str:lead_email>/', views.form_step3),
    path('step3/submit/<str:lead_email>/', views.submit_step3),

    path('send-form-email/', views.send_form_email),
]