# AGENTS.md

## Cursor Cloud specific instructions

This repository is **documentation plus offline Python tooling** for EMG/KMG IT architecture (`docs/`) and two generators under `scripts/`. There is no web app, database, or long-running service to start.

### Dependencies

- **Python 3** (stdlib + pip).
- **`drawpyo`** — `pip3 install -r requirements.txt` (used by `scripts/mmd_to_drawio.py`).
- **`openpyxl`** — `pip3 install openpyxl` (used by `scripts/generate_qa_interview_excel.py`; not listed in `requirements.txt`).

The VM update script installs both packages on each session start.

### Lint / tests

There is no project linter or test suite. Use:

```bash
python3 -m compileall -q scripts
```

as a quick syntax check before running scripts.

### Core workflows (hello-world)

**Regenerate draw.io from Mermaid** (writes to `docs/drawio/`):

```bash
python3 scripts/mmd_to_drawio.py
```

Sources: `docs/svg/*.mmd`, `docs/it-landscape-emg.mmd`. See `docs/drawio/README.md`.

**Regenerate QA interview Excel**:

```bash
python3 scripts/generate_qa_interview_excel.py
```

Output: `docs/QA_Interview_Evaluation.xlsx`. See `docs/README_interview_excel.md`.

### Ports and external systems

Nothing in this repo listens on a network port. Production systems described in `docs/architecture-emg-integrations.md` (ABAI, SAP, ИМ, etc.) are external and cannot be run from this codebase.
