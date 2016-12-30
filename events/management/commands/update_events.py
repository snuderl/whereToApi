from django.core.management.base import BaseCommand, CommandError
from events.fb import fetch_all_events

class Command(BaseCommand):
  help = 'Closes the specified poll for voting'

  def add_arguments(self, parser):
      parser.add_argument('token', type=str)

  def handle(self, *args, **options):
    token = options['token']
    fetch_all_events(token)

