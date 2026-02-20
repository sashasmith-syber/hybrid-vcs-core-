# GitHub Copilot – Hybrid VCS Repository Instructions

## 1. Project identity and goals

You are an AI coding agent working in the **Hybrid VCS** ecosystem.

Hybrid VCS is a **local‑first version control system** for web content and development artifacts that combines Git's reliability with SQLite's flexibility.  
It integrates with tools like the **Comet** browser extension and the **Spider Entity** web crawler to capture, version, and compress web content with full Git history while keeping everything under operator control.

Your primary goals:

- Implement and maintain core Hybrid VCS functionality (Git + SQLite + compression + APIs).  
- Safely extend the Spider Entity crawler and related tools without breaking robots.txt compliance or storage constraints.  
- Preserve local‑first, privacy‑respecting behavior and adhere to strict security practices from the PROTOS‑1 security architecture.

Always favor **correctness, safety, and maintainability** over clever or speculative changes.

---

## 2. How to build, run, and test

Before writing or modifying code, ensure any change can be built and tested end‑to‑end.

### 2.1 Backend / core services

Use the documented quickstart flow for the Hybrid VCS backend:

- Clone and set up the project:
  - `git clone <repo-url>`
  - `cd hybrid-vcs-core-`
- Install dependencies:
  - `pip install -r requirements.txt`
- Run local backend:
  - `python run_local.py`
- Health check:
  - `curl http://localhost:8081/health`  
    Expect JSON like `{"status": "healthy", "connected": true}`.

When you add or modify backend code:

- Prefer adding or updating **tests** that can be run via the project's standard test commands (e.g., `python quick_start.py`, `pytest` suites, or documented equivalents).  
- If you introduce new entrypoints or scripts, document their usage in the README or appropriate docs.

### 2.2 Spider Entity web crawler

Spider Entity is a web crawler integrated with Hybrid VCS. It must remain compliant, resource‑aware, and safe.

Deployment and run options (do not change defaults without a clear reason):

- Local:
  - `python deploy_spider.py --method local`
- Docker:
  - `python deploy_spider.py --method docker`
- systemd:
  - `python deploy_spider.py --method systemd`
- Start crawling with config:
  - `python spider_entity.py --config spider_config.json`

Key monitoring endpoints:

- Health: `http://localhost:8080/health`
- Status: `http://localhost:8080/status`
- Metrics: `http://localhost:9090/metrics`
- WebSocket updates: `ws://localhost:8080/ws`

When editing Spider Entity:

- Keep **robots.txt compliance and rate limiting** intact (`respect_robots: true`, `delay`, `max_pages`, `max_depth`).  
- Maintain SQLite‑based storage and Git integration, including automated commit strategies.  
- Don't introduce breaking changes to public REST APIs (`/api/crawl/start`, `/api/crawl/stop`, `/api/status`, `/api/metrics`, `/api/config`) without clear versioning and documentation.

---

## 3. Coding standards and architecture expectations

### 3.1 General style

- Follow the existing language and framework conventions in this repo (Python for backend/crawler, any existing React/Vite front‑end templates where present).  
- Prefer **clear, explicit code** over clever one‑liners.  
- Add docstrings and inline comments where behavior is non‑obvious, especially around data stores, crawling logic, and security‑relevant checks.

If you see existing ESLint / type‑checking or Python tooling, configure new files to align with those (for instance, Vite + React + TypeScript templates should use the recommended TS‑aware ESLint configs, not ad‑hoc settings).

### 3.2 Hybrid VCS core

For code interacting with the Hybrid VCS core:

- Treat Git as the **source of truth** for version history; SQLite is for flexible querying and metadata.  
- Ensure operations are **idempotent** where possible (e.g., capturing the same page again should not corrupt earlier versions).  
- Preserve compression and storage efficiency; do not store redundant blobs when a compressed format or deduplication strategy is already present.

When making schema changes in SQLite:

- Provide migration steps.  
- Maintain compatibility with existing data if feasible, or clearly document breaking changes.

### 3.3 Spider Entity crawling architecture

Spider Entity components include: Crawler engine, `SpiderEntity` orchestrator, `DatabaseManager` (SQLite), Git integration module, compression engine, monitoring, and deployment scripts.

When editing or adding modules:

- Keep crawler code **asynchronous** and non‑blocking where it already is async.  
- Respect existing interfaces for:
  - `DatabaseManager` (storage and retrieval of crawled content).  
  - Git integration (commit frequency, message templates like `Crawl batch {batch_id} pages {pages}`).  
  - Compression settings (`algorithm`, `level`, `chunk_size`).
- Ensure monitoring hooks remain intact and continue to expose useful metrics for Grafana / Prometheus dashboards.

---

## 4. Security, privacy, and PROTOS‑1 constraints

Security is **non‑negotiable** and follows the PROTOS‑1 Maximum Security Protocol.

When proposing or implementing changes:

- Do **not** log secrets, tokens, or personally identifiable information.  
- Use environment variables or secret management for credentials; never hard‑code them.  
- Assume a **Zero‑Trust** model: validate all inputs, even if they come from internal services.

### 4.1 Input sanitization and validation

Apply strong input validation in line with the Input Sanitization Matrix:

- Validate and sanitize all external input (HTTP APIs, configs, URLs, shell args).  
- Prefer parameterized queries for any database interaction; avoid raw string concatenation.  
- For shell or OS commands, avoid direct execution where possible; if necessary, use whitelists and sanitized arguments.

### 4.2 Encryption and network security

- Use TLS/HTTPS for all outbound HTTP requests in production; do not disable certificate verification.  
- Encrypt sensitive data at rest where feasible (e.g., stored credentials, API tokens).  
- Follow the principle of least privilege: request only the permissions and network access that a component needs.

### 4.3 Dependency management

- Pin or constrain dependency versions in `requirements.txt` to avoid supply‑chain surprises.  
- Review new dependencies for known vulnerabilities before adding them.  
- Prefer well‑maintained libraries with a clear security track record.

---

## 5. Robots.txt and crawling compliance

Spider Entity **must** respect the following constraints at all times:

- Honor `robots.txt` directives for every domain (`respect_robots: true` must never be disabled without explicit operator override and documentation).  
- Enforce configurable rate limiting (`delay_seconds` in `spider_config.json`) and never exceed `max_pages` or `max_depth` without explicit configuration.  
- Identify the crawler honestly via `user_agent` (e.g., `HybridVCS-Spider/1.0`).  
- Do not follow redirects to out‑of‑scope domains unless explicitly configured via `allowed_domains`.

---

## 6. Commit and change hygiene

- Write clear, imperative commit messages (e.g., `Add robots.txt compliance check`, `Fix SQL injection in query builder`).  
- Keep PRs focused: one logical change per PR.  
- Update `CHANGELOG.md` and `RELEASE_NOTES.md` for any user‑visible changes.  
- Do not commit secrets, credentials, or large binary assets; use `.gitignore` to exclude build artifacts, `venv/`, `__pycache__/`, and similar.
