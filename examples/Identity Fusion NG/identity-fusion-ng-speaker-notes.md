# Identity Fusion NG — speaker notes

Presenter script for the Identity Fusion NG newcomer deck. The YAML specs carry the slides; this file is the manual the SME reads while presenting. Grounded in the Identity Fusion NG docs (Home, Getting started, configuration and operation guides).

Specs: `identity-fusion-ng-slides-01-03.yaml` through `identity-fusion-ng-slides-13-15.yaml`.

---

## Slide 1 — Identity Fusion NG

Identity Fusion NG is an ISC connector. It consolidates managed-source accounts, computes attributes, and optionally matches identities so you are not limited to exact-match correlation.

It supersedes the deprecated v1.x line. Point existing tenants at the migration guide.

The slides are the mental model. These notes plus Home, Getting started, and the configuration guides are the manual. Ask who in the room is greenfield versus v1.

---

## Slide 2 — Why Identity Fusion NG?

The failure mode is one person in HR and AD becoming two identities when correlation finds nothing.

Map aligns schemas and can keep several values. Define mints identifiers and normalises names and dates before comparison. Match scores near-duplicates and sends the grey zone to a reviewer.

Map and Define still pay off with Match off. Records and Orphan are teased here; the cheat sheet is slide 4. Match is not correlation — that lands on slide 11.

Read: Home, Mapping attributes, Defining attributes, Matching identities.

---

## Slide 3 — What is the Map, Define, Match framework?

Order is always Map, then Define, then Match. You can enable one step; you cannot reorder them.

Inputs are managed sources, plus ISC identities when identity scope is on. Identity scope is optional; often the baseline already lives in your sources.

After Match there are four exits: Fusion account, review form, automatic merge, or drop for Records and Orphan. Unique values wait until Match decides. Source type changes the exits only, never the order of steps.

Read: Home framework table, Configuring sources and scope.

---

## Slide 4 — Who participates, and in which step?

Walk the matrix left to right. Seed is who originates the Fusion account, not who merely participates.

Baseline is identities in scope, existing Fusion accounts, and already-correlated accounts. Only uncorrelated managed accounts enter Match. Map still walks every participant, so contributing attributes is not a Match privilege.

Records register unique values and emit no Fusion account on a miss. A matching Orphan attaches to an existing identity; a miss is dropped, and can optionally be disabled on the managed source.

Two meanings of orphan: the source type versus a Fusion account with no contributing accounts left. One connector can mix source types.

Read: Source types, Configuring sources and scope.

---

## Slide 5 — Umbrella or side-car?

Umbrella versus side-car is the Fusion source Authoritative flag, not whether Match runs. Matching runs in both.

Use umbrella when Fusion must create identities. Use side-car for generated usernames, merged attributes, or Records and Orphan sources.

Authoritative, Records, and Orphan name each managed source. Umbrella and side-car name the Fusion source.

Read: Configuring sources and scope.

---

## Slide 6 — How does Map resolve conflicting attributes?

Map runs first. Many source names become one Fusion attribute. First found takes the first non-empty value in configured source order. Keep a list or concatenate when several values are legitimate; concatenate is distinct values in brackets, space separated, duplicates removed. Source name forces one source to win whatever the order says.

Main account uses that snapshot then origin, with no further fallback. Origin account stays on provenance. `originSource` and `originAccount` are set at creation, not merge strategies. Identity scope adds `$identity`; the merge walk stays on configured sources. New configurations default to Main account.

Read: Mapping attributes.

---

## Slide 7 — What does Define compute, and when?

Normal definitions run after Map and before Match so normalised names and dates improve scoring. Unique definitions run after Match: usernames, employee numbers, counters, UUIDs. Collisions retry with `$counter` up to the configured maximum attempts.

Static writes once. Always recalculate runs every aggregation. Empty or failed Normal output clears the stored value; use `$previous` to keep the last value. Records can register unique values without emitting a Fusion account.

Read: Defining attributes, Velocity context.

---

## Slide 8 — What can happen to an account in Match?

