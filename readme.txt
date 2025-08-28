ChatGPT said:
JIRA Story: Add Physical Model to Domain & Full Name to Prevent Overwrites in Target Physical Data Dictionary
Summary

Update the “Target Physical Data Dictionary” community so domains and asset Full Name values include Physical Model Name, preventing table/column overwrites when different physical models reuse the same table name within the same container.

Description (Problem + What to Build)

Current state

Community: Target Physical Data Dictionary

Domain naming: {CMDB Asset ID}.{Container Type} under subcommunity {CMDB Asset ID}

Full Name patterns:

Table: {CMDB Asset ID}.{Container Type}.{Table_Name}

Column: {CMDB Asset ID}.{Container Type}.{Table_Name}.{Column Name}

Issue: If two different physical models have the same {Table_Name} in the same {Container Type}, ingesting the second model overwrites the first asset because the Full Name collides.

Target state

Domain naming becomes:
{CMDB Asset ID}.{Physical Model Name}.{Container Type}

Full Name patterns become:

Table: {CMDB Asset ID}.{Physical Model Name}.{Container Type}.{Table_Name}

Column: {CMDB Asset ID}.{Physical Model Name}.{Container Type}.{Table_Name}.{Column Name}

Outcome: Assets from distinct physical models no longer collide; each model lives in its own domain and has unique Full Names.

Scope of this story

Implement new Domain Builder logic that includes Physical Model Name.

Implement new Full Name Constructor for Table and Column assets.

Modify ingest/update logic to enforce uniqueness using the new pattern and never overwrite assets from other physical models.

Run one ingest for each of the 5 attached files (each file = distinct physical model), resulting in 5 domains with the following expected table counts:

CMI_AWS_PDD_1_METADATA_FINAL → 396

CMI_AWS_PDD_ET0BOP_PDD_1_METADATA_FINAL → 106

CMI_AWS_PDD_ET0EUCP_PDD_1_METADATA_FINAL → 4

CMI_AWS_PDD_ET0MSTRP_PDD_1_METADATA_FINAL → 100

CMI_AWS_PDD_ET0STGP_PDD_1_METADATA_FINAL → 186

Total tables expected across 5 domains: 792

Backward-compatibility handling for any legacy assets (no deletes in this story; mark legacy pattern as deprecated via a property and preserve relationships).

Assumptions

Physical Model Name for a load is taken from the source file’s base name (without extension) exactly as provided above.

“Container Type” strings remain unchanged (no dots introduced).

Dots (.) remain the delimiter in Full Name. Underscores in model names are allowed.

Case-insensitive comparisons; trim surrounding whitespace during construction.

Out of scope

Deleting or renaming any legacy domains/assets.

Changing any Business Glossary linkages beyond re-pointing by Full Name during ingest.

UI changes in Collibra; this is loader/workflow/config + metadata policy work.

Acceptance Criteria (Functions that work)

Domain Builder works

Given {CMDB Asset ID}, {Physical Model Name}, {Container Type}, the system creates or reuses domain {CMDB Asset ID}.{Physical Model Name}.{Container Type} under the correct community hierarchy.

Domain creation is idempotent (re-running does not create duplicates).

Table Full Name Constructor works

For each table row, the constructed Full Name equals
{CMDB Asset ID}.{Physical Model Name}.{Container Type}.{Table_Name}.

Names are trimmed; multiple spaces collapse to single; no leading/trailing dots.

Column Full Name Constructor works

For each column row, the constructed Full Name equals
{CMDB Asset ID}.{Physical Model Name}.{Container Type}.{Table_Name}.{Column Name}.

Column’s is part of relationship correctly targets the Table asset created with the new Full Name.

Uniqueness & No-Overwrite works

When two different physical models contain the same {Table_Name} for the same {Container Type}, ingest creates two distinct Table assets (one per model) and does not overwrite either.

Re-running the same file updates only its own model’s assets (no cross-model updates).

Counts per Domain work

After ingest:

Domain for CMI_AWS_PDD_1_METADATA_FINAL contains 396 table assets.

