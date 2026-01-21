# Pause-Point-Mapper
Visualize and analyze cycling activity tracks to detect stops and pauses, cluster them, and display interactive maps with reverse-geocoded locations.

Pause Point Mapper is a Django-based tool that accepts GPX/TCX/FIT files or Strava activity links, analyzes trackpoint time gaps and distances, detects pause/stop points using DBSCAN clustering, reverse-geocodes stop locations using Nominatim, and renders an interactive Folium map with start/finish/highest/longest/stop markers. It is intended for local use and does not persist user uploads.
Key features:
Parse GPX, TCX, and FIT files; fetch Strava activity and streams.
Detect stops by time-gap threshold and cluster nearby stops.
Reverse-geocode stops to human-readable addresses.
Render interactive maps with route and popup details.
Quick start (dev):
Create and activate venv, install dependencies, run python [manage.py](http://_vscodecontentref_/0) migrate, then python [manage.py](http://_vscodecontentref_/1) runserver.
Security note: Do not commit secrets (e.g., STRAVA_CLIENT_SECRET) to the repo; use environment variables.
