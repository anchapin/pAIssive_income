# Claude Agentic Coding Best Practices

This repository aims to follow Anthropic Claude's agentic coding best practices for safe,
reliable,
and auditable automation.

## Core Principles

1. **Explicit State and Input Handling**
   - All agent state and input/output should be explicit,
   never hidden in globals or side effects.

2. **Modular Decomposition**
   - Decompose logic into small, focused, testable modules and functions.

3. **Strong Input Validation**
   - Rigorously validate and sanitize all inputs at boundaries.

4. **Deterministic, Auditable Steps**
   - Ensure reproducibility; log every key operation and decision.

5. **Idempotency and Recovery**
   - Actions should be safe to repeat; design for recovery from failures.

6. **Human Oversight**
   - Allow for human review/override at key junctures (e.g.,
   dry run,
   confirmation prompts).

7. **Documentation**
   - Clearly document agent behaviors, expected inputs/outputs, and safety mechanisms.

8. **Testing and Simulation**
   - Comprehensive unit and integration tests, including edge/failure modes.

9. **Security and Permissions**
   - Use least privilege and audit all side effects.

## Checklist for Contributors

- [ ] Does this code have explicit, documented inputs and outputs?
- [ ] Are all external inputs validated and sanitized?
- [ ] Is the logic broken into small, testable functions or modules?
- [ ] Are all key actions logged for traceability?
- [ ] Is the code idempotent and resilient to partial failures?
- [ ] Is there a clear path for human override or review?
- [ ] Are security, permissions, and side effects explicitly handled?
- [ ] Are new behaviors covered by unit/integration tests?
- [ ] Is this file/module/class documented per these guidelines?

## How to Apply

- Reference this document in PRs and code reviews.
- Use the checklist as part of your development workflow.
- Raise issues or PRs for areas where the repo does not yet meet these standards.

For more detail,
see: https://www.anthropic.com/engineering/claude-code-best-practices?s=03
