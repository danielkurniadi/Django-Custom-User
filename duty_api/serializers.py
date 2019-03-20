from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import (
    BindingDict, BoundField, JSONBoundField, NestedBoundField, ReturnDict,
    ReturnList
)

from .models import Duty, DutyManager


class DutySerializer(serializers.ModelSerializer):
    """Duty object serializer
    """

    class Meta:
        model = Duty
        fields = (
            'duty_start', 'duty_end', 
            'task1_start', 'task1_end',
            'task2_start', 'task2_end',
            'task3_start', 'task3_end',
        )

    def create(self, validated_data):
        duty = Duty.objects.create(**validated_data)
        return duty

