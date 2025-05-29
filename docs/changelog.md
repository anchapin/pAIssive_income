# Changelog

Track all major changes, releases, and fixes here.

## [Unreleased] - 2024-06-10

- Tool registry now supports rich metadata for each tool, including `keywords` for intent matching and `input_preprocessor` for input adaptation, enabling agentic reasoning and autonomous tool selection.
- CrewAIAgentTeam and compatible agent teams now select and invoke tools automatically using this metadata, supporting extensible keyword matching and robust input preparation.
- All agentic reasoning steps and tool invocations are now logged to the `agentic_reasoning` logger; logging configuration is left to the application.
- Documentation and usage examples updated in `docs/common-utils-tooling.md` and `docs/agent-team.md` to reflect these enhancements.