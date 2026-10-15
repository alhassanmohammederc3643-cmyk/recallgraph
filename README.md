# RecallGraph

**A new session. The right memory.**

A standalone, synthetic agent-memory and coordination demo for Graph Hacks, track **Agent Memory and Coordination**. FalkorDB is the primary store: the planning agent traverses current facts and their sources; the delivery agent claims a shared task through a version-checked graph write. No graph means no answer. This is inspired by the personal-assistant problem, but does not contain MINI source code, private conversations or real personal data.

## Run locally

Requirements: Docker Engine with Compose v2. No paid service, LLM key or account needed.

```sh
docker compose up --build
# Open http://localhost:8080
```

Click **Start synthetic session**, then **Ask planning agent**. Save the correction to mobile wallet and ask again. Claim the handoff twice: only the first claim succeeds. Refresh the page or restart the web container: graph memory survives. Use `docker compose down` to stop; `docker compose down -v` deletes demo data.

The app binds only to localhost. This is a shared sandbox, not a production service. Do not expose it to the internet without authentication, authorization, rate limits and per-user identity management. The demo's tenant header is NOT authentication.

For Python-only development, run a FalkorDB server, install `requirements.txt`, then set `FALKOR_HOST`, `FALKOR_PORT`, optionally `FALKOR_PASSWORD`, and run `python app.py`. Run tests with `pytest -q` against a running local FalkorDB. Tests use temporary graph names and delete their nodes afterward.

## What is working

- Episodic memory: session episodes record facts and their sources.
- Semantic memory: current payment preference drives the next plan.
- Procedural memory: a graph policy limits the action to a draft.
- Correction: `SUPERSEDES` links keep older facts, without using them for the current answer.
- Coordination: one task claim succeeds, including under concurrent claims.
- Tenant separation: distinct graph names derived from tenant IDs.
- Traceability: answers cite the source note and relationship path.
- Failure handling: no cached fallback if FalkorDB is unavailable.

These are deterministic, tool-using demo agents, not an LLM chatbot. There are no external actions, transfers or actual bookings. No production scale, latency or revenue claims.

## Graph data model

```
(Person)-[:OWNS]->(Project)-[:NEEDS]->(Task)-[:GOVERNED_BY]->(Procedure)
(Person)-[:PREFERS]->(Fact)-[:SUPPORTED_BY]->(Source)
(Episode)-[:RECORDED]->(Fact)-[:SUPERSEDES]->(older Fact)
(Agent)-[:MADE]->(Decision)-[:BASED_ON]->(Fact)
(Decision)-[:FOR]->(Task)<-[:CLAIMED]-(Agent)
```

`Fact.active` selects current knowledge. A superseded fact remains queryable for an audit. A task has `status` and `version`; a claim updates both in a single database write query. See `memory.py` for the complete executable Cypher, `QUERIES.md` for key queries and `BUILDER_WALKTHROUGH.md` for the decisions to review.

## Verification

Verified October 14, 2026, after the event opened (00:01 IST October 15 = 18:31 GMT October 14), using FalkorDB module 4.18.11 on Redis 8.0.2 and Python 3.10. Eight tests passed, including concurrent claims. The Python core and browser UI are tested. Docker Compose is provided for reproducibility; Docker is not installed in the build environment, so the Compose path has not been executed there. Verify it on a Docker-enabled machine before submission.

## AI assistance and participant review

Implementation and test preparation were produced with AI coding assistance. Participant review and technical explanation are still required before a submission; this README does not claim that review has already happened. The builder should understand the data model, current-fact traversal, parameterized queries, status/version claim and failure handling. See the walkthrough. This is not yet a registered or submitted entry.

## Event sources

- https://www.wemakedevs.org/hackathons/falkordb
- https://www.wemakedevs.org/hackathons/falkordb/rules
- https://www.wemakedevs.org/hackathons/falkordb/resources

No numerical judging rubric was found on these official pages. The relevant stated focus is persistent memory, shared state/handoffs and separate memory per user or tenant.

## Free hosted judge sandbox

`Dockerfile.render` runs the web app and a real FalkorDB server in one container. Use it only for the synthetic judge demo. On free hosting with ephemeral storage, memory survives browser refresh and sessions while the container is running, but resets on a full service restart/redeploy. The local Compose route has a named data volume for longer-lived storage. No durable hosted persistence, production reliability or private user isolation is claimed.
