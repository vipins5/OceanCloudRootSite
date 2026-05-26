# OceanCloud Custom Agents

This folder contains repository-scoped custom agents for GitHub Copilot.

## Available Agents

1. Comment Moderator Agent
   - File: `.github/agents/comment-moderator.agent.md`
   - Purpose: check pending comments, draft moderation summaries, trigger moderation workflow checks.

2. Content QA Agent
   - File: `.github/agents/content-qa.agent.md`
   - Purpose: validate links, SEO metadata, and article script bundle consistency.

3. Release Agent
   - File: `.github/agents/release-agent.agent.md`
   - Purpose: run release validations, prepare deploy checklist, draft release notes.

## How to Use

In Copilot Chat:
1. Open agent picker.
2. Select one of the OceanCloud agents.
3. Provide a focused task prompt.

Example prompts:
- "Check pending comments and summarize moderation actions needed today."
- "Run content QA and list any SEO/canonical/script-bundle issues."
- "Prepare release readiness report and release notes for latest changes."

## Notes

- Agents are intentionally scoped and do not auto-deploy or auto-moderate without explicit instruction.
- For automation, these agents can still call existing scripts/workflows in this repository.
