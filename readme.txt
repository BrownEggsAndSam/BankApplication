# Data Set Compliance & EDG Scorecard Discussion

## Question: Can a data set have a low EDG score (e.g., 12%) and still be in **Accepted** status?

**Answer:** - **Yes.** - The **Accepted** status only means the data set
has passed the workflow and is allowed through the governance process. -
The EDG score is evaluated separately. - For **High DGR (High
Governance) assets**, curators are expected to have an EDG score close
to **100%** (typically **90%+ is considered acceptable**). - For
**Medium and Low DGR assets**, the EDG score is **not a governance
requirement**, so even a very low score does not matter.

## Question: When should the EDG Scorecard actually be used?

**Answer:** - Only for **High DGR assets**. - Logic should be: - **High
DGR** - Include EDG Scorecard in compliance calculations. - **Medium /
Low DGR** - Ignore the EDG Scorecard entirely. - It is not a meaningful
metric for compliance.

## Question: Does the STTM Scorecard follow the same rule?

**Answer:** - Yes. - For Medium and Low DGR assets: - Attribute
rationalization is not required. - Therefore STTM scorecard values are
also not important. - STTM compliance mainly matters for High DGR
assets.

## Question: What should the Data Set Compliance metric actually be?

Current example: - **595 Accepted out of 757 total**

**Answer:** - That is generally the correct direction. - The compliance
metric should represent: - Accepted data sets. - Minus obsolete/retired
data sets (depending on final rules). - Additional status logic still
needs to be finalized.

## Question: Should Approved data sets count the same as Accepted?

**Answer:** - Probably **yes**. - Some data sets are **Approved** but
cannot be vended because of other restrictions. - Governance needs to
confirm whether Approved receives the same weight as Accepted.

## Question: What about Contract Restricted data sets?

**Answer:** - Third-party purchased data may have contractual sharing
restrictions. - These data sets: - Remain in **Accepted** status. - Pass
governance rules. - **Cannot be vended downstream.** - They should
likely be excluded from ICR compliance calculations.

## Question: Which statuses should be ignored?

**Answer:** Ignore: - Candidate - Retired

Reason: - Candidate = incomplete or half-built. - Retired = no longer
active.

## Question: Who defines the weighting and filtering rules?

**Answer:** Governance owners: - Matt - Charu

They will determine: - Which statuses count. - Which statuses are
excluded. - Weighting of statuses. - Final governance calculation rules.

## Question: Is Data Set Compliance different from Release Review Compliance?

**Answer:** Yes.

### Data Set Compliance

Measures: - Accepted percentage. - EDG Scorecard (High DGR only). - STTM
completion. - Overall governance.

### Release Review Compliance

Includes: - Data Exchange - Cloud Compliance - Data Model Compliance -
AR Compliance - NPI Compliance - Release Review

Notes: - N/A values are excluded from the denominator. - A separate
Release Review scorecard has already been created with Sangi.

## Question: Which STTM requirements actually matter?

**Answer (per Charu):** For compliance she only cares that: - STTM tab
is completed. - Required attributes pass. - These checks only apply to
High DGR assets.

She does **not** consider EDG Review Status itself to be the governing
requirement.

## Question: Should EDG Review Status drive compliance?

**Answer:** Probably not. - EDG Review Status depends on several other
governance factors. - Compliance should instead be based on the actual
governance requirements.

## Question: How does STTM connect to the Data Set Compliance table?

**Answer:** Originally STTM existed at: - Interface level. - Data Flow
level.

Both relationships were tracked separately.

## Question: What changed in the new model?

**Answer:** STTM has moved to the **Producer Offering** level.

Relationship:

``` text
Producer Offering
        │
        ├── Interface
        │
        └── Data Flow
```

Important notes: - One Interface can have one or more Producer
Offerings. - Producer Offering is now an additional entity to account
for. - STTM linkage will likely need to move from Interface/Data Flow to
Producer Offering. - Final mapping still requires additional discussion.
