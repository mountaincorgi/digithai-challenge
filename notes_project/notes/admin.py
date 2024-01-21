from django.contrib import admin
from notes.models import Note


class NoteAdmin(admin.ModelAdmin):
    fields = ("user", "title", "content", "created", "modified")
    list_display = ("id", "user", "title", "created", "modified")
    list_filter = ("user__username",)
    readonly_fields = ("created", "modified")
    search_fields = ("id", "user__username", "title")


admin.site.register(Note, NoteAdmin)
