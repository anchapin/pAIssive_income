# Changelog

Track all major changes, releases, and fixes here.

## [Unreleased] - 2025-06-17

### Dependencies
- Updated webpack from 5.99.8 to 5.99.9 with bug fixes for HMR, ES modules, and asset processing
- Updated @babel/core from 7.27.1 to 7.27.4
  - Improved parseExpression error messages
  - Reduced regenerator helper size optimizations
  - Split regeneratorRuntime into multiple helpers for better performance
  - Various bug fixes for async generator functions and TypeScript compatibility
- Updated cssnano from 6.1.2 to 7.0.7
  - Updated browserslist for better browser support
  - Fixed PostCSS peer dependency to version without vulnerabilities
  - Updated TypeScript declarations for better type safety
  - Performance improvements for default preset loading
  - Added support for selector order preservation in postcss-minify-selectors
  - Fixed percentage value preservation in at-rules with double quotes
## [Unreleased] - 2024-06-10

- Tool registry now supports rich metadata for each tool, including `keywords` for intent matching and `input_preprocessor` for input adaptation, enabling agentic reasoning and autonomous tool selection.
- CrewAIAgentTeam and compatible agent teams now select and invoke tools automatically using this metadata, supporting extensible keyword matching and robust input preparation.
- All agentic reasoning steps and tool invocations are now logged to the `agentic_reasoning` logger; logging configuration is left to the application.
- Documentation and usage examples updated in `docs/common-utils-tooling.md` and `docs/agent-team.md` to reflect these enhancements.