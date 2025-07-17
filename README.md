──────────────────────────────────────────  
AI-STYLE DATA PIPELINE – GRANULAR, RIGOROUS HIGH-LEVEL OUTLINE  
Version 0.9 (living document)  
──────────────────────────────────────────  

The outline is **layer-oriented**: each layer is a **replaceable module** with **strict in/out contracts**.  
All code lives in a **monorepo** (`ai-style-pipeline/`) and is **test-driven** (TDD).  
CI runs nightly; prod runs on a single cron job.

---

### 🔍 LAYER-0:  REQUIREMENTS & CONTRACTS
| Artifact | Location | Content |
|---|---|---|
| `requirements.txt` | repo root | pinned major/minor versions only |
| `contracts/` | repo root | JSON schemas for every I/O interface |
| `docs/adr/` | repo root | Architecture Decision Records (markdown) |

---

### 🔧 LAYER-1:  INFRASTRUCTURE BOOTSTRAP
| Module | Tech | Responsibility |
|---|---|---|
| `infra/docker/` | Docker + Compose | reproducible dev & prod images |
| `infra/ci/` | GitHub Actions | lint, unit tests, nightly pipeline run |
| `infra/cron/` | systemd timer | nightly call to `orchestrator.sh` |

---

### 🗂️ LAYER-2:  DATA INGESTION
| Module | Library vs Hand-written | I/O Contract |
|---|---|---|
| `ingest/hot_folder.py` | **Hand-written** (15 LOC) | watches `~/drop/` → `ingest/YYYY-MM-DD/` |
| `ingest/extract.py` | **Library** (`ffmpeg-python`) | `*.mp4` → PNG frames |
| `ingest/validate.py` | **Hand-written** (pytest) | reject non-image/video, log checksum |

---

### 🧹 LAYER-3:  CURATION ENGINE
| Module | Library vs Hand-written | Purpose |
|---|---|---|
| `curation/dedup.py` | **Library** (`imagehash`) + 20 LOC wrapper | perceptual-hash dedupe |
| `curation/quality_gate.py` | **Hand-written** + OpenCV | SSIM ≥ 0.85, face filter |
| `curation/auto_curate.py` | **Library** (`faiss`, `hdbscan`) | keep outliers vs dense clusters |
| `curation/ontology.py` | **Hand-written dataclass** | load & validate `ontology.json` |

Tests:  
- `tests/test_curation.py` (pytest, CI gate)  
- mocks use **fixture frames** under `tests/fixtures/`

---

### 📝 LAYER-4:  CAPTIONING
| Module | Library vs Hand-written | Purpose |
|---|---|---|
| `caption/ontology_templates.py` | **Hand-written** dataclass | build prompt string from ontology |
| `caption/finetune_blip.py` | **Library** (HF PEFT) | LoRA fine-tune on seed captions |
| `caption/auto_caption.py` | **Hand-written** | apply fine-tuned BLIP-2 to frames |
| `caption/validate_captions.py` | **Hand-written** + pytest | ensure tokens ⊆ ontology vocabulary |

---

### 🎓 LAYER-5:  TRAINING
| Module | Library vs Hand-written | Purpose |
|---|---|---|
| `train/config.py` | **Hand-written** Pydantic schema | single YAML → runtime dataclass |
| `train/adapter.py` | **Library** (PEFT) | 16-dim LoRA wrapper |
| `train/reward_model.py` | **Hand-written** (tiny MLP) | CLIP-H → scalar “brand score” |
| `train/trainer.py` | **Hand-written** 150 LOC | orchestrates diffusion + reward |
| `train/evaluate.py` | **Hand-written** | FID, brand_score, CLIP aesthetic |

All training code is **100 % deterministic**; seeds logged.

---

### 🚀 LAYER-6:  ORCHESTRATOR & CLI
| Module | Library vs Hand-written | Purpose |
|---|---|---|
| `orchestrator.sh` | **Hand-written** bash 30 LOC | nightly cron entry |
| `cli/main.py` | **Typer** (CLI lib) | `python -m cli train --config configs/base.yml` |
| `cli/serve.py` | **FastAPI** | REST endpoint for inference slider |

---

### 🧪 LAYER-7:  TESTING & QA
| Type | Coverage Target | Tool |
|---|---|---|
| Unit tests | ≥ 80 % | pytest + coverage |
| Integration test | nightly | GitHub Action spins container, runs full pipeline on 5 mock frames |
| Static analysis | 100 % | `ruff`, `mypy --strict` |
| Repro check | nightly | CI produces SHA-256 of final LoRA; compare to previous night |

---

### 📦 LAYER-8:  ARTIFACT HANDLING
| Artifact | Storage | Retention |
|---|---|---|
| Raw frames | S3 / Wasabi / local NAS | 90 days |
| Curated frames | `data/approved/` (Git-LFS) | indefinite |
| LoRA weights | `models/` (Git-LFS) | last 3 versions |
| Metrics | `metrics/YYYY-MM-DD.json` | 30 days |
| Docker images | GH Container Registry | last 5 tags |

---

### 🔁 LAYER-9:  CHANGE MANAGEMENT
- **ADR template** in `docs/adr/000-template.md`  
- **Semantic versioning**: `vMAJOR.MINOR.PATCH`  
  - MAJOR = ontology changes  
  - MINOR = new library bump  
  - PATCH = bug-fix  
- **Feature flags** via `config.yml` toggles (never if-statements).

---

### 🛡️ LAYER-10:  SECURITY / LICENSE
- **License**: MIT for code, CC-BY-NC 4.0 for datasets.  
- **Secrets**: none stored in repo (use GitHub secrets).  
- **Supply-chain scan**: `pip-audit` nightly.

---

### 📅 DELIVERY ROADMAP (2-week sprints)
| Sprint | Deliverable |
|---|---|
| 1 | hot-folder, dedup, quality gate, ontology schema |
| 2 | auto-curate, BLIP-2 fine-tune, first LoRA |
| 3 | reward model, CLI, CI pipeline |
| 4 | REST API, nightly cron, public micro-drop |

---

### 🧑‍💻 CONTRIBUTOR GUIDE
- `CONTRIBUTING.md` enforces **conventional commits** (`feat:`, `fix:`, `docs:`).  
- Pre-commit hooks: lint, test, ontology JSON schema check.  
- All modules expose `__main__.py` so any file is runnable:  
  `python -m curation.auto_curate --help`.
