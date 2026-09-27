from rest_framework import serializers

from .models import DiagnosticCentre,DiagnosticTest,CentreTest


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticCentre
        fields = ["id", "name", "location"]

class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        fields = ["id", "name"]

class CentreTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreTest
        fields = ["id", "centre", "test", "price"]