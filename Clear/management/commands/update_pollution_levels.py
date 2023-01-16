from django.core.management.base import BaseCommand, CommandError

from Clear.models import PollutionLevels


# Add a custom Command for manage.py to update pollution levels
class Command(BaseCommand):
    help = 'Updates pollution levels'


    def handle(self, *args, **options):
        # Call the class method to update pollution levels from the Air Quality API
        PollutionLevels.update_pollution_levels()
        self.stdout.write(self.style.SUCCESS('Pollution levels successfully updated'))
        return
    