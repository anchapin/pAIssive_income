# Architecture Overview

This section provides a high-level view of the system and summarizes architecture lessons from past fixes and improvement plans.

---

## System Components

- **API Gateway:** RESTful API for all modules (see [api_gateway.md](../06_module_deep_dives/api_gateway.md))
- **AI Models Module:** Model management, serving, caching
- **Agent Team:** Multi-agent and CrewAI orchestration
- **Domain Modules:** Niche analysis, monetization, marketing, user, dashboard
- **Common Utilities:** Logging, security, config, secrets
- **DevOps:** Docker, GitHub Actions, Kubernetes, CI/CD

---

## Key Architecture Lessons

- **Service initialization order matters:** Initialize databases and core services before launching API or agent orchestrators ([see MCP_ADAPTER_FIX.md](../../../MCP_ADAPTER_FIX.md)).
- **Microservices communication:** Use explicit service discovery and avoid hardcoding hostnames—see [03_service_discovery.md](03_service_discovery.md).
- **Configuration best practices:** Always load sensitive config from env vars/secrets, never hardcode in code or compose files ([docker-compose-fix-README.md](../../../docker-compose-fix-README.md)).
- **Security:** Secure all network interfaces by default; never expose internal-only services to the public network.
- **CI/CD and DevOps:** Use Docker Buildx and multi-stage builds for reproducibility (see [docs/03_devops_and_cicd/](../../03_devops_and_cicd/)).

---

## Diagrams

(Add or generate diagrams as needed.)

---

For historical context and detailed architecture evolution, see [docs/09_archive_and_notes/amazon_q_notes.md](../../09_archive_and_notes/amazon_q_notes.md) and [improvement_plan.md](../../../improvement_plan.md).