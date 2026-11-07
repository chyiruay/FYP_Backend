from django.apps import AppConfig

class MembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'members'
    # The water-level scraper no longer starts here (it ran on every manage.py
    # command and once per web worker). Run it as its own process:
    #   python manage.py scrape_water_levels --every 60
