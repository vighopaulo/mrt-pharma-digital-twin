from pathlib import Path
from uuid import uuid4
import json, pytest
from mrt.intelligence.benchmarking import BenchmarkEngine, BenchmarkLibrary, BenchmarkProject
from mrt.intelligence.discovery import DiscoveryContext, SignatureDiscoveryEngine
from mrt.intelligence.profiles import BenchmarkProfileBuilder
from mrt.intelligence.profiles.profile_link import ProfileLink, ProfileLinkType
from mrt.intelligence.profiles.serialization import BenchmarkProfileSerializer

def signature(data):
    return SignatureDiscoveryEngine().discover(DiscoveryContext(project_id=uuid4(), data=data)).signature

def result_for(metadata=None):
    project=BenchmarkProject(name='Example Cancer Centre',signature=signature({'spatial':{'transport_distance_m':250},'equipment':{'pet_ct_count':3,'cyclotron_count':1},'metrics':{'patients_per_day':45}}),country='Canada',region='Toronto',facility_type='Cancer hospital',project_type='Existing facility',source_reference='report-2026',source_title='Hospital Annual Report',source_url='https://example.org/report',image_url='https://example.org/hospital.jpg',profile_url='https://app.example.org/benchmarks/example',is_verified=True,metadata=metadata or {})
    reference=signature({'spatial':{'transport_distance_m':240},'equipment':{'pet_ct_count':3,'cyclotron_count':1},'metrics':{'patients_per_day':44}})
    return BenchmarkEngine(BenchmarkLibrary([project])).retrieve(reference)[0]

def test_profile_builder_creates_display_ready_profile():
    p=BenchmarkProfileBuilder().build(result_for())
    assert p.name=='Example Cancer Centre' and p.rank==1 and p.country=='Canada'
    assert p.image_url.endswith('hospital.jpg') and p.display_url.endswith('/example')
    assert p.similarity_percentage>90 and p.metrics['pet_ct_count']==3 and p.sources[0].verified

def test_profile_links_are_deduplicated():
    p=BenchmarkProfileBuilder().build(result_for({'links':[{'label':'Duplicate','url':'https://example.org/report','type':'source'},{'label':'Map','url':'https://maps.example.org/hospital','type':'map'}]}))
    urls=[x.url for x in p.links]
    assert urls.count('https://example.org/report')==1 and 'https://maps.example.org/hospital' in urls

def test_additional_metrics_and_sources():
    p=BenchmarkProfileBuilder().build(result_for({'profile_metrics':{'bed_count':450},'sources':[{'title':'Case Study','url':'https://example.org/case','verified':True}]}))
    assert p.metrics['bed_count']==450 and len(p.sources)==2

def test_build_many_and_json_payload(tmp_path: Path):
    p=BenchmarkProfileBuilder().build_many([result_for()])[0]
    payload=p.to_dict(); assert payload['links'][0]['link_type']=='profile'; json.dumps(payload)
    path=tmp_path/'profiles.json'; BenchmarkProfileSerializer.dump([p],path)
    assert json.loads(path.read_text())['profiles'][0]['name']=='Example Cancer Centre'

def test_invalid_link_rejected():
    with pytest.raises(ValueError): ProfileLink('Invalid','ftp://example.org/file',ProfileLinkType.OTHER)
