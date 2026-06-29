# GTM Container Audit Cleanup

A reusable AI skill for reviewing Google Tag Manager containers with the mindset
of a web analyst, not only a cleanup script.

The goal is simple: help analytics, marketing, and tracking teams understand
whether a GTM container is useful, reliable, readable, and safe to maintain.
It looks for obvious hygiene issues, but it also checks whether tags, triggers,
variables, consent logic, ecommerce values, media payloads, and custom code make
sense for the business action they are supposed to measure.

## Who This Is For

- Web analysts who audit or refactor GTM containers.
- Marketing teams who need cleaner media, conversion, and consent tracking.
- Analytics engineers who need a structured review before touching a container.
- Agencies or consultants who need a repeatable audit and cleanup workflow.
- AI agents such as Codex, Claude Code, or Gemini that need clear GTM audit
  rules and deterministic helper scripts.

## Problems It Helps Solve

- Too many duplicated, obsolete, or poorly named GTM objects.
- Tags that fire in the wrong context or send values in the wrong format.
- GA4 or media tags that use old ecommerce paths, fixed product indexes, or
  fragile helper variables.
- Consent, CMP, and server-side routing setups that are hard to understand.
- Custom HTML or Custom JavaScript that is risky, duplicated, or difficult to
  maintain.
- Cleanup plans that are too superficial, too verbose, or not actionable enough
  for a human reviewer.

The skill is designed to answer one practical question:

> Is this GTM container built in the simplest, clearest, and safest way to
> support the measurement goals?

## How The Review Works

The workflow uses three independent checks before any cleanup recommendation is
made:

1. **Mechanical hygiene check**
   Finds objective issues such as duplicates, unused objects, broken references,
   single-trigger groups, missing triggers, outdated Universal Analytics style
   setup, naming drift, and folder problems.

2. **Business logic check**
   Reviews whether the configuration fits the intended measurement action. For
   example, a purchase tag should use purchase data, item arrays should be used
   where a vendor expects arrays, and a consent variable should not return the
   same result for different consent purposes unless that is intentional.

3. **Custom-code and technical check**
   Reviews Custom HTML, Custom JavaScript variables, and custom templates for
   what they read, what they return or push, which APIs they touch, and whether
   the code is safe and maintainable.

The source model maps where objects and references are located. It is only a
navigation aid. It does not create, suppress, or downgrade findings. Each check
must verify the raw export, API evidence, configuration, or code directly.

## Inputs

The skill can work from one or more of these sources:

- GTM container export JSON.
- GTM API or MCP access, when available.
- GTM UI screenshots or implementation notes.
- Tag Assistant, browser, network, or dataLayer observations.
- Information about the site type, markets, CMP, ecommerce behavior, server-side
  routing, naming rules, and cleanup route.

A GTM export JSON is the best starting point because it is reproducible and can
be checked by the helper scripts.

## Outputs

Depending on the requested mode, the skill can produce:

- An audit summary.
- A cleanup plan workbook for human review.
- Hidden proof tabs or supporting evidence files for analyst continuation.
- A validated GTM import JSON when that route is explicitly chosen.
- A change log after cleanup execution or after a generated cleanup artifact.
- QA instructions for GTM preview, browser testing, vendor requests, and consent
  behavior.

Cleanup plans and change logs are user-facing deliverables. They should explain
what matters, what should change, why it matters, how to QA it, and what remains
blocked. Internal evidence should stay in supporting tabs or files.

## What It Will Not Do

- It will not publish or create a GTM version unless explicitly requested.
- It will not mutate a live container without approval and a safe workspace or
  approved artifact route.
- It will not delete tags only because they are old.
- It will not treat summarized inventory as proof.
- It will not invent custom JavaScript to hide missing website or dataLayer
  requirements.
- It will not give legal or privacy advice as a final decision.

## Repository Structure

- `SKILL.md`: agent-facing workflow and routing instructions.
- `agents/openai.yaml`: Codex skill metadata and default prompt.
- `references/01-skill/`: purpose, users, inputs, outputs, acceptance criteria,
  and non-goals.
- `references/02-commands/`: validation commands, runtime QA templates, and
  forward-test prompts.
- `references/03-rules/`: audit rules, semantic logic, naming, operation
  schema, workbook architecture, change-log rules, and mutation safety.
- `scripts/`: deterministic helpers for source mapping, baseline findings,
  custom-code extraction, semantic scans, reconciliation, validation, and
  release checks.
- `pyproject.toml`: lint configuration for script import hygiene and undefined
  names.

## Useful Commands

Run from the repository root.

Build the protected audit evidence package:

```powershell
python -B scripts/gtm_audit_package_build.py path\to\container.json --out-dir artifacts\audit-package --pretty
```

Run the individual checks when debugging or extending the skill:

```powershell
python -B scripts/gtm_source_model.py path\to\container.json --pretty
python -B scripts/gtm_baseline_audit.py path\to\container.json --pretty
python -B scripts/gtm_custom_code_extract.py path\to\container.json --pretty
python -B scripts/gtm_semantic_source_scan.py path\to\container.json --pretty
```

Validate a release:

```powershell
python -m ruff check scripts
python -B scripts/gtm_self_test.py
python -B scripts/check_release.py --tag vYYYY.MM.DD.N
git diff --check
git status --short
```

## Safety And Privacy

Do not commit client exports, audit workbooks, generated JSON files, screenshots,
container IDs, domains, emails, or temporary reports. This repository should only
contain reusable skill instructions, generic scripts, metadata, and public
documentation.

## Versioning

Releases use Calendar Versioning:

- First release of a day: `vYYYY.MM.DD`
- Same-day follow-up: `vYYYY.MM.DD.N`

Release notes should be written for web analysts and marketing stakeholders:
what improved, why it matters, how it was validated, and what limits remain.
