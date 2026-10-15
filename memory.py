"""RecallGraph: graph-backed memory and deterministic tool-using demo agents."""
import hashlib
import os
import re
import time
import uuid
from falkordb import FalkorDB

class Memory:
    def __init__(self, tenant='demo', port=None):
        # Separate graphs, not a filter that can accidentally be omitted.
        self.name = 'recall_' + hashlib.sha256(tenant.encode()).hexdigest()[:24]
        self.db = FalkorDB(host=os.getenv('FALKOR_HOST', 'localhost'),
                          port=port or int(os.getenv('FALKOR_PORT', '6379')),
                          password=os.getenv('FALKOR_PASSWORD') or None)
        self.graph = self.db.select_graph(self.name)

    def query(self, cypher, params=None):
        result = self.graph.query(cypher, params or {})
        return result.result_set

    def reset(self):
        self.query('MATCH (n) DETACH DELETE n')
        self.query('''CREATE (u:Person {id:'user', name:'Sam (fictional)'}),
          (p:Project {id:'demo', name:'Workshop booking'}),
          (t:Task {id:'task-1', title:'Prepare payment instructions', status:'open', version:0}),
          (u)-[:OWNS]->(p), (p)-[:NEEDS]->(t),
          (a:Agent {id:'planner', name:'Planning agent'}),
          (b:Agent {id:'worker', name:'Delivery agent'}),
          (r:Procedure {id:'payment', rule:'Prepare a draft only; do not send or spend.'}),
          (t)-[:GOVERNED_BY]->(r)''')
        self.remember('bank', 'Session 1: Sam prefers a bank transfer.', 'session-1')
        return self.snapshot()

    def remember(self, value, source, session='session-2'):
        if value not in ('bank', 'mobile wallet'):
            raise ValueError('Choose bank or mobile wallet for this synthetic demo.')
        if not source or len(source)>500:
            raise ValueError('Source must be 1-500 characters.')
        fid, sid = str(uuid.uuid4()), str(uuid.uuid4())
        # Old memory is retained with SUPERSEDES provenance, not silently erased.
        self.query('''MATCH (u:Person {id:'user'})
          OPTIONAL MATCH (u)-[:PREFERS]->(old:Fact {active:true})
          SET old.active=false
          CREATE (f:Fact {id:$fid, value:$value, active:true, created:$ts}),
          (s:Source {id:$sid, text:$source}),
          (e:Episode {id:$session, summary:$source}),
          (u)-[:PREFERS]->(f), (f)-[:SUPPORTED_BY]->(s),
          (e)-[:RECORDED]->(f)
          FOREACH (x IN CASE WHEN old IS NULL THEN [] ELSE [old] END |
             CREATE (f)-[:SUPERSEDES]->(x))''',
          dict(fid=fid, sid=sid, value=value, source=source, ts=time.time(), session=session))
        return fid

    def plan(self):
        # A three-edge traversal, plus policy. There is no in-memory answer fallback.
        rows = self.query('''MATCH (u:Person {id:'user'})-[:OWNS]->(p:Project)-[:NEEDS]->(t:Task),
          (u)-[:PREFERS]->(f:Fact {active:true})-[:SUPPORTED_BY]->(s:Source),
          (t)-[:GOVERNED_BY]->(r:Procedure)
          RETURN t.id, t.title, t.status, f.value, s.text, f.id, r.rule, p.name
          ORDER BY f.created DESC LIMIT 1''')
        if not rows:
            raise ValueError('No current memory with a source. Initialize the synthetic demo.')
        task, title, status, value, source, fact, rule, project = rows[0]
        action = f'Draft {value} instructions for {project}. No message or payment is sent.'
        self.query('''MATCH (t:Task {id:$task}), (f:Fact {id:$fact}), (a:Agent {id:'planner'})
          CREATE (d:Decision {id:$id, action:$action, created:$ts}),
          (a)-[:MADE]->(d), (d)-[:BASED_ON]->(f), (d)-[:FOR]->(t)''',
          dict(task=task, fact=fact, id=str(uuid.uuid4()), action=action, ts=time.time()))
        return dict(action=action, task=task, status=status, preference=value, source=source,
                    path=['Person', 'PREFERS', 'Fact', 'SUPPORTED_BY', 'Source'],
                    rule=rule, cypher='MATCH (u)-[:PREFERS]->(f:Fact {active:true})-[:SUPPORTED_BY]->(s)')

    def handoff(self, agent='worker', expected_version=0):
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}',agent):
            raise ValueError('Invalid agent ID')
        # Status/version predicates are checked in the same write query as the claim.
        rows = self.query('''MATCH (t:Task {id:'task-1', status:'open', version:$v})
          MERGE (a:Agent {id:$agent})
          SET t.status='claimed', t.version=t.version+1, t.owner=$agent
          CREATE (a)-[:CLAIMED]->(t)
          RETURN t.id, t.status, t.owner, t.version''',dict(agent=agent, v=expected_version))
        return dict(claimed=bool(rows), task=rows[0] if rows else None)

    def snapshot(self):
        facts = self.query('''MATCH (f:Fact)-[:SUPPORTED_BY]->(s:Source)
          RETURN f.id, f.value, f.active, s.text ORDER BY f.created''')
        tasks = self.query('MATCH (t:Task) RETURN t.id, t.title, t.status, t.version, t.owner')
        counts = self.query('MATCH (n) RETURN count(n)')[0][0]
        edges = self.query('MATCH (a)-[r]->(b) RETURN labels(a), type(r), labels(b)')
        return dict(graph=self.name, facts=facts, tasks=tasks, nodes=counts, edges=edges)
