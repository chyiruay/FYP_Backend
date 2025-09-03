from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from .banjir_api import scrape_state_banjir_data

def start_scheduler():
    print("🔁 Scheduler is starting...")
    scheduler = BackgroundScheduler()

    state_codes = [
        "JHR", "KDH", "KTN", "MLK", "NSN", "PHG", "PRK", "PLS", "PNG",
        "SBH", "SWK", "SGR", "TRG", "KUL", "LBN", "PJY"
    ]

    def job():
        all_data = []
        for code in state_codes:
            print(f"Scraping {code}...")
            state_data = scrape_state_banjir_data(code)
            all_data.extend(state_data)
        with open("data/banjir_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print("✅ JSON updated.")

    # 立即运行一次，然后每小时重复
    scheduler.add_job(
       job,
       'interval',
       hours=1,
        #next_run_time=datetime.now()  # 立即运行
    )

    scheduler.start()
