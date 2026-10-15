# Queries that make the graph necessary

Full executable statements and parameters live in `memory.py`.

## Current fact and source

```cypher
MATCH (u:Person {id:'user'})-[:OWNS]->(p:Project)-[:NEEDS]->(t:Task),
      (u)-[:PREFERS]->(f:Fact {active:true})-[:SUPPORTED_BY]->(s:Source),
      (t)-[:GOVERNED_BY]->(r:Procedure)
RETURN t.id, t.title, t.status, f.value, s.text, f.id, r.rule, p.name
ORDER BY f.created DESC LIMIT 1
```

The plan uses the returned preference, project and policy. A later correction changes the traversal's result. No evidence means no answer.

## Claim a task once

```cypher
MATCH (t:Task {id:'task-1', status:'open', version:$v})
MERGE (a:Agent {id:$agent})
SET t.status='claimed', t.version=t.version+1, t.owner=$agent
CREATE (a)-[:CLAIMED]->(t)
RETURN t.id, t.status, t.owner, t.version
```

The expected status/version predicate and write are in one database query. A second claim returns zero rows. Verified with eight concurrent calls, only one winner. This demo does not implement retries, lease expiry or task completion.

## Correction provenance

The remember operation marks the prior active fact inactive, creates the new fact and source, links the session episode, and connects the new fact to the prior fact with `SUPERSEDES`. Values and source notes are parameters, never string-concatenated Cypher. Concurrent preference correction conflicts are outside this demo's scope; only handoff claims are concurrency-tested.

## Isolation and removal test

Each tenant selects a distinct graph key derived from its tenant ID. The demo header chooses from two fixed fictional tenants and is not authentication. Stop FalkorDB or point the app to an unused port: `/api/plan` returns 503 and produces no answer. No graph data or query result is persisted in an alternative database.
