import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"User {n}")

    @factory.post_generation
    def custom_password(obj, create, extracted, **kwargs):
        if extracted:
            obj.set_password(extracted)
            if create:
                obj.save()
