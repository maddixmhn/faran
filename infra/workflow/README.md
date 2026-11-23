# Workflow services

Pinned stack: Paperclip source release `v2026.1117.0` (official container tag `2026.1117.0`), n8n production image `2.48.7`, PostgreSQL `18-alpine`, and optional Cloudflare Tunnel `2026.11.1`. The local override uses PostgreSQL `16-alpine` and the official cached n8n `2.46.4` image by immutable digest because this host cannot currently pull the production images; refresh pins only after checking upstream sources. Do not deploy the local override to production. Paperclip uses its image's persistent `/paperclip` volume; n8n stores workflows/credentials in PostgreSQL and its encryption material in the persistent n8n volume. Do not delete or replace these volumes during ordinary upgrades.

## Local operator sandbox

### Local dashboards

The Faran admin dashboard and Dr. Soleimani evaluator can also be served by the optional, loopback-only `dashboards` profile. From the Faran repository root, run:

```powershell
docker compose --env-file infra/workflow/.env -f infra/workflow/compose.yaml -f infra/workflow/compose.local.yaml --profile dashboards up -d --build faran-web evaluator-web
```

Open `http://localhost:8000` for the university admin panel and `http://localhost:8001` for the evaluator. Both are static frontends; Paperclip/n8n/PostgreSQL remain separate local services. Dashboard containers run read-only with a temporary cache and only loopback ports. The Nginx base is pinned to the official image digest already cached on this host because Docker Hub returned 403 for tag metadata; refresh the digest only after verifying its upstream tag, licence, security updates, and compatibility. To stop only the two frontends, run `docker compose --env-file infra/workflow/.env -f infra/workflow/compose.yaml -f infra/workflow/compose.local.yaml --profile dashboards stop faran-web evaluator-web`.

1. Install/start Docker Desktop's Linux engine.
2. Copy `.env.example` to `.env`. Replace all required secrets with independent random values. Do not put model API keys in public files or browser JavaScript.
3. Start the services:

   ```powershell
   docker compose --env-file .env -f compose.yaml -f compose.local.yaml up -d
   ```

4. In a second terminal, start the official Paperclip CLI locally. It stores its own database, configuration and keys in `infra/workflow/data/paperclip-local`:

   ```powershell
   npx --yes paperclipai@2026.1117.0 run --data-dir .\data\paperclip-local --bind loopback
   ```

   Complete its local setup. Add `host.docker.internal` to `server.allowedHostnames` in `data/paperclip-local/instances/default/config.json` so the n8n container can call the health endpoint; keep the instance loopback-only and restart Paperclip after the edit. The CLI allow-hostname helper currently returns `EPERM: fsync` on this Windows setup. The optional Paperclip Compose service is profile-gated because Windows loopback service and Docker service cannot both own port 3100.
5. Open Paperclip at `http://localhost:3100` and n8n at `http://localhost:5678`; complete their initial admin setup where prompted. On this host, the n8n owner is claimed and the saved execution has been viewed in the browser. On a new workstation, finish first-owner setup before opening saved runs. Schedules and provider-driven agent runs remain disabled.
6. Import the local-only read-only health diagram (inactive, manual trigger):

   ```powershell
   docker compose --env-file .env -f compose.yaml -f compose.local.yaml exec n8n n8n import:workflow --input=/workflows/faran-paperclip-health.local.json
   ```

7. Import the local-only role-status diagram (also inactive, manual trigger):

   ```powershell
   docker compose --env-file .env -f compose.yaml -f compose.local.yaml exec n8n n8n import:workflow --input=/workflows/faran-agent-status.local.json
   ```

   The status flow reads only the synthetic Faran agent roster and outputs role name, role key, lifecycle status, heartbeat flag, monthly budget and last heartbeat. It filters runtime configuration and other Paperclip fields before its final node. Its local Paperclip endpoint relies on the private trusted sandbox; do not reuse this URL or auth model on an internet-facing deployment. Set up the n8n owner in the browser before reviewing saved runs. Production must use authenticated Paperclip API access and be separately reviewed.