Domain for CMI_AWS_PDD_ET0BOP_PDD_1_METADATA_FINAL contains 106 table assets.

Domain for CMI_AWS_PDD_ET0EUCP_PDD_1_METADATA_FINAL contains 4 table assets.

Domain for CMI_AWS_PDD_ET0MSTRP_PDD_1_METADATA_FINAL contains 100 table assets.

Domain for CMI_AWS_PDD_ET0STGP_PDD_1_METADATA_FINAL contains 186 table assets.

Collision Guard works

If a would-be Full Name equals an existing asset from a different model, loader raises a collision warning and continues (no overwrites). The conflicting record is logged with file name, row number, and computed Full Name.

Logging & Audit work

Loader output reports, per file: domains created/reused, tables created/updated, columns created/updated, relationships created, and any collisions/warnings.

A CSV log is produced and attached to the JIRA or stored in the designated logs location.

Legacy Asset Protection works

Any pre-existing assets with the old Full Name pattern are left intact.

If an old-pattern asset corresponds to a new-pattern asset, both can co-exist; the loader sets a property on the new asset: Legacy Full Name = {old pattern} when determinable.

Search & Reference work

Searching by {CMDB Asset ID}, {Physical Model Name}, {Table_Name} returns only assets within that model’s domain (e.g., a search filtered to model = CMI_AWS_PDD_ET0BOP_PDD_1_METADATA_FINAL returns its 106 tables).

Idempotent Re-run works

Re-running a file produces 0 overwrites outside its model and consistent counts within its own domain.

Deliverables

Updated loader/workflow/config implementing the new Domain and Full Name patterns.

Configuration or code for sanitization/normalization (trim, collapse spaces).

Uniqueness enforcement (by Full Name) at Table & Column levels under the new scheme.

One execution per attached file with logs.

Brief runbook (1–2 pages) explaining the new patterns and how to validate.

Validation Steps (QA Checklist)

Ingest each of the 5 files individually; confirm the domain is {CMDB Asset ID}.{Physical Model Name}.{Container Type}.

For each domain, verify table counts match AC #5 (396 / 106 / 4 / 100 / 186).

Spot-check 5 random tables per domain and 5 random columns under each: verify Full Name string follows new pattern and relationships resolve to the correct parent table.

Re-ingest one file and confirm no cross-model updates and counts remain stable.

Attempt a synthetic collision (same table name across models) and confirm no overwrite; collision logged.

Technical Notes / Implementation Details

Extract Physical Model Name: Use source file base name (e.g., CMI_AWS_PDD_ET0BOP_PDD_1_METADATA_FINAL).

Full Name delimiter: . between segments; do not replace underscores within segments.

Normalization: trim(), collapse multiple whitespace to single space in segment names; strip delimiter artifacts.

Idempotency: Use deterministic lookups by the new Full Name (and domain) when deciding create vs update.

Legacy handling: If the old Full Name can be computed from inputs, populate Legacy Full Name on the new asset for traceability.

Safety: No deletes in this story.

Sub-Tasks

Update Domain Builder to include {Physical Model Name}.

Update Full Name constructors for Table and Column assets.

Update ingest/upsert logic to key by new Full Name and domain; prevent cross-model overwrites.

Add collision detection + structured logging (CSV).

Run ingest for the 5 files; attach logs and screenshots of counts.

Write mini runbook + update Confluence documentation.

Risks & Mitigations

Downstream dependencies expecting old Full Names → Mitigation: keep legacy assets intact; add Legacy Full Name property on new assets; communicate change.

Special characters in model/table/column names → Mitigation: trim/collapse spaces; maintain underscores; reject or log on invalid delimiter usage if encountered.

Human error in file/model mapping → Mitigation: model name pulled directly from file base name to reduce manual entry.

Definition of Done

All Acceptance Criteria pass.

5 domains created with verified table counts (396 / 106 / 4 / 100 / 186).

No overwrite incidents across models; collisions (if any) logged.

Documentation/runbook published and linked to the story.
