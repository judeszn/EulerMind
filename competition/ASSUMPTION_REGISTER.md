# Assumption Register (Sprint Δ1)

Every unresolved competition assumption, so unknowns cannot quietly
become design decisions. Competition-side twin of the Evidence
Protocol's Pending Clarifications: an assumption is **Confirmed** only
by a primary source (rules text, template text, profiler source, or an
organizer answer) — never by plausibility.

| ID | Assumption | Status | Impact | Source / resolution path |
|---|---|---|---|---|
| A-01 | Judges (and an LLM-based audit system) read REPORT.md | **Confirmed** | High | Template README: "Judges and the LLM-based audit system will read this" |
| A-02 | Judged `test_prompts` responses come from the submission's application code, not the bare GGUF | **Unknown** | **Critical** | Profiler never generates responses — mechanism is outside it. → Organizer question Q1. World A (bare GGUF): kernel earns credit only via REPORT/demo. World B (application): certified answers at judging time — decisive differentiator |
| A-03 | Hidden math validation subset resembles GSM8K-style problems | **Unknown** | High | Devpost: "validation sets are provided for each [domain]" — locate the official math set via portal/Discord; until then gsm8k+arc_easy proxies are assumptions |
| A-04 | S_perf TPS measured via `llama-bench` generation row (`-p 512 -n 128`) | **Confirmed** | High | Profiler source, `throughput.py` |
| A-05 | S_perf denominator = max TPS observed across all teams (not the 15.0 reference) | **Unknown** | High | Devpost table says TPS_max; notes say TPS_REFERENCE=15.0 provisional. → Organizer question Q2. Smoke run proves a 135M model reaches ~92 TPS, so the difference is enormous |
| A-06 | Audit re-measurement runs on a cloud VM, not a physical Standard Laptop | **Confirmed** | Medium | Profiler source: `measured_on: "audit_cloud_vm"`. Consequence: CI-VM numbers minimize drift-flag risk |
| A-07 | Scoring uses our 2 test prompts + 2 hidden organizer prompts (4 total) | **Confirmed** | Medium | Template README, rule 7 |
| A-08 | `packaging: docker_build_from_repo` permits wrapping inference in application code at audit time | **Unknown** | **Critical** | Schema allows the value; semantics undocumented. → Organizer question Q3. Linked to A-02 |
| A-09 | Automated accuracy = `lm_eval` on the bare GGUF against the hidden subset | **Confirmed** (mechanism) / **Unknown** (task) | High | Profiler source, `accuracy.py`: "Real audits use the full hidden 30% validation subset" |
| A-10 | P_thermal is effectively 0 on the audit cloud VM (no exposed sensors) | **Likely, unmeasured** | Low | Smoke run: `core_temp_c_peak: null, throttled: false` on CI VM — same class of environment |
| A-11 | The final submission must be a clean template-shaped repo (not this research repo restructured) | **Assumed, unconfirmed** | Medium | Template says "fork this repository"; a separate clean submission repo citing this one avoids the risk entirely — decision pending |

**Update rule:** an assumption moves to Confirmed/Refuted only with the
source quoted in this table. Any design decision that depends on an
Unknown assumption must name the assumption ID in its decision record.
