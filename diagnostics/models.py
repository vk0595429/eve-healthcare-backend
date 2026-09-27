from django.db import models


class DiagnosticCentre(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DiagnosticTest(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class CentreTest(models.Model):
    centre = models.ForeignKey(
        DiagnosticCentre,
        on_delete=models.CASCADE,
        related_name="centre_tests",
    )
    test = models.ForeignKey(
        DiagnosticTest,
        on_delete=models.CASCADE,
        related_name="centre_tests",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["centre", "test"],
                name="unique_centre_test",
            )
        ]

    def __str__(self):
        return f"{self.centre.name} - {self.test.name}"