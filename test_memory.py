from concurrent.futures import ThreadPoolExecutor
import os
import uuid
import pytest
from memory import Memory

@pytest.fixture
def m():
    obj=Memory('test-'+str(uuid.uuid4()))
    obj.reset()
    yield obj
    obj.query('MATCH (n) DETACH DELETE n')

def test_current_fact_and_history(m):
    assert m.plan()['preference']=='bank'
    m.remember('mobile wallet','Synthetic session 2 correction')
    assert m.plan()['preference']=='mobile wallet'
    facts=m.snapshot()['facts']
    assert len(facts)==2
    assert sum(bool(f[2]) for f in facts)==1
    assert m.query('MATCH (:Fact)-[:SUPERSEDES]->(:Fact) RETURN count(*)')[0][0]==1

def test_reconnect_persistence(m):
    m.remember('mobile wallet','Synthetic correction')
    restored=Memory('unused')
    restored.graph=restored.db.select_graph(m.name)
    assert restored.plan()['preference']=='mobile wallet'

def test_tenant_isolation(m):
    other=Memory('other-'+str(uuid.uuid4()))
    assert other.snapshot()['facts']==[]
    with pytest.raises(ValueError):other.plan()

def test_single_claim_under_concurrency(m):
    with ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda n:m.handoff('worker'+str(n)),range(8)))
    assert sum(r['claimed'] for r in results)==1

def test_no_evidence_no_answer(m):
    m.query('MATCH (f:Fact) SET f.active=false')
    with pytest.raises(ValueError):m.plan()

def test_injection_stored_as_data(m):
    source="Sam's note: '}) MATCH (n) DETACH DELETE n //"
    m.remember('mobile wallet',source)
    assert m.plan()['source']==source
    assert m.snapshot()['nodes']>0

def test_invalid_input(m):
    with pytest.raises(ValueError):m.remember('crypto','test')
    with pytest.raises(ValueError):m.handoff("x' DELETE n")

def test_api_failure_no_fake_answer(monkeypatch):
    from app import app
    monkeypatch.setenv('FALKOR_PORT','6398')
    r=app.test_client().post('/api/plan',json={})
    assert r.status_code==503
    assert 'No answer or action' in r.json['error']