8. Import the combined local snapshot diagram (manual and inactive):

   ```powershell
   docker compose --env-file .env -f compose.yaml -f compose.local.yaml exec n8n n8n import:workflow --input=/workflows/faran-system-snapshot.local.json
   ```

   It reads Paperclip health, then the same synthetic role roster, and emits one sanitized status snapshot. The health, role and snapshot workflows remain manual and inactive.

9. Import and manually run the read-only task monitor when you need the latest synthetic company task statuses:

   ```powershell
   docker compose --env-file .env -f compose.yaml -f compose.local.yaml exec n8n n8n import:workflow --input=/workflows/faran-task-monitor.local.json
   ```

   The monitor reads at most 25 recently updated issues from the installed Paperclip company API, then emits only IDs, identifier, title, status, priority, assignee/project IDs and timestamps. It excludes descriptions, comments and runtime settings. Its manual trigger is inactive; it creates no issue and wakes no agent.

10. Check health with `docker compose ps` and `docker compose logs --tail 100 n8n n8n-db`. In n8n, run a manual workflow to inspect its saved execution and individual node status.

The manual evaluation feed reads only Paperclip heartbeat-run summary metadata (maximum 1,000 runs) and emits `faran-event-schema/1.0`. It excludes prompts, task descriptions/comments, provider traces, credentials and learner data. It is read-only, inactive, and does not start agents. Current sandbox history is empty, so its honest result is `connected-no-runs`; do not use mock data as evidence. When runs exist, the output is marked `synthetic: false` but still `real-run-metadata-unverified`: it is not signed or independently authenticated evidence. Copy the final node's JSON output to a local `.json` file and upload it to the evaluator. Unsupported statuses remain visible as unknown; missing policy versions are flagged by the evaluator.

To import or update all five tracked workflow definitions in one step, run from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\infra\workflow\scripts\import-local-workflows.ps1
```

Each definition carries its persistent n8n workflow ID, so re-import updates the existing workflow instead of creating a duplicate. All definitions set `active: false`; this command does not enable schedules or start agent routines.

## Start the local runtime at sign-in

The current Windows workstation has a user-level Task Scheduler entry, `Faran Local Workflow Runtime`. It starts Docker Desktop, ensures n8n/PostgreSQL are up, and starts the Paperclip CLI on loopback if its health endpoint is unavailable. It runs only after this Windows account signs in; the task stores no password and does not enable n8n schedules or Paperclip agent routines. Its logs are under ignored `infra/workflow/data/launcher-logs/`.

To install it on another development workstation:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\infra\workflow\scripts\install-startup-task.ps1
```

To remove the logon task:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\infra\workflow\scripts\remove-startup-task.ps1
```

This helps restore the local sandbox after interactive sign-in. It is not unattended 24/7 hosting: Windows must be on, the owner must sign in, and the machine must stay awake. Use an always-on server for the production availability target.

The local overlay publishes both admin ports only on loopback. Do not remove the `127.0.0.1` binding to make setup easier.

## Authenticated local Paperclip role reads

The two local role-reading workflows reference the n8n credential `Faran Paperclip Local Observer`; their workflow JSON contains only its credential ID/name, never the token. The credential holds a Paperclip board API key encrypted by n8n. Paperclip currently issues board keys with broad board permissions, so this 30-day key is for the loopback-only synthetic sandbox and manual GET workflows only; it is not a read-only key and must not be used on a public deployment. The key was created using Paperclip's local implicit-admin CLI identity. The current host's n8n owner is claimed and can access the active credential in the Personal project; the obsolete credential for the revoked key has been deleted. Rotate the key before its expiry through the Paperclip token commands and update the n8n credential; do not add the key to workflow JSON, `.env`, or Git.

The temporary import staging folder `infra/workflow/data/credential-staging/` is Git-ignored and restricted to the current Windows account. The original key in its JSON files has been revoked (the API returns HTTP 401 for it); the active replacement key was imported directly from stdin into n8n and is not saved in those host files. The obsolete encrypted credential has been removed from n8n. Remove the remaining old staging files locally:

```powershell
Remove-Item -LiteralPath .\infra\workflow\data\credential-staging\paperclip-token.json, .\infra\workflow\data\credential-staging\paperclip-header-auth.json, .\infra\workflow\data\credential-staging\last-run.json -Force
```

## Manual local backup and recovery evidence

Backups are manual; this repository does not enable a backup schedule. From the repository root, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\infra\workflow\scripts\backup-local-runtime.ps1
```

