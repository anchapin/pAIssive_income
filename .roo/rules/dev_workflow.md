---
description: Guide for managing task-driven development workflows
globs: **/*
alwaysApply: true
---
# Development Workflow

This guide outlines the typical process for managing software development projects.

## Primary Interaction: MCP Server vs. CLI

The project offers two primary ways to interact:

1.  **MCP Server (Recommended for Integrated Tools)**:
    - For AI agents and integrated development environments (like Roo Code), interacting via the **MCP server is the preferred method**.
    - The MCP server exposes development functionality through a set of tools.
    - This method offers better performance, structured data exchange, and richer error handling compared to CLI parsing.
    - Refer to [`mcp.md`](mdc:.roo/rules/mcp.md) for details on the MCP architecture and available tools.
    - **Restart the MCP server** if core logic in `scripts/modules` or MCP tool/direct function definitions change.

2.  **Development Tools and Scripts**:
    - Use project-specific scripts and tools for development workflow management.
    - Scripts should provide a user-friendly interface for direct terminal interaction.
    - Tools can serve as a fallback if the MCP server is inaccessible or a specific function isn't exposed via MCP.
    - Refer to project documentation for detailed command reference.

## Standard Development Workflow Process

-   Start new projects by setting up initial project structure and requirements documentation
-   Begin coding sessions by reviewing current tasks, status, and priorities
-   Determine the next task to work on based on dependencies and project priorities
-   Analyze task complexity before breaking down large tasks into smaller components
-   Review project requirements and implementation plans regularly
-   Select tasks based on dependencies (all prerequisites completed), priority level, and logical order
-   Clarify tasks by checking documentation or asking for user input
-   View specific task details to understand implementation requirements
-   Break down complex tasks into manageable subtasks with clear requirements
-   Clear existing plans if needed before regenerating task breakdown
-   Implement code following task details, dependencies, and project standards
-   Verify tasks according to test strategies before marking as complete (See [`tests.md`](mdc:.roo/rules/tests.md))
-   Mark completed tasks as done when all requirements are satisfied
-   Update dependent tasks when implementation differs from original plan
-   Add new tasks discovered during implementation as needed
-   Add new subtasks as needed for complex features
-   Append notes or details to task documentation as implementation progresses
-   Generate updated documentation after making changes to requirements
-   Maintain valid dependency structure and update when requirements change
-   Respect dependency chains and task priorities when selecting work
-   Report progress regularly and update project status

## Task Complexity Analysis

-   Analyze project complexity for comprehensive understanding of requirements
-   Review complexity analysis for a formatted, readable assessment
-   Focus on tasks with highest complexity for detailed breakdown
-   Use analysis results to determine appropriate subtask allocation
-   Note that complexity analysis should inform task breakdown decisions

## Task Breakdown Process

-   Break down complex tasks into manageable subtasks based on complexity analysis
-   Specify appropriate number of subtasks based on complexity and scope
-   Leverage research and domain knowledge for informed task breakdown
-   Clear existing plans before generating new ones when needed
-   Provide additional context when breaking down tasks
-   Review and adjust generated subtasks as necessary
-   Expand multiple pending tasks at once when appropriate
-   Replace existing subtask breakdown when requirements change significantly

## Implementation Drift Handling

-   When implementation differs significantly from planned approach
-   When future tasks need modification due to current implementation choices
-   When new dependencies or requirements emerge
-   Update multiple future tasks when implementation context changes
-   Update specific tasks when requirements or approach changes

## Task Status Management

-   Use 'pending' for tasks ready to be worked on
-   Use 'done' for completed and verified tasks
-   Use 'deferred' for postponed tasks
-   Add custom status values as needed for project-specific workflows

## Task Structure Fields

- **id**: Unique identifier for the task (Example: `1`, `1.1`)
- **title**: Brief, descriptive title (Example: `"Initialize Repo"`)
- **description**: Concise summary of what the task involves (Example: `"Create a new repository, set up initial structure."`)
- **status**: Current state of the task (Example: `"pending"`, `"done"`, `"deferred"`)
- **dependencies**: IDs of prerequisite tasks (Example: `[1, 2.1]`)
    - Dependencies are displayed with status indicators (✅ for completed, ⏱️ for pending)
    - This helps quickly identify which prerequisite tasks are blocking work
- **priority**: Importance level (Example: `"high"`, `"medium"`, `"low"`)
- **details**: In-depth implementation instructions (Example: `"Use GitHub client ID/secret, handle callback, set session token."`) 
- **testStrategy**: Verification approach (Example: `"Deploy and call endpoint to confirm 'Hello World' response."`) 
- **subtasks**: List of smaller, more specific tasks (Example: `[{"id": 1, "title": "Configure OAuth", ...}]`) 
- Refer to task structure details (previously linked to `tasks.md`).

## Configuration Management

Project configuration is managed through standard configuration files:

1.  **Project Configuration Files:**
    *   Located in the project root directory.
    *   Store project settings: build configurations, environment settings, logging level, project metadata, etc.
    *   **Managed via project-specific configuration tools and scripts.**
    *   **View/Set configurations via project management tools.**
    *   Created and maintained as part of project setup.

2.  **Environment Variables (`.env` / `mcp.json`):**
    *   Used **only** for sensitive API keys and specific endpoint URLs.
    *   Place API keys (one per provider) in a `.env` file in the project root for local usage.
    *   For MCP/Roo Code integration, configure these keys in the `env` section of `.roo/mcp.json`.
    *   Available keys/variables: See `assets/env.example` or project documentation.

**Important:** Configuration settings should be managed through appropriate project tools and configuration files.
**If AI commands FAIL in MCP** verify that the API key for the selected provider is present in the `env` section of `.roo/mcp.json`.
**If AI commands FAIL in CLI** verify that the API key for the selected provider is present in the `.env` file in the root of the project.

## Determining the Next Task

- Identify the next task to work on based on project priorities and dependencies.
- Identify tasks with all dependencies satisfied
- Tasks are prioritized by priority level, dependency count, and logical order
- Consider comprehensive task information including:
    - Basic task details and description
    - Implementation details
    - Subtasks (if they exist)
    - Contextual requirements
- Recommended before starting any new development work
- Respect project's dependency structure
- Ensure tasks are completed in the appropriate sequence
- Plan ready-to-use approaches for common development actions

## Viewing Specific Task Details

- Review specific tasks and their detailed requirements.
- Use clear identification for subtasks and their relationships
- Display comprehensive information for each task
- For parent tasks, show all subtasks and their current status
- For subtasks, show parent task information and relationship
- Provide contextual requirements appropriate for the specific task
- Useful for examining task details before implementation or checking status

## Managing Task Dependencies

- Add dependencies between tasks as needed.
- Remove dependencies when requirements change.
- Prevent circular dependencies and duplicate dependency entries
- Check dependencies for existence before adding or removing
- Update documentation after dependency changes
- Visualize dependencies with status indicators in documentation

## Iterative Subtask Implementation

Once a task has been broken down into subtasks using `expand_task` or similar methods, follow this iterative process for implementation:

1.  **Understand the Goal (Preparation):**
    *   Review the subtask documentation to thoroughly understand the specific goals and requirements of the subtask.

2.  **Initial Exploration & Planning (Iteration 1):**
    *   This is the first attempt at creating a concrete implementation plan.
    *   Explore the codebase to identify the precise files, functions, and even specific lines of code that will need modification.
    *   Determine the intended code changes (diffs) and their locations.
    *   Gather *all* relevant details from this exploration phase.

3.  **Log the Plan:**
    *   Document the detailed implementation plan in project documentation.
    *   Provide the *complete and detailed* findings from the exploration phase. Include file paths, line numbers, proposed diffs, reasoning, and any potential challenges identified. Do not omit details. The goal is to create a rich, timestamped log within the subtask's documentation.

4.  **Verify the Plan:**
    *   Review the documentation again to confirm that the detailed implementation plan has been successfully recorded.

5.  **Begin Implementation:**
    *   Update the subtask status to in-progress in project documentation.
    *   Start coding based on the logged plan.

6.  **Refine and Log Progress (Iteration 2+):**
    *   As implementation progresses, you will encounter challenges, discover nuances, or confirm successful approaches.
    *   **Before appending new information**: Briefly review the *existing* details logged in the subtask documentation to ensure the update adds fresh insights and avoids redundancy.
    *   **Regularly** update the subtask documentation with new findings.
    *   **Crucially, log:**
        *   What worked ("fundamental truths" discovered).
        *   What didn't work and why (to avoid repeating mistakes).
        *   Specific code snippets or configurations that were successful.
        *   Decisions made, especially if confirmed with user input.
        *   Any deviations from the initial plan and the reasoning.
    *   The objective is to continuously enrich the subtask's documentation, creating a log of the implementation journey that helps developers learn, adapt, and avoid repeating errors.

7.  **Review & Update Rules (Post-Implementation):**
    *   Once the implementation for the subtask is functionally complete, review all code changes and the relevant chat history.
    *   Identify any new or modified code patterns, conventions, or best practices established during the implementation.
    *   Create new or update existing rules following internal guidelines (previously linked to `cursor_rules.md` and `self_improve.md`).

8.  **Mark Task Complete:**
    *   After verifying the implementation and updating any necessary rules, mark the subtask as completed in project documentation.

9.  **Commit Changes (If using Git):**
    *   Stage the relevant code changes and any updated/new rule files (`git add .`).
    *   Craft a comprehensive Git commit message summarizing the work done for the subtask, including both code implementation and any rule adjustments.
    *   Execute the commit command directly in the terminal (e.g., `git commit -m 'feat(module): Implement feature X for subtask <subtaskId>\n\n- Details about changes...\n- Updated rule Y for pattern Z'`).
    *   Consider if a Changeset is needed according to internal versioning guidelines (previously linked to `changeset.md`). If so, run `npm run changeset`, stage the generated file, and amend the commit or create a new one.

10. **Proceed to Next Subtask:**
    *   Identify the next subtask based on project priorities and dependencies.

## Code Analysis & Refactoring Techniques

- **Top-Level Function Search**:
    - Useful for understanding module structure or planning refactors.
    - Use grep/ripgrep to find exported functions/constants:
      `rg "export (async function|function|const) \w+"` or similar patterns.
    - Can help compare functions between files during migrations or identify potential naming conflicts.

---
*This workflow provides a general guideline. Adapt it based on your specific project needs and team practices.*