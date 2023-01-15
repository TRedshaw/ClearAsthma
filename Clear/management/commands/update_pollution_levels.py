from django.core.management.base import BaseCommand, CommandError

from Clear.models import PollutionLevels


class Command(BaseCommand):
    help = 'Updates pollution levels'


    def handle(self, *args, **options):
        PollutionLevels.update_pollution_levels()
        self.stdout.write(self.style.SUCCESS('Pollution levels successfully updated'))