The script uses Paperclip's supported `db:backup` command and captures the Paperclip instance config, local encryption/signing keys and storage files; it also saves an n8n PostgreSQL custom-format dump, the n8n `/home/node/.n8n` volume (including its credential encryption key), and the workflow `.env`. It writes a manifest and SHA-256 checksums under the ignored `infra/workflow/data/backups/<timestamp>` directory and restricts the backup folder to the current Windows account. These files contain secrets and workflow/account data: keep the complete folder private and never commit or upload it. Keep the backup on the same machine only as a temporary recovery copy; it is not off-site disaster protection. Remove old copies manually after verifying a newer one.

Recovery requires restoring each database, the matching encryption keys, configs and Paperclip storage as one set. Do not replace live databases while services are running. The 2026-11-22 recovery drill restored the n8n dump into an isolated PostgreSQL 16 database (173 public tables) and Paperclip's compressed SQL dump into a separate isolated PostgreSQL 16 database (320 public tables); both temporary databases were removed afterward. The n8n volume archive was listed successfully. This verifies database dump readability and SQL restore, but not a full application cold-start, credential decryption, Paperclip file recovery, or a production disaster-recovery procedure. Those remain acceptance work before relying on this bundle for a full restore.

The production health workflow only calls Paperclip's read-only `/api/health` endpoint at `paperclip:3100`. For this Windows host, import `faran-paperclip-health.local.json`; it calls the host-run CLI at `host.docker.internal:3100`. The local-only roster workflow calls the trusted local Paperclip agents endpoint for the synthetic company. Both definitions remain inactive with manual triggers. Saved local executions show each node's actual status; the flows start no agent run and change no Paperclip data.

## Cloudflare host overlay

The Cloudflare overlay is a configuration artifact, not an active deployment. It requires an always-on Linux Docker host, a Cloudflare Tunnel token stored in `.env`, hostnames routed to `paperclip:3100` and `n8n:5678`, and authentication policies created before starting it. For production, set `PAPERCLIP_PUBLIC_URL`, `N8N_HOST`, `N8N_PROTOCOL=https`, `N8N_EDITOR_BASE_URL`, `N8N_WEBHOOK_URL`, `N8N_PROXY_HOPS=1`, and `N8N_SECURE_COOKIE=true` to the confirmed hostnames. Do not add the local override in production. Keep the service ports unpublished; only the tunnel container reaches them on the Docker network.

After creating hostname routes and Access rules, start:

```powershell
docker compose --env-file .env -f compose.yaml -f compose.cloudflare.yaml up -d
```

The Cloudflare account, zone, hostnames and origin have not been configured. Never publish these endpoints without an Access/login policy. Cloudflare Tunnel does not provide a server or persistent compute.

## Trigger policy

Services use `restart: unless-stopped` so the host can keep them available and recover after reboot. This does **not** activate Paperclip routines or n8n schedules. Schedules stay disabled until the owner selects cadence, timezone, model/provider, monthly budget, concurrency and pause/recovery policy. The initial n8n workflow should use a manual trigger and synthetic-only data until a live integration is approved and configured.

## Update policy

Do not use floating `latest` tags. Check upstream release/security notes and backups before changing pins. Back up Paperclip data, `n8n_db`, `n8n_data`, encryption keys and workflow definitions together; restoring n8n without its original encryption key can make saved credentials unusable.

Configuration references: [n8n isolation settings](https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/isolate-n8n.md), [disable the MCP module](https://github.com/n8n-io/n8n-docs/blob/main/docs/connect/connect-to-n8n-mcp-server.md), [webhook URLs behind a reverse proxy](https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-webhook-urls-with-reverse-proxy.md), and [n8n endpoint environment variables](https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/endpoints.md).

