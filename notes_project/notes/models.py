from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Note(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes",
        verbose_name="User",
    )
    title = models.CharField("Title", max_length=255)
    content = models.TextField("Content", blank=True)
    created = models.DateTimeField("Created", blank=True, auto_now_add=True)
    modified = models.DateTimeField(
        "Modified", blank=True, null=True, auto_now=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("note-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Note"