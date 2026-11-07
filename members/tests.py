import json
import tempfile
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from members.models import WaterLevel


def make_row(station_id="S1", state="JHR", level="1.00"):
    return {
        "station_id": station_id, "station_name": f"Station {station_id}",
        "district": "D", "main_basin": "B", "sub_basin": "SB",
        "last_update": "01/01/2026 10:00", "water_level": level,
        "normal": "1", "alert": "2", "warning": "3", "danger": "4",
        "state_code": state,
    }


class WaterLevelAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user)

    def test_returns_only_latest_snapshot_for_state(self):
        old = timezone.now() - timedelta(hours=1)
        new = timezone.now()
        WaterLevel.objects.create(scraped_at=old, **make_row("S1", level="1.00"))
        WaterLevel.objects.create(scraped_at=new, **make_row("S1", level="2.00"))
        WaterLevel.objects.create(scraped_at=new, **make_row("K1", state="KDH"))

        res = self.client.get("/api/water-level/", {"state": "JHR"})

        self.assertEqual(res.status_code, 200)
        self.assertEqual([r["water_level"] for r in res.json()], ["2.00"])

    def test_no_data_returns_empty_list(self):
        res = self.client.get("/api/water-level/", {"state": "JHR"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_state_is_required(self):
        res = self.client.get("/api/water-level/")
        self.assertEqual(res.status_code, 400)

    def test_is_public(self):
        WaterLevel.objects.create(**make_row())
        res = APIClient().get("/api/water-level/", {"state": "JHR"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_state_list_is_public(self):
        res = APIClient().get("/api/states/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 16)


class ScrapeCommandTests(TestCase):
    def run_command(self, *args):
        out = StringIO()
        call_command("scrape_water_levels", *args, stdout=out)
        return out.getvalue()

    def test_import_from_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([make_row("S1"), make_row("S2")], f)

        out = self.run_command("--from-file", f.name)

        self.assertIn("Imported 2 rows", out)
        self.assertEqual(WaterLevel.objects.count(), 2)

    @mock.patch("members.management.commands.scrape_water_levels.scrape_state_banjir_data")
    def test_one_failing_state_does_not_stop_others(self, scrape):
        def fake(code):
            if code == "KDH":
                raise RuntimeError("site down")
            return [make_row(f"{code}-1", state=code)]
        scrape.side_effect = fake

        out = self.run_command()

        self.assertIn("failed: KDH", out)
        self.assertEqual(WaterLevel.objects.count(), 15)
        self.assertFalse(WaterLevel.objects.filter(state_code="KDH").exists())

    @mock.patch("members.management.commands.scrape_water_levels.scrape_state_banjir_data")
    def test_empty_scrape_keeps_previous_snapshot(self, scrape):
        WaterLevel.objects.create(scraped_at=timezone.now() - timedelta(hours=1), **make_row())
        scrape.return_value = []

        self.run_command()

        self.assertEqual(WaterLevel.objects.count(), 1)

    @mock.patch("members.management.commands.scrape_water_levels.scrape_state_banjir_data")
    def test_prunes_old_snapshots(self, scrape):
        WaterLevel.objects.create(scraped_at=timezone.now() - timedelta(days=40), **make_row("OLD"))
        scrape.return_value = [make_row("NEW")]

        self.run_command("--keep-days", "30")

        self.assertFalse(WaterLevel.objects.filter(station_id="OLD").exists())
