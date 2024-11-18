import factory

from .models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    category_name = factory.Faker('word')
    description = factory.Faker('sentence')