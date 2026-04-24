import json
import asyncio
from typing import List, Dict, Any
from loguru import logger
from .llm_client import LLMClient
from .search_tool import SearchTool
from .config import config
from .prompts import load_prompt

class ResearchAgent:
    def __init__(self, llm: LLMClient = None, search: SearchTool = None):
        self.llm = llm or LLMClient()
        self.search = search or SearchTool()
    
    async def research(self, topic: str, depth: int = 2, verify: bool = True) -> Dict[str, Any]:
        logger.info(f"Starting research: {topic}")
        queries = await self._generate_queries(topic)
        all_results = await self._gather_information(queries)
        report = await self._synthesize(topic, all_results)
        
        if depth > 1:
            follow_up_queries = await self._generate_followup(topic, report["summary"])
            if follow_up_queries:
                new_results = await self._gather_information(follow_up_queries)
                all_results.extend(new_results)
                report = await self._synthesize(topic, all_results, previous_report=report)
        
        final_report = report["final_report"]
        
        if verify:
            verification = await self._verify_claims(final_report, all_results)
            final_report += "\n\n" + verification
        
        return {
            "topic": topic,
            "report": final_report,
            "sources": list({res["url"] for res in all_results if "url" in res}),
            "summary": report["summary"]
        }
    
    async def _generate_queries(self, topic: str) -> List[str]:
        prompt_template = load_prompt("generate_queries")
        prompt = prompt_template.format(topic=topic)
        system = "You are an expert at formulating search queries. Respond with valid JSON only."
        response = await self.llm.generate(prompt, system_prompt=system)
        try:
            queries = json.loads(response.strip())
            return queries[:5] if isinstance(queries, list) else [topic]
        except:
            return [topic]
    
    async def _generate_followup(self, topic: str, summary: str) -> List[str]:
        prompt_template = load_prompt("generate_followup")
        prompt = prompt_template.format(topic=topic, summary=summary)
        system = "Respond only with a JSON array of search queries."
        response = await self.llm.generate(prompt, system_prompt=system)
        try:
            queries = json.loads(response.strip())
            return queries[:3] if isinstance(queries, list) else []
        except:
            return []
    
    async def _gather_information(self, queries: List[str]) -> List[Dict]:
        tasks = [self.search.search(q) for q in queries]
        results_per_query = await asyncio.gather(*tasks)
        all_results = [item for sublist in results_per_query for item in sublist]
        
        summarized = []
        for res in all_results:
            content = res.get("raw_content") or res.get("content")
            if content and len(content) > config.max_summary_tokens:
                summary = await self._summarize_text(content)
                res["content"] = summary
            summarized.append(res)
        return summarized
    
    async def _summarize_text(self, text: str) -> str:
        prompt_template = load_prompt("summarize")
        prompt = prompt_template.format(max_tokens=config.max_summary_tokens, text=text[:5000])
        return await self.llm.generate(prompt, system_prompt="You are a precise summarizer.")
    
    async def _synthesize(self, topic: str, search_results: List[Dict], previous_report: Dict = None) -> Dict:
        # build sources_text
        sources_text = ""
        for idx, res in enumerate(search_results[:10]):
            sources_text += f"\n[Source {idx+1}] Title: {res.get('title')}\nURL: {res.get('url')}\nContent: {res.get('content')}\n{'-'*40}\n"
        
        refinement = ""
        if previous_report:
            refinement = f"\n\nYou previously produced a draft. Refine it with the additional information below:\nPrevious draft summary: {previous_report.get('summary', '')}"
        
        prompt_template = load_prompt("synthesize")
        prompt = prompt_template.format(topic=topic, sources_text=sources_text, refinement_section=refinement)
        system = "You are an expert research synthesizer. Always attribute claims to sources."
        final_report = await self.llm.generate(prompt, system_prompt=system)
        
        # extract short summary
        summary_prompt_template = load_prompt("summary_extract")
        summary_prompt = summary_prompt_template.format(report=final_report)
        summary = await self.llm.generate(summary_prompt, system_prompt=None)
        return {"final_report": final_report, "summary": summary}

    async def _verify_claims(self, report: str, search_results: List[Dict]) -> str:
        """
        Extract claims from report (simple heuristic: sentences with [X] citations)
        and verify them against the corresponding source content.
        Returns a verification summary string.
        """
        import re
        # Find all claims that include a citation like [1], [2], etc.
        claim_pattern = re.compile(r'([^.!?]+[.!?])\s*\[(\d+)\]')
        claims = claim_pattern.findall(report)
        
        if not claims:
            return "No claim‑citation pairs found to verify."
        
        verification_lines = []
        for sentence, source_num in claims:
            source_num = int(source_num)
            if source_num <= len(search_results):
                source_content = search_results[source_num - 1].get("content", "")
                if not source_content:
                    source_content = "[No content available]"
                prompt_template = load_prompt("verify_claims")
                prompt = prompt_template.format(claim=sentence.strip(), source_content=source_content[:1500])
                system = "You return only the category and a short explanation."
                response = await self.llm.generate(prompt, system_prompt=system)
                verification_lines.append(f"Claim: {sentence[:100]}... | Source {source_num} | {response}")
            else:
                verification_lines.append(f"Claim: {sentence[:100]}... | Source {source_num} not found.")
        
        return "## Verification Report\n\n" + "\n".join(verification_lines)