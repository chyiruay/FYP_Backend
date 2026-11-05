# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The backend for a flood-warning app. It serves **two different
interfaces over the same models**:

- a **server-rendered Django web UI** (23 templates) for staff — donations, categories,
  locations, shelters and users, each with full CRUD
- a **REST API** under `/api/` (Django REST Framework, token auth) consumed by the Flutter
  mobile app in the sibling `FYP_Frontend` repo

Django 5.1 + DRF. The mobile app is the main product; the web UI is the admin surface.

**Change both when you change a model.** `members/views.py` (356 lines, web) and
`members/api_views.py` (201 lines, API) are independent code paths over the same tables.
Neither calls the other.

## Security: things already burned

- **The old `SECRET_KEY` sat in a public repo and must never be reused.** `settings.py` now
  reads `DJANGO_SECRET_KEY` from the environment with a throwaway dev fallback. Anything
  deployed must set the env var.
- **`db.sqlite3` is committed in 5 historical commits.** It is now untracked and `.gitignore`d,
  but the historical copies remain — they hold 10 user rows (confirmed fabricated). Removing
  them from history needs `git filter-repo`.
- `DEBUG` and `ALLOWED_HOSTS` now come from env too. `"*"` was removed from `ALLOWED_HOSTS` —
  it accepts any `Host` header.

Never commit a real key, a database, or a `.env` here again. There is now a `.gitignore`;
there wasn't one before, which is exactly how the database got committed.

## The app layout is misleading

| App | What you'd expect | What's actually there |
|---|---|---|
| `members` | membership | **everything** — `CustomUser`, all models, both view layers, the API |
| `accounts` | the user model | almost empty: one `SignUpView`, a form, a 3-line `models.py` |
| `flood` | flood logic | the Django project package — `settings.py`, root `urls.py` |

`AUTH_USER_MODEL = 'members.CustomUser'`, **not** `accounts`. The `accounts` app only
contributes `/accounts/signup/` and otherwise defers to `django.contrib.auth.urls`.

`flood/urls.py` still carries the stock `my_tennis_club` docstring from the tutorial this
was started from. It routes `""` to `members.urls`, so the **web UI lives at the site root**
and the API hangs off `/api/` inside it.

`LOGIN_REDIRECT_URL = "donation"` — the web UI's landing page is the donation list.

## Water level data is scraped, not fetched

`members/banjir_api.py` is named like an API client but is a **Selenium scraper**:

```python
driver = webdriver.Chrome(options=options)   # headless Chrome
driver.get(f"https://publicinfobanjir.water.gov.my/aras-air/data-paras-air/?state={state_code}")
time.sleep(3)                                # fixed wait, not a wait-for-element
soup = BeautifulSoup(html, "html.parser")
rows = soup.find_all("tr", class_="item")    # breaks if they change the markup
```

Consequences you must plan around:

- **It needs Chrome and a matching chromedriver on the host.** This is the single biggest
  obstacle to deploying the backend anywhere.
- **It takes at least 3 seconds per request** and runs inside the request/response cycle, so
  `WaterLevelAPI` and `BanjirStateAPIView` are slow endpoints by construction. Nothing is
  cached and nothing is queued.
- **It breaks silently when the government site changes its HTML.** The `len(cols) >= 12`
  check means a layout change yields an empty list rather than an error.
- Column positions are hardcoded by index (`cols[7]` is the water level).

If this needs to be made robust, the fix is a scheduled job that scrapes into the database
plus endpoints that read from it — not a faster scrape.

The Flutter app also calls `https://api.data.gov.my/weather` **directly**, bypassing this
backend entirely. So the project has two external data sources reached two different ways.

## API authentication

`REST_FRAMEWORK` sets `TokenAuthentication` and a global default of `IsAuthenticated`, so
**new API views are authenticated unless they opt out**. The ones that opt out:

- `RegisterView`, `LoginView` — `AllowAny`, necessarily
- `ShelterListAPIView` — `AllowAny`, and it returns **every shelter with no filtering**
- `UserListView` — `IsAdminUser`

Clients send `Authorization: Token <key>`. The app stores the token in `SharedPreferences`
under `auth_token`.

`corsheaders` is installed and its middleware is first in `MIDDLEWARE`, but **no
`CORS_ALLOWED_ORIGINS` is configured** — so it is effectively doing nothing. That's harmless
for a native mobile client (CORS is a browser rule) but will confuse anyone who assumes it's
been set up.

## Shelters have coordinates but no spatial queries

`Shelter` stores `latitude`/`longitude` as plain `FloatField`s, and `ShelterListAPIView`
returns all of them. **Distance is calculated client-side** — there's a haversine in
`lib/screens/map_page.dart` in the Flutter repo.

So "nearest open shelter" is currently: download every shelter, compute distance on the
phone. Moving that server-side is the natural next feature, and the reason to consider
Postgres + PostGIS over MySQL if the database is ever migrated off SQLite.

## Commands

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata seed            # categories, locations, donations, 13 shelters
python manage.py createsuperuser          # no users in the seed — make your own
python manage.py runserver 0.0.0.0:8000   # 0.0.0.0 so a phone on the LAN can reach it
```

`members/fixtures/seed.json` replaces the committed `db.sqlite3` as the way to get a working
database. It holds only reference data — **no users**, since password hashes don't belong in
a public repo, and no `DonationRecord`/`DonationHistory`, which are per-user activity.

`WaterLevel` is **not** in the seed: `WaterLevelAPI` reads `data/banjir_data.json` (committed)
and never queries that table, so its rows are dead cache.

`runserver` must bind `0.0.0.0`, not the default `127.0.0.1`, for a real device to connect.
`10.0.2.2` in `ALLOWED_HOSTS` is how the Android emulator reaches the host machine.

## Known issues

- `db.sqlite3` is no longer tracked — build a local one with `migrate` + `loaddata seed`. The
  **5 historical copies are still in git history** on a public repo, so purging them needs
  `git filter-repo` and a force-push.
- **No tests.** `members/tests.py` and `accounts/tests.py` are the empty Django stubs.
- `DATABASES` is still SQLite. Fine locally; it will not survive an ephemeral deploy host,
  and SQLite serialises writes.
- Comments throughout are a mix of Chinese and English.
- Scraped water-level data is not persisted, so there is no history and no trend — every
  request re-scrapes the current reading.
