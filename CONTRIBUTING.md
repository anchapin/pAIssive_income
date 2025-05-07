# Contributing Guidelines

Thank you for considering a contribution to this project!

We follow [Claude Agentic Coding Best Practices](claude_coding_best_practices.md) to ensure safe, reliable, and auditable automation. **All contributors must review and follow these guidelines before submitting pull requests.**

## Checklist for Contributors

Before submitting your PR, please ensure:

- [ ] This code has explicit, documented inputs and outputs.
- [ ] All external inputs are validated and sanitized.
- [ ] Logic is broken into small, testable functions or modules.
- [ ] All key actions are logged for traceability.
- [ ] Code is idempotent and resilient to partial failures.
- [ ] There is a clear path for human override or review.
- [ ] Security, permissions, and side effects are explicitly handled.
- [ ] New behaviors are covered by unit/integration tests.
- [ ] This file/module/class is documented per the best practices guidelines.

See the full checklist and principles in [claude_coding_best_practices.md](claude_coding_best_practices.md).

## Pull Requests

- Reference the checklist above in your PR description.
- Use the checklist as part of your development and review workflow.
- If you see areas where the repo does not yet meet these standards, please raise an issue or PR.

Thank you for helping us maintain high standards!