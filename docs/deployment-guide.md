# Web Deployment Guide

## Supported product

The supported release is the Streamlit web application. Desktop windows and EXE bundles are intentionally not part of the architecture.

## Local or LAN run

```powershell
python -m pip install -r requirements.txt
streamlit run app.py --server.port 8510
```

Health endpoint: `http://127.0.0.1:8510/_stcore/health`.

For LAN classroom use, add `--server.address 0.0.0.0` and allow the selected port only on the trusted classroom network.

## Hosted Streamlit run

- Entrypoint: `app.py`
- Python: 3.12
- Install file: `requirements.txt`
- No secrets or database are required.
- Keep server-side node and timeout controls enabled; BFS can grow exponentially.

## Release verification

```powershell
python -m compileall -q app.py core algorithms ui
python -m pytest tests -q
```

CI additionally starts Streamlit and polls its health endpoint. A public deployment should use the same `master` revision that passed CI.
