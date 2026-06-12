# Claude Skills

Project-level Claude Code skills, installed from the collections in Snyk's
"Top 8 Claude Skills for Entrepreneurs, Startup Founders, and Solopreneurs"
article. Skills activate contextually when a task matches their description;
list them with `/skills` in Claude Code.

## Sources

| # | Collection | Source | License | What was installed |
|---|---|---|---|---|
| 1 | Marketing Skills (Corey Haines) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | MIT | All skills (copywriting, CRO, SEO, launch, pricing, emails, ads, analytics, …) |
| 2 | Wondelai Product & Strategy | [wondelai/skills](https://github.com/wondelai/skills) | MIT | jobs-to-be-done, storybrand-messaging, scorecard-marketing, hooked-ux, cro-methodology, negotiation, refactoring-ui, ios-hig-design, ux-heuristics, web-typography, top-design |
| 3 | Anthropic PPTX | [anthropics/skills](https://github.com/anthropics/skills) | See `pptx/LICENSE` | `pptx` (pitch decks / presentations) |
| 4 | SaaS Financial Projections | originally `founderjourney/claude-skills` — **repo no longer exists on GitHub**; recreated locally from the article's spec | MIT | `saas-financial-projections` |
| 5 | Claude Skills Library (nginity) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | MIT | marketing, product-team, business-growth, project-management bundles; ceo-advisor + cto-advisor. Skills whose names collided with collection #1 were skipped (that collection takes precedence). |
| 6 | Landing Page Mastery | [alexdcd/Mafia-Claude-Skills](https://github.com/alexdcd/Mafia-Claude-Skills) | Apache-2.0 | `landing-page-mastery` (note: outputs Spanish by default — ask for English) |
| 7 | Anthropic Skill Creator | [anthropics/skills](https://github.com/anthropics/skills) | See `skill-creator/LICENSE` | `skill-creator` (build your own skills) |
| 8 | Snyk Fix | [snyk/studio-recipes](https://github.com/snyk/studio-recipes) | Apache-2.0 | `snyk-fix` (vulnerability scan + remediation) |

## Prerequisites for specific skills

- **pptx**: `pip install "markitdown[pptx]" Pillow`, `npm install -g pptxgenjs`, and LibreOffice (for PDF conversion / visual QA).
- **snyk-fix**: requires the Snyk MCP server configured in Claude Code, plus a Snyk account/CLI auth.
- Skills with `scripts/` directories run bundled Python (stdlib-only) helpers.

## Security review

Per the article's guidance, all skill files and bundled scripts were scanned
before installation for prompt-injection phrases, piped shell downloads,
base64-decoded payloads, credential/SSH-key access, and unexpected network or
subprocess calls. No malicious patterns were found. Network access in bundled
scripts is limited to URLs the user explicitly provides (SEO/CRO auditors);
subprocess use is limited to git and LibreOffice.

Re-review any skill after pulling upstream updates.
