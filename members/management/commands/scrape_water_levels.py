"""Scrape water levels for every state and store them as a new snapshot.

    python manage.py scrape_water_levels              # scrape once
    python manage.py scrape_water_levels --every 60   # keep running, scrape hourly
    python manage.py scrape_water_levels --from-file data/banjir_data.json
                                                      # import a saved scrape (no Chrome needed)

Runs as its own process rather than inside the web server, so the scraper
starts exactly once no matter how many web workers there are, and is never
triggered by migrate/test/check.
"""
import json
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from members.banjir_api import STATES, scrape_state_banjir_data
from members.models import WaterLevel

logger = logging.getLogger(__name__)

FIELDS = [
    "station_id", "station_name", "district", "main_basin", "sub_basin",
    "last_update", "water_level", "normal", "alert", "warning", "danger",
    "state_code",
]


class Command(BaseCommand):
    help = "Scrape water levels for all states and save them to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--every", type=int, metavar="MINUTES",
            help="Keep running and scrape every MINUTES minutes.",
        )
        parser.add_argument(
            "--from-file", metavar="PATH",
            help="Import rows from a JSON file instead of scraping.",
        )
        parser.add_argument(
            "--keep-days", type=int, default=30,
            help="Delete snapshots older than this many days (default 30).",
        )

    def handle(self, *args, **options):
        if options["from_file"]:
            self.import_file(options["from_file"])
            return

        self.scrape_all(options["keep_days"])
        if options["every"]:
            from apscheduler.schedulers.blocking import BlockingScheduler

            scheduler = BlockingScheduler()
            scheduler.add_job(
                self.scrape_all, "interval",
                minutes=options["every"], args=[options["keep_days"]],
            )
            self.stdout.write(f"Scraping every {options['every']} minutes. Ctrl+C to stop.")
            try:
                scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                pass

    def scrape_all(self, keep_days):
        scraped_at = timezone.now()
        saved, failed = 0, []

        for code, _name in STATES:
            # Isolate each state: one failure (site change, timeout) must not
            # discard the other states' data.
            try:
                rows = scrape_state_banjir_data(code)
            except Exception:
                logger.exception("Scraping %s failed", code)
                failed.append(code)
                continue
            if not rows:
                # An empty result usually means the page layout changed.
                # Keep the previous snapshot rather than storing nothing.
                failed.append(code)
                continue
            saved += self.save_rows(rows, scraped_at)

        deleted, _ = WaterLevel.objects.filter(
            scraped_at__lt=timezone.now() - timedelta(days=keep_days)
        ).delete()

        msg = f"Saved {saved} rows for {len(STATES) - len(failed)}/{len(STATES)} states"
        if failed:
            msg += f"; failed: {', '.join(failed)}"
        if deleted:
            msg += f"; pruned {deleted} old rows"
        self.stdout.write(msg)

    def import_file(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                rows = json.load(f)
        except (OSError, ValueError) as e:
            raise CommandError(f"Could not read {path}: {e}")
        count = self.save_rows(rows, timezone.now())
        self.stdout.write(f"Imported {count} rows from {path}")

    @staticmethod
    @transaction.atomic
    def save_rows(rows, scraped_at):
        objs = [
            WaterLevel(scraped_at=scraped_at, **{k: row.get(k, "") for k in FIELDS})
            for row in rows
        ]
        WaterLevel.objects.bulk_create(objs)
        return len(objs)
