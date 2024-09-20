from django.core.management.base import BaseCommand

from api.models import Category


class Command(BaseCommand):
    help = "Initialize the database with default categories and sample"

    def handle(self, *args, **kwargs):

        categories = ["Food", "Travel", "Art & Culture", "Music"]
        for category_name in categories:
            Category.objects.get_or_create(category_name=category_name)

        self.stdout.write(
            self.style.SUCCESS(
                "Database successfully initialized with default data"
            )
        )