Only uncorrelated managed accounts are scored against the baseline. Combined score at or above auto-merge merges. Between the review floor and auto-merge goes to a form. Below the floor is non-match: create an identity when Fusion is authoritative, or drop for Records and Orphan.

Deferred candidates: the only match is another new account from the same source in the same run, so identity creation waits for the next aggregation. Scoring runs when automatic merge is on, or when manual review is on with valid reviewers; otherwise borderline scores register as non-matched.

Read: Matching identities, Match flow, Source types.

---

## Slide 9 — How is a match score built?

Each rule compares one attribute with an algorithm. The minimum similarity is also that rule's weight. Combined score is the weighted mean. A failed mandatory rule vetoes the candidate whatever the combined score says. Skip if missing keeps empty attributes out of the blend.

Use Enhanced Name Matcher for names and Binary for exact identifiers. Jaro-Winkler, LIG3, Dice, Double Metaphone, and custom Velocity stay in these notes. Start the review floor around 80; enable automatic merge only after tuning. Dry-run before production.

Read: Matching identities, Tuning matching algorithms.

---

## Slide 10 — Where do humans fit in?

A review form shows the top candidates; reviewers link to an existing identity or create a new one. The decision applies on the next aggregation, not immediately.

Reviewers are source owners acting globally, or per-source reviewer entitlement holders. Fusion reports and dry-run preview Match without writing.

Statuses this leaves behind: `activeReviews`, `candidate`, `authorized`, `manual`, `auto`. Without automatic merge or valid reviewers, borderline scores register as non-matched.

Read: Review forms and reviewers, Managing reviewers.

---

## Slide 11 — How is correlation different from matching?

Matching decides who this account is. Correlation is the ISC link. You cannot link an account to an identity that does not exist yet, so Fusion creates it first.

Correlate on aggregation PATCHes during the run. Reverse correlation writes an attribute for native ISC rules and needs optimised aggregation switched off. Do not correlate stages the work; matching still runs. An enforced correlation role lets ISC finish links later.

Correlation calls are expensive, so many projects stage them during initial load with do not correlate, then assign an enforced correlation role.

Read: Managing correlation.

---

## Slide 12 — What does a Fusion account give an operator?

Every Fusion account carries provenance: contributing accounts, sources, origin, history. Native identity and account name are set at creation and never rewritten.

Status entitlements are calculated and searchable: `new`, `activeReviews`, `reviewer`, `nonMatched`, `uncorrelated`, `baseline`, `orphan`. Action entitlements are requestable, including `report` and `reviewer:<sourceId>`.

Source data can be aggregated before processing, after a delay, or not at all. Use a UUID when you need a truly immutable identifier.

Read: Standard account schema, Entitlement list.

---

## Slide 13 — What is external processing for?

External settings is one gateway, not a different product. Proxy mode runs connector logic on your infrastructure and streams results back. Scenario recording needs proxy because it writes to disk. External logging posts from ISC, or writes to disk when proxy is on.

Dry-run runs the full pipeline with writes suppressed. Scheduled ISC aggregations never send dry-run input, so use `spcx` or the proxy host.

Read: Proxy mode, Analyze with dry-run, Capture scenarios.

---

## Slide 14 — Where can you plug in your own code?

Keep this short unless the room is implementers. Configuration covers most needs: mappings, Velocity, match rules, custom Velocity algorithms.

Overrides live in your own SaaS connector build. A service override keeps the pipeline and every other service intact. An operation override hands you the wired registry so you rewrite the flow, not the plumbing.

Nine operations: test connection, account list, read, create, update, enable, disable, entitlement list, schema discovery. Most projects need neither override.

Read: Connector operations.

---

## Slide 15 — Which path is yours?

Four peer starting points, then the same first-run path: create the source, test connection, discover schema, aggregate entitlements, account aggregation.

- HR and AD deduplication: umbrella, Configuring sources and scope, Matching identities.
- Username or employee-ID pool: Records, Defining attributes.
- Contractor cleanup: Orphan, Matching identities.
- Attribute consolidation only: side-car, Mapping attributes.

Getting started has the setup checklist and the Choose your path table. No separate summary slide: this is the recap.
