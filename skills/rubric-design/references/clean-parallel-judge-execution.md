# Clean Parallel Judge Execution

## When this applies

Use this reference when a rubric will be applied by an LLM judge, especially for multi-dimension, long, high-stakes, or repeated evaluations.

## Problem

If the judge continues the current conversation, the score can be contaminated by prior context:

- earlier user intent or corrections not present in the evaluated output
- agent memory or session history
- implementation notes or plans
- assumptions from the conversation that are not part of the evaluation packet

This makes scores less reproducible and can reward content that is not actually present in the evaluated artifact.

## Default pattern

1. Build a self-contained evaluation packet:
   - evaluation target
   - evaluated output
   - rubric document
   - allowed source/evidence bundle, if any
   - cap and penalty rules
   - JSON output schema
2. Run judging in a clean new subagent/session.
3. Tell the judge to ignore all prior conversation, memory, and unstated assumptions.
4. If the rubric has multiple dimensions, split the rubric into dimension/checklist shards.
5. Run shard judges in parallel clean subagents.
6. Have each shard judge return only its assigned shard JSON.
7. Parent agent validates all shard JSON, checks score bounds and missing/duplicate criteria, reconciles contradictions, and applies global caps centrally.

## Parent aggregation checks

- All dimensions/checklist items are present exactly once.
- Every score is within `0..max_score`.
- Evidence is quoted or summarized from the evaluation packet, not outside context.
- Local caps are applied before global caps.
- Global caps are applied once, centrally, after all shard scores are merged.
- The final result includes `judging_context` and context contamination notes.

## Same-context exception

Same-context judging is acceptable only for low-stakes quick checks or when a clean subagent is unavailable. The scorecard must label this explicitly, e.g.:

```json
{
  "judging_context": "same_context_exception",
  "context_contamination_notes": "Low-stakes quick check; no external evidence beyond the provided output was used."
}
```

## Korean-first rubric documents

For Korean user requests or Korean-first domains, human-facing rubric prose should be Korean-first. Machine identifiers such as JSON keys, file paths, commands, API names, enum values, schema fields, and proper nouns may remain in their original language.
