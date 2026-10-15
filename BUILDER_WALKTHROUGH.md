# Builder review before entry approval

This build uses AI assistance. Do not claim independent authorship or a review you have not completed.

1. Run the demo. Ask for a plan before and after a correction. What changed, and which graph fact caused it?
2. Look at the old fact in the ledger. Explain why retaining it is different from continuing to use it.
3. Read `Memory.plan` in `memory.py`. Point out the preference, source and policy traversals.
4. Claim the task twice. Explain why the second query returns no rows.
5. Read `test_single_claim_under_concurrency`. Explain the status/version gate; it is not a blanket claim of production reliability.
6. Stop FalkorDB. Confirm the app refuses an answer rather than guessing or replaying stale memory.
7. Understand the limits: synthetic data, deterministic agents, no LLM integration, no MINI integration, no real send/spend, demo tenant selection is not auth, concurrent corrections not tested.

Before submitting, the participant should choose or improve the scenario, review the architecture and demo, and be ready to explain the code and queries. Organizers may reject an entirely AI-generated entry without meaningful participant contribution, verification and understanding.
