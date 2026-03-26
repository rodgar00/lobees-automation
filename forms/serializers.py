from rest_framework import serializers
from .models import FormResponse


class Step1Serializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponse
        fields = ["interested", "reschedule", "preferred_date"]


class Step2Serializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponse
        fields = ["proposed_time_ok", "preferred_time", "comments"]


class Step3Serializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponse
        fields = ["final_confirmation", "communication_channel", "notes"]