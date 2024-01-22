import factory
from notes.models import Note


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Sequence(lambda n: f"Note {n}")
    content = factory.Faker("paragraph", nb_sentences=5)

    # We need to save the created date again after model creation because
    # Django's auto-now-add will override anything we pass in as a kwarg
    @factory.post_generation
    def custom_created(obj, create, extracted, **kwargs):
        if extracted:
            obj.created = extracted
            if create:
                obj.save()
