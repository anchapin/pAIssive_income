# Python runtime security update (November 2026)

## Overview

The vulnerable pins in `requirements.txt` that Dependabot flagged have been raised to patched releases. They were resolved together for Python 3.10, the version CI uses.

- **PR:** [#424](https://github.com/anchapin/pAIssive_income/pull/424)
- **Files:** `requirements.txt`, `requirements_filtered.txt` (protobuf), `.github/workflows/consolidated-ci-cd.yml` (protobuf pin)

## Coupled stacks updated together

- fastapi 0.162 / starlette 1.7 / sse-starlette 3.5 / python-multipart 0.0.32
- mcp 1.30 / fastmcp 3.4 / pydantic 2.14 / anyio 4.16
- requests 2.34 / urllib3 2.8 / certifi 2026.10.23
- jupyter-server 2.21 / notebook 7.6 / jupyterlab 4.6 / tornado 6.5.10
- litellm 1.103.11 / openai 2.54 / boto3 1.44
- Authlib 1.9.5 / PyJWT 2.15.1 / cryptography 50.0.2

## Held back

Checked against the vulnerable ranges of the open Dependabot alerts, 42 of the 428 alert matches on `requirements.txt` remain.

These need Python 3.11 or newer:

- Pillow 13.0.0: 36 alerts. Pillow 12.3.0 is the newest release that supports Python 3.10, and the alerts' minimum.
- tornado 6.6: 3 alerts. 6.5.10 is used.
- filelock 4.2.1: 2 alerts. 3.32.7 is used. virtualenv 21.14.9+ requires filelock 3.24.2 or newer.

PyPDF2 3.0.1 has 1 alert with no fixed release. The package is deprecated in favour of pypdf.

Moving CI to Python 3.11+ would allow the first three.
