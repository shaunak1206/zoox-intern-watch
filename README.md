# zoox-intern-watch

A GitHub Actions job checks Zoox's Lever board (hourly on weekday Pacific working hours, every 6 hours otherwise). When a new software-oriented internship appears, it opens an issue in this repo that mentions @shaunak1206, so GitHub sends an email or push notification.

- `watch.py` fetches the board, keeps internships whose title or team looks software related (software, autonomy, AI/ML, data science, IT and applications, infrastructure and similar), and skips hardware, manufacturing, program management and similar roles.
- `seen.json` holds every internship id already seen. It was seeded on 2026-11-10 with the 12 internships that were already open, so only postings after that trigger a notification.
- Run it by hand from the Actions tab (Run workflow). Tick "test" to send a test notification.
- If the board stops returning postings, the job fails and GitHub emails the failure.
