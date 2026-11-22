# فاران | Faran University Agent Platform

Local, synthetic-data prototype for a multi-department digital university. Current version is mock-only; Paperclip, models, cloud services, and scheduled execution are disconnected/disabled. Marketing output is a draft.

## Run

Requires Python 3.10+; no third-party packages or paid API key.

```powershell
python faran.py seed
python faran.py run
python faran.py status
```

State is stored in `.faran/state.json`. The sample run is deterministic and idempotent by task ID. It represents a synthetic hardening course, synthetic enrollment, offline fixture exercise, zero mock cost, and independent deterministic evaluation. It does not perform a real scan or establish production recovery, scheduling, concurrency, or Paperclip integration.

See [docs/ROADMAP.md](docs/ROADMAP.md) for acceptance and next steps.

## PWA and Android

The Persian RTL dashboard is served from the repository root for Vercel. It includes an installable web manifest, an offline shell cache, and a mock workflow that saves demo state in browser local storage. Native Android wrapper is generated with Capacitor 8; run `npm ci`, copy root web files into `www`, then `npm run android:sync` and open `android/` in Android Studio. The Android wrapper requires Android SDK/Gradle tooling to produce an APK. UI workflow state is browser-local and does not sync across devices.
