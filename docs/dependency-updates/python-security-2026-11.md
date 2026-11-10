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

These fixes require Python 3.11 or newer:

- Pillow 13.0.0
- tornado 6.6
- filelock 4.2.1

Moving CI to Python 3.11+ would allow them.

These packages have no fixed release yet:

- mistune
- nbconvert (one advisory)
- PyPDF2
