# ArtistAgent vs DataGathererAgent Benchmark Results

| Prompt | Case | ArtistAgent Output | Correct | Time (ms) | DataGathererAgent Output | Correct | Time (ms) |
|--------|------|-------------------|---------|-----------|-------------------------|---------|-----------|
| `2 + 3 * 4` | Simple arithmetic (calculator) | `14` | ✅ | 3.3 | `Data found for '2 + 3 * 4': [Mock data about '2 + 3 * 4']` | ❌ | 0.0 |
| `What is 10 divided by 2?` | Division (calculator) | `Error: Invalid characters in expression` | ❌ | 0.0 | `Data found for 'What is 10 divided by 2?': [Mock data about 'What is 10 divided by 2?']` | ❌ | 0.0 |
| `gather: artificial intelligence` | Data gathering (info) | `No suitable tool found for this prompt.` | ❌ | 0.0 | `Data found for 'artificial intelligence': [Mock data about 'artificial intelligence']` | ✅ | 0.0 |
| `Draw a picture of a cat.` | No matching tool | `No suitable tool found for this prompt.` | ✅ | 0.0 | `Data found for 'Draw a picture of a cat.': [Mock data about 'Draw a picture of a cat.']` | ❌ | 0.0 |

> **Extending this benchmark:**
> - Add new prompts to the `PROMPTS` list as new tools/skills are added.
> - Add more agents (columns) as you implement new agent types.
> - Consider evaluating multi-step reasoning/tool chaining in future versions.
