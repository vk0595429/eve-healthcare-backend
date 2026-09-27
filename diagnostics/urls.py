from django.urls import path

from .views import (
    DiagnosticCentreListCreateView,
    DiagnosticTestListCreateView,
    CentreTestListCreateView
)


urlpatterns = [
    path(
        "centres/",
        DiagnosticCentreListCreateView.as_view(),
        name="centre-list-create",
    ),
    path(
        "tests/",
        DiagnosticTestListCreateView.as_view(),
        name="test-list-create",
    ),
    path(
    "centre-tests/",
    CentreTestListCreateView.as_view(),
    name="centre-test-list-create",
    ),
]