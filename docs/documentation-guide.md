# Documentation Guide

This guide describes the structure, standards, and update process for the documentation in the pAIssive Income Framework.

## Documentation Structure

- **Root README.md**: Project summary, high-level info, and links to main documentation.
- **docs/**: Main documentation directory.
  - **README.md**: Table of contents and navigation for all docs.
  - **getting-started.md**: Onboarding, setup, and usage guide.
  - **overview.md**: Project architecture and module descriptions.
  - **api-reference.md**: Detailed API documentation.
  - **contributing.md**: Contributor guidelines and code standards.
  - **Other topical docs**: e.g., devops, CI, marketing, monetization, troubleshooting, etc.

## Documentation Standards

- Use clear, concise language and proper Markdown formatting.
- Start each file with a short description of its audience and scope.
- Cross-reference related docs using relative links.
- Keep onboarding/setup instructions in one authoritative place (`getting-started.md`).
- When updating documentation, ensure all references/links are current.
- Add a "Feedback & Updates" section to major docs for user suggestions.

## Update/Contribution Process

1. **Identify the doc to update** or the new doc to add.
2. **Check for overlap/duplication** with existing docs.
3. **Edit or create the doc** following the standards above.
4. **Update the table of contents** in `docs/README.md` if needed.
5. **Open a pull request** with the proposed changes, clearly describing the update.
6. **Tag reviewers or stakeholders** as appropriate.
7. **Merge after review** and ensure the doc is accessible and cross-linked.

## Stakeholder Feedback

- Users and contributors can suggest changes by:
  - Opening an issue with the label `documentation`
  - Commenting directly on docs in pull requests
  - Emailing the maintainer: a.n.chapin@gmail.com

## Keeping Documentation Up To Date

- Documentation should be updated with each major code or feature change.
- Assign a reviewer for docs in large PRs.
- Archive outdated docs in `docs/archive/` (create if needed).