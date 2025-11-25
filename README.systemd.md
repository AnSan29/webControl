# systemd service & timer for webControl

This repository includes example systemd unit and timer files to run webControl on system boot and restart it daily at 03:00.

Important: these are *examples* which require manual installation and tuning for your environment. Follow the instructions below on a Linux server (systemd).

## Files included
- `systemd/webcontrol.service.example` — template service to start the server using `scripts/run_server.sh`.
- `systemd/webcontrol-restart.service.example` — one-shot service to restart the main unit (used by the timer).
- `systemd/webcontrol-restart.timer.example` — timer that triggers the restart at 03:00 every day.

## Install and enable
1. Copy example files to `/etc/systemd/system/` (requires root):

```bash
sudo cp systemd/webcontrol.service.example /etc/systemd/system/webcontrol.service
sudo cp systemd/webcontrol-restart.service.example /etc/systemd/system/webcontrol-restart.service
sudo cp systemd/webcontrol-restart.timer.example /etc/systemd/system/webcontrol-restart.timer
```

2. Edit `/etc/systemd/system/webcontrol.service`:
- Set `User=` to the user running the service (e.g., `ubuntu` or `www-data`).
- Make sure `WorkingDirectory=` points to the repository root where `.env`, `scripts/run_server.sh` and `.venv` live.
- Optionally adjust security options and resource limits.

3. Reload `systemd` and enable/start the unit and timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now webcontrol.service
sudo systemctl enable --now webcontrol-restart.timer
```

4. Check status:

```bash
sudo systemctl status webcontrol.service
sudo journalctl -u webcontrol.service -f
sudo systemctl status webcontrol-restart.timer
``` 

## Notes and suggestions
- For production use, place the project into a stable path (e.g., `/srv/webcontrol`).
- Use a dedicated OS user (e.g., `webcontrol`) with restricted permissions.
- If you serve behind a reverse proxy (nginx), ensure the proxy is up before this service by adding `After=nginx.service`.
- Consider using process managers like `gunicorn` with uvicorn workers for advanced setups.
- I intentionally left `.env` aside — keep secrets out of version control and prefer `EnvironmentFile=` in systemd or `systemctl set-environment`.

## Troubleshooting
- If the service fails on start, inspect logs and `systemctl status` and fix path/permissions.
- If your service should be restarted more gracefully, add `ExecStop` to perform sanity checks before shutdown.

