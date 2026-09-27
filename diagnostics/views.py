from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import DiagnosticCentre, DiagnosticTest,CentreTest
from .serializers import DiagnosticCentreSerializer, DiagnosticTestSerializer,CentreTestSerializer


class DiagnosticCentreListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer
    permission_classes = [IsAuthenticated]


class DiagnosticTestListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer
    permission_classes = [IsAuthenticated]

class CentreTestListCreateView(generics.ListCreateAPIView):
    queryset = CentreTest.objects.all()
    serializer_class = CentreTestSerializer
    permission_classes = [IsAuthenticated]