# Contributing

Improve decisions demonstrated by real tasks, rather than adding instructions for every conceivable failure. Keep the installed skill self-contained. Put detail behind relevant links, and keep repository maintenance tools outside the installed skill.

## Check a change

From the repository root, using Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v
python scripts/release.py
```

These commands check packaging and synthetic local runtime invariants, including a deliberately interrupted child and short timeout. They do not run user jobs or call models. Optional LangGraph tests skip when its requirements are absent; use an isolated environment with `docs/requirements-langgraph.txt` to run them. If your environment provides a skill validator, run it separately against `skills/agent-workflow`; it is not a package dependency.

For changes to instructions or discovery, follow the [behavior evaluation guide](evals/README.md). Keep the actor's inputs separate from the grading criteria. Report actual tool actions and resulting artifacts, including unrelated changes or missing requested work. Do not report an unexecuted scenario as passing.

## Report a useful problem

Include the user request, invocation type (direct or scheduled), model/host version, synthetic initial records, relevant tool trace, observed action, and the expected outcome. Name the version or content hash tested. For a prose change, compare the old and new bytes under the same conditions where practical; disclose when only a design review was possible.

Prefer a narrow correction supported by the failure. Preserve requested scope, existing authorization, and existing task records. Check both that useful work continues and that the skill avoids unrequested work. Examples and scenario categories are not instructions to build every imaginable mechanism.

## Keep private material out

Use invented tasks and fixtures. Do not submit private code, raw operational records, real job identifiers, personal machine paths, internal metrics, credentials, or private conversation excerpts. Reproduce the failure with a synthetic case instead.

The release script uses an explicit list of public root files and public directories. It excludes `research/evidence/` and unexpected root files even if `.gitignore` changes. Every supported text file inside a public directory is included, so do not keep private notes there. Symlinks and unsupported file types are rejected. Public upstream source snapshots are local research evidence, not vendored dependencies.

Before sharing, optionally add private names or identifiers to a local UTF-8 file **outside this repository**, one literal per line:

```bash
python scripts/release.py --private-terms ../private-terms.txt
python scripts/release.py --private-terms ../private-terms.txt --output ../agent-workflow-kit-release.zip
```

Do not commit that file. Findings identify the rule and file without printing the matched private text. Pattern checks cannot recognize every secret or sensitive idea; review every release member before sharing. The ZIP contains a SHA-256 manifest and exactly the bytes that passed inspection. Reproducibility applies to unchanged source and the same build environment.

When preparing a public repository from a private authoring workspace, use a new directory containing only the checked archive's files. Do not upload the authoring workspace or its Git history: ignored research evidence and local files can still exist there. Verify the extracted files against the release manifest. Keep private-term lists, field observations, and user-specific runtime adapters outside that directory. The email check rejects email-shaped contact details as well as other sensitive patterns; use a public issue URL for contact in this kit.

## Scope of automation

The CI configuration runs offline checks only. Live agent evaluations need a disposable workspace and explicit tool/cost boundaries; they do not run automatically on public pull requests. Publishing a release, configuring a scheduler, and changing a user's existing automation are separate actions from maintaining this skill.
