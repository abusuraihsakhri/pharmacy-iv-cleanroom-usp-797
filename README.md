# Pharmacy IV Cleanroom USP 797

A Python threshold-evaluation prototype with a browser demonstration, CLI, and optional FastAPI API. It explores software workflows associated with sterile-compounding environmental monitoring. It **does not implement or validate USP <797> compliance**.

## Browser demonstrator

Open [web/index.html](web/index.html) in a modern browser for a local demonstration that runs without Python. It provides an optional same-origin server mode when FastAPI is running. A GitHub Pages deployment workflow is included; its live URL will be documented only after successful publication and verification.

**Safety boundary:** The built-in primary (25.0) and secondary (12.0) thresholds are illustrative values without assigned units, **not** USP <797> limits. This code does not classify cleanrooms, calculate beyond-use dates (BUDs), verify sterility or stability, or issue compliance certifications. Do not use its results to release sterile preparations, assign BUDs, or make patient-care decisions.

## Implemented functionality

- Generic numerical threshold and keyword alerts with urgency classification.
- Multi-worker coordinator in the agents directory and a separate USP-named demonstration subsystem.
- JSON dossiers, CLI checks, CSV batches, and a process-memory HMAC-SHA256 audit chain.
- Eight enrichment modules that apply similar generic threshold logic to different workflow labels (not instrument integrations).
- Mock-only chat; no real external model provider is connected.

## Run locally

Requires Python 3.9 or later.

~~~bash
git clone https://github.com/abusuraihsakhri/pharmacy-iv-cleanroom-usp-797.git
cd pharmacy-iv-cleanroom-usp-797
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api,test]"
python -m pytest -q
python cli.py audit --task-id DEMO-001 --target ZONE-A --primary 29.4 --secondary 14.8
python cli.py batch -i sample.csv -o results.csv
python cli.py serve --host 127.0.0.1 --port 8000
~~~

Visit http://127.0.0.1:8000/ for the browser UI; select server mode only while the backend runs. The API exposes GET /health, POST /api/audit, POST /api/chat, GET /metrics (JSON counters), and /docs.

The installed command pharmacy-iv-cleanroom-usp-797 uses the separate USP-named CLI, while python cli.py runs the main multi-worker prototype. They have distinct thresholds and output schemas.

## Security and privacy

- Enter only synthetic non-identifying data. Pattern-based checks are **not** comprehensive de-identification or HIPAA-compliant protection.
- Browser mode makes no background requests or persistent storage writes. Results remain in page memory unless explicitly exported as JSON.
- Server mode sends inputs to the selected same-origin API. Server dossiers and audit-chain entries live only in process memory and disappear on restart; integrity checks performed in a new process cannot validate old entries.
- Reading GET /api/audit/logs requires the X-Audit-Token header matching a configured AUDIT_READ_TOKEN; without that environment variable the route is unavailable.
- Use a network boundary or external authentication before exposing other API routes to untrusted clients.
- Configure a strong AUDIT_SECRET_KEY. Without one the process creates an ephemeral key and warns. A sample audit key existed in repository history: never reuse it; rotate it if ever deployed.
- Compose now binds its published port to 127.0.0.1 and requires AUDIT_SECRET_KEY from the environment. Never commit audit keys or real patient data.
- The HMAC chain is in-process tamper evidence, not a durable compliance record.

## Testing and deployment

~~~bash
python -m pytest -q
python -m compileall -q agents usp_797_cleanroom cli.py enrichment.py simulator.py
python simulator.py 100
~~~

GitHub Actions verifies Python 3.10–3.12 and checks browser JavaScript syntax. The browser demonstrator uses standard HTML, CSS and JavaScript, not Pyodide or backend Python in GitHub Pages. Modern Chromium, Firefox and Safari are expected to work; deployment-specific browser testing is still necessary.

Consult the [official USP <797> resource](https://www.usp.org/compounding/general-chapter-797) and local regulations for actual sterile-compounding requirements.

## License

[MIT](LICENSE).
