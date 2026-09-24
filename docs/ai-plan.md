# Optional Local Read-Only Reporting Assistant

**Status:** Deferred; no AI code, model, or client dependency is present. The attendance MVP must be complete and useful with this component absent.

## Allowed boundary

If implemented later, run a local model only. A narrow runner may call allowlisted, admin-authorized aggregate report endpoints with bounded date/class arguments. The model receives aggregate results by default, not names, roll numbers, event rows, device tokens, sensor slots, fingerprint images, or templates. Do not make cloud calls.

The model cannot query SQLite, generate SQL, call arbitrary URLs, change configuration, create/delete students, alter records, enroll fingerprints, or control hardware. Validate tool name/arguments in deterministic code. Enforce caller auth and date/rate limits outside the model.

## Output and failure behavior

Present database counts/date scope as source facts and label any natural-language wording as a model-generated explanation. Never let the model invent missing values; say when results are unavailable. Keep raw result provenance available to the operator. If model/runtime is unavailable or slow, report that and leave ordinary dashboard/report paths unaffected.

No separate AI API is part of the core contract. Do not add Ollama or a model download until the core MVP is tested and the privacy/latency/storage cost is accepted. See [privacy/security](privacy-security.md).
