from __future__ import annotations
from collections.abc import Iterable
from typing import Any
from ..benchmarking import BenchmarkResult
from .benchmark_profile import BenchmarkProfile
from .profile_link import ProfileLink, ProfileLinkType
from .profile_source import ProfileSource

class BenchmarkProfileBuilder:
    DEFAULT_METRIC_FIELDS = ("patients_per_day", "annual_patient_volume", "bed_count", "pet_ct_count", "spect_count", "cyclotron_count", "staff_count", "transport_distance_m", "capital_cost", "operating_cost")
    def build(self, result: BenchmarkResult) -> BenchmarkProfile:
        p=result.project; metadata=dict(p.metadata); obs=self._observations(result)
        metrics=self._metrics(obs, metadata)
        scores={s.section:s.score for s in result.similarity.section_scores}
        highlights, differences=self._comparison_points(result)
        location=', '.join(v for v in (p.region,p.country) if v)
        parts=[v for v in (p.facility_type,p.project_type,location) if v]
        return BenchmarkProfile(
            benchmark_id=p.id, name=p.name, rank=result.rank, similarity_score=result.score,
            similarity_percentage=result.percentage, country=p.country, region=p.region,
            facility_type=p.facility_type, project_type=p.project_type, image_url=p.image_url,
            display_url=result.display_url, summary=' · '.join(parts),
            similarity_explanation=result.similarity.explanation, section_scores=scores,
            highlights=highlights, differences=differences, metrics=metrics,
            links=self._links(result), sources=self._sources(result), metadata=metadata)
    def build_many(self, results: Iterable[BenchmarkResult]):
        return tuple(self.build(r) for r in results)
    @staticmethod
    def _observations(result):
        out={}
        for e in result.project.signature.evidence.snapshot():
            s=e.metadata.get('signature_section'); f=e.metadata.get('field_name')
            if isinstance(s,str) and isinstance(f,str): out.setdefault(s,{})[f]=e.value
        return out
    def _metrics(self, observations, metadata):
        out={}
        for values in observations.values():
            for k,v in values.items():
                if k in self.DEFAULT_METRIC_FIELDS: out[k]=v
        extra=metadata.get('profile_metrics')
        if isinstance(extra,dict): out.update(extra)
        return out
    @staticmethod
    def _links(result):
        p=result.project; links=[]
        for label,url,kind in (("View benchmark profile",p.profile_url,ProfileLinkType.PROFILE),("Official/source website",p.source_url,ProfileLinkType.SOURCE),("View image",p.image_url,ProfileLinkType.IMAGE)):
            if url: links.append(ProfileLink(label,url,kind))
        extra=p.metadata.get('links')
        if isinstance(extra,list):
            for item in extra:
                if not isinstance(item,dict): continue
                label,url=item.get('label'),item.get('url')
                if not isinstance(label,str) or not isinstance(url,str): continue
                try: kind=ProfileLinkType(item.get('type','other'))
                except ValueError: kind=ProfileLinkType.OTHER
                links.append(ProfileLink(label,url,kind))
        seen=set(); unique=[]
        for link in links:
            if link.url not in seen: seen.add(link.url); unique.append(link)
        return tuple(unique)
    @staticmethod
    def _sources(result):
        p=result.project; sources=[]
        if p.source_title or p.source_reference or p.source_url:
            sources.append(ProfileSource(p.source_title or p.name,p.source_reference,p.source_url,str(p.metadata.get('source_date')) if p.metadata.get('source_date') else None,p.metadata.get('publisher'),p.is_verified))
        extra=p.metadata.get('sources')
        if isinstance(extra,list):
            for item in extra:
                if isinstance(item,dict) and isinstance(item.get('title'),str):
                    sources.append(ProfileSource(item['title'],item.get('reference'),item.get('url'),item.get('date'),item.get('publisher'),bool(item.get('verified',False))))
        return tuple(sources)
    @staticmethod
    def _comparison_points(result):
        hi=[]; diff=[]
        for s in result.similarity.section_scores:
            if s.compared_fields==0: continue
            label=s.section.replace('_',' ').title()
            if s.score>=0.8: hi.append(f"{label} is strongly aligned ({s.score*100:.1f}%).")
            elif s.score<0.5: diff.append(f"{label} differs materially ({s.score*100:.1f}%).")
        return tuple(hi),tuple(diff)
