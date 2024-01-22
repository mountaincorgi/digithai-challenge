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
    title = models.CharField("Title", max_length=140)
    content = models.TextField("Content", blank=True)
    created = models.DateTimeField("Created", blank=True, auto_now_add=True)
    modified = models.DateTimeField(
        "Modified", blank=True, null=True, auto_now=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("note-detail", kwargs={"pk": self.pk})

    @property
    def preview_content(self):
        """Shorten the content shown on certain pages."""

        if len(self.content) > 180:
            return self.content[:177] + "..."
        return self.content

    class Meta:
        verbose_name = "Note"
