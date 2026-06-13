# Contributing to claude-agent-team

Thanks for your interest in improving **claude-agent-team** — a Claude Code skill that scaffolds a multi-agent development team. Contributions of all sizes are welcome, and we're glad to have you here.

## Ways to Contribute

There are lots of ways to help:

- **Report issues** — found a bug, a confusing message, or something that doesn't scaffold correctly? Open an issue.
- **Submit pull requests** — fixes, new features, and improvements are all appreciated.
- **Improve the agent prompts** — clearer, sharper agent instructions make the whole team work better.
- **Refine templates** — the scaffolded files are only as good as their templates.
- **Polish the docs** — typos, clarifications, and better examples are genuinely valuable.

If you're not sure where to start, browse the open issues or just ask in a new one.

## Before You Open a PR

Please run these local checks so CI stays green:

```bash
# 1. Compile all Python scripts
python -m py_compile assets/scripts/*.py

# 2. Validate the settings JSON
python -m json.tool assets/.claude/settings.json > /dev/null

# 3. Make sure doc frontmatter parses
#    (confirm the YAML frontmatter in your changed docs is well-formed)
```

If any of these fail, fix them before pushing — they're the same checks CI runs.

## Commit Messages

We use a simple convention:

```
<type>(<scope>): <description>
```

For example:

```
fix(scripts): handle missing settings file gracefully
docs(readme): clarify install steps
feat(agents): add reviewer agent prompt
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

## Pull Request Checks

Every PR runs the **validate** GitHub Action, which re-runs the checks above. Make sure your branch passes locally first so the Action does too.

## Large Changes

Planning something big — a new agent role, a structural refactor, or a breaking change? **Please open an issue first** so we can talk it through before you invest a lot of time. It helps us align early and saves everyone effort.

Happy contributing!
