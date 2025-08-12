Executive Presentation: DSET Enablement Tool
1. Background
The Dataset (DSET) Enablement Tool is a Collibra workflow designed to streamline Attribute Rationalization.

Attribute IDs uniquely represent business concepts, while Physical Names are field-level names that vary across datasets (e.g., Loan Identifier → LN_ID, LN_FC_ID, LN_ALT_ID).

Without automation, mapping Physical Names to the correct Attribute IDs requires time-consuming, manual review against the Enterprise Data Glossary (EDG) and registered datasets.

This tool was built to:

Reduce effort

Increase accuracy

Standardize data registration

Accelerate dataset onboarding

2. Purpose
Provide users a guided, automated way to populate Attribute IDs for datasets being onboarded into Collibra.

Leverage existing registered datasets and the Enterprise Data Glossary to:

Validate user-entered Attribute IDs.

Suggest matches based on proven mappings.

Flag operational or invalid entries for review.

3. Problem Statement
Current challenge:

Business and technical teams spend excessive time manually searching for Attribute IDs when registering datasets.

Risk of inconsistent mappings if teams use outdated or incorrect IDs.

Manual rationalization is error-prone and slows down data onboarding.

Impact:

Inconsistent metadata.

Delays in dataset registration.

Reduced trust in metadata quality.

4. Goal
Automate and simplify Attribute Rationalization so users can:

Confidently register datasets with accurate Attribute IDs.

Reduce turnaround time for dataset onboarding.

Improve metadata consistency across the enterprise.

5. Demo Outline — Business Features to Show
A. Input Stage
Upload DSET Template

Show the two tabs: Dataset Information (ignored) and Attribute Information (used for matching).

Highlight typical user input (Physical Names filled in, Attribute IDs blank or partially filled).

B. Matching & Validation
Automatic Physical Name Matching

Explain that matching is exact, case-insensitive, whitespace normalized.

Show how:

Single exact match → Attribute ID auto-filled (green).

Multiple matches → Logged in “Attribute Log” for review.

No matches → Left blank + “No recommendations” in log.

Validation of Existing IDs

Green = valid (found in accepted EDG).

Red = invalid (not in accepted EDG).

Orange = operational attribute (ATTR08105).

C. Attribute Log
Reviewing Suggestions

Show the “Attribute Log” tab with:

Physical Name

Suggested Attribute IDs

Attribute Names

Source Dataset

Status (“Multiple matches”, “No recommendations”, “Conflict with user-provided ID”)

Explain how this helps resolve ambiguity quickly.

D. Speed & Accuracy
Execution Speed

Run the tool live to demonstrate processing hundreds of rows in seconds using preloaded caches.

Accuracy Gains

Show before/after example where the tool:

Corrected invalid IDs.

Auto-filled blank IDs.

Flagged operational attributes.

E. Business Impact
Efficiency

Quantify reduction in manual effort (e.g., “1 hour of work reduced to <5 minutes”).

Consistency

Show how centralizing EDG & dataset registry lookups ensures uniform attribute usage.

6. Key Talking Points for Executives
Why it matters: Cuts down onboarding time, reduces errors, and increases trust in metadata.

Low learning curve: Business users can use it without deep technical knowledge.

Scalable: Handles large datasets efficiently.

Future-ready: Can expand to fuzzy matching, synonym support, and attribute relationship mapping.

If you’d like, I can also make you a one-slide visual showing the workflow from User Upload → Cache Lookup → Matching & Coloring → Output & Review, which would make the presentation more executive-friendly.

Do you want me to create that visual diagram for the deck? It’ll make the demo flow click instantly.
