"""Web Research Module - Conducts real online research using Brave Search"""
import os
import requests
import anthropic
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class WebResearcher:
    """Conducts real web research and generates comprehensive reports"""

    def __init__(self):
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if self.anthropic_api_key:
            self.claude = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.claude = None
            print("⚠️  No ANTHROPIC_API_KEY found - AI analysis disabled")

    def search_web(self, query: str, count: int = 10) -> List[Dict]:
        """Search the web using Brave Search API"""

        if not self.brave_api_key:
            print("⚠️  No BRAVE_API_KEY found - using mock results")
            return self._mock_search_results(query)

        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }

            params = {
                "q": query,
                "count": count
            }

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                # Extract web results
                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "source": "brave_search"
                    })

                return results
            else:
                print(f"⚠️  Brave Search API error: {response.status_code}")
                return self._mock_search_results(query)

        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return self._mock_search_results(query)

    def _mock_search_results(self, query: str) -> List[Dict]:
        """Generate mock search results for testing"""
        return [
            {
                "title": f"Research findings on {query}",
                "url": "https://example.com/research",
                "description": f"Recent studies and developments related to {query}",
                "source": "mock"
            },
            {
                "title": f"Latest insights: {query}",
                "url": "https://example.com/insights",
                "description": f"Expert analysis and perspectives on {query}",
                "source": "mock"
            },
            {
                "title": f"Technical overview of {query}",
                "url": "https://example.com/technical",
                "description": f"In-depth technical documentation and guides for {query}",
                "source": "mock"
            }
        ]

    async def conduct_research(self, task_title: str, task_description: str, agent_type: str = "Research Agent") -> Dict:
        """
        Conduct comprehensive research on a topic

        1. Expand and refine the research request (prefilter)
        2. Search the web for relevant information
        3. Analyze findings using Claude
        4. Generate a structured research report
        """

        print(f"\n🔬 Starting research: {task_title}")
        print(f"   Agent: {agent_type}")
        print(f"   Topic: {task_description}")

        # Step 1: Expand and refine the research request
        if self.claude:
            print(f"   🎯 Expanding research scope...")
            expanded_request = await self._expand_research_request(
                task_title,
                task_description,
                agent_type
            )
            print(f"   ✅ Research scope refined")
        else:
            expanded_request = {
                "refined_title": task_title,
                "refined_description": task_description,
                "research_objectives": [task_description],
                "key_questions": [task_description],
                "search_strategy": task_description
            }

        # Step 2: Determine search queries based on expanded request
        search_queries = self._generate_search_queries(expanded_request["search_strategy"])

        # Collect research data from web
        all_results = []
        for query in search_queries:
            print(f"   🔍 Searching: {query}")
            results = self.search_web(query, count=5)
            all_results.extend(results)

        print(f"   ✅ Found {len(all_results)} sources")

        # Synthesize findings using Claude
        if self.claude and len(all_results) > 0:
            report_content = await self._synthesize_with_ai(
                expanded_request["refined_title"],
                expanded_request["refined_description"],
                all_results,
                agent_type,
                expanded_request
            )
        else:
            report_content = self._generate_basic_report(
                task_title,
                task_description,
                all_results
            )

        return {
            "status": "success",
            "task_title": task_title,
            "sources_found": len(all_results),
            "search_queries": search_queries,
            "content": report_content,
            "sources": all_results,
            "generated_at": datetime.now().isoformat(),
            "agent_type": agent_type
        }

    async def _expand_research_request(
        self,
        title: str,
        description: str,
        agent_type: str
    ) -> Dict:
        """
        Prefilter: Expand and refine research request for optimal, scientifically defensible,
        action-oriented results.

        This step ensures:
        - Research objectives are clearly defined
        - Scientific rigor in framing
        - Actionable outcomes are prioritized
        - Search strategy is optimized
        """

        expansion_prompt = f"""You are an expert research strategist helping to refine a research request. Your goal is to expand and clarify the request to ensure optimal, scientifically defensible, and action-oriented results.

**Original Request:**
Title: {title}
Description: {description}
Agent Type: {agent_type}

**Your Task:**
Analyze this research request and expand it into a well-structured research plan that will yield the best possible results.

Please provide your analysis in the following JSON format:

{{
  "refined_title": "A clear, specific title that captures the core research question",
  "refined_description": "An expanded description that clarifies scope, context, and relevance",
  "research_objectives": [
    "Primary objective 1 (what we need to discover)",
    "Secondary objective 2",
    "Additional objective 3 (if needed)"
  ],
  "key_questions": [
    "Specific question 1 that must be answered",
    "Specific question 2 that must be answered",
    "Specific question 3 (if applicable)"
  ],
  "success_criteria": [
    "Criterion 1 for evaluating quality of results",
    "Criterion 2 for scientific defensibility",
    "Criterion 3 for actionability"
  ],
  "search_strategy": "Optimized search query/keywords that will find the most relevant, recent, and authoritative sources",
  "expected_deliverables": [
    "Deliverable 1 (e.g., 'Evidence-based recommendations')",
    "Deliverable 2 (e.g., 'Comparison of approaches with pros/cons')"
  ],
  "scientific_rigor_notes": "How to ensure findings are scientifically defensible (e.g., 'Prioritize peer-reviewed sources', 'Compare multiple authoritative sources')",
  "action_orientation": "How to make results actionable (e.g., 'Include specific implementation steps', 'Provide decision framework')"
}}

**Guidelines:**
1. Make objectives SMART (Specific, Measurable, Achievable, Relevant, Time-bound where applicable)
2. Ensure questions can be answered with available web sources
3. Frame the search strategy to find authoritative, recent, and relevant sources
4. Emphasize practical applications and actionable insights
5. Consider scientific validity and evidence quality
6. Keep the scope focused but comprehensive enough to be useful

Return ONLY the JSON, no additional text."""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": expansion_prompt}]
            )

            # Parse JSON response
            import json
            response_text = message.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                # Extract JSON from markdown code block
                lines = response_text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith("```"):
                        if in_json:
                            break
                        in_json = True
                        continue
                    if in_json:
                        json_lines.append(line)
                response_text = "\n".join(json_lines)

            expanded = json.loads(response_text)

            # Log the expansion
            print(f"   📋 Refined objectives: {len(expanded.get('research_objectives', []))}")
            print(f"   ❓ Key questions: {len(expanded.get('key_questions', []))}")

            return expanded

        except Exception as e:
            print(f"⚠️  Research expansion error: {e}")
            # Fallback to basic structure
            return {
                "refined_title": title,
                "refined_description": description,
                "research_objectives": [description],
                "key_questions": [f"What are the key findings about {title}?"],
                "success_criteria": ["Find authoritative sources", "Provide actionable insights"],
                "search_strategy": description,
                "expected_deliverables": ["Research summary", "Recommendations"],
                "scientific_rigor_notes": "Use reputable sources",
                "action_orientation": "Focus on practical applications"
            }

    def _generate_search_queries(self, description: str) -> List[str]:
        """Generate relevant search queries from task description"""

        # Extract key terms and generate queries
        base_query = description[:200]  # Use first 200 chars

        queries = [
            base_query,
            f"{base_query} latest research",
            f"{base_query} technical overview",
        ]

        return queries[:3]  # Limit to 3 queries

    async def _synthesize_with_ai(
        self,
        title: str,
        description: str,
        search_results: List[Dict],
        agent_type: str,
        expanded_request: Dict = None
    ) -> str:
        """Use Claude to synthesize research findings into a comprehensive report"""

        # Format search results for Claude
        sources_text = "\n\n".join([
            f"**Source {i+1}: {r['title']}**\n"
            f"URL: {r['url']}\n"
            f"Summary: {r['description']}"
            for i, r in enumerate(search_results[:15])  # Limit to 15 sources
        ])

        # Build enhanced prompt with expanded request context
        objectives_text = ""
        if expanded_request:
            objectives_list = "\n".join([f"- {obj}" for obj in expanded_request.get("research_objectives", [])])
            questions_list = "\n".join([f"- {q}" for q in expanded_request.get("key_questions", [])])
            deliverables_list = "\n".join([f"- {d}" for d in expanded_request.get("expected_deliverables", [])])

            objectives_text = f"""
**Research Objectives:**
{objectives_list}

**Key Questions to Address:**
{questions_list}

**Expected Deliverables:**
{deliverables_list}

**Scientific Rigor Requirements:**
{expanded_request.get("scientific_rigor_notes", "Ensure findings are evidence-based")}

**Action Orientation:**
{expanded_request.get("action_orientation", "Focus on practical, actionable insights")}
"""

        prompt = f"""You are a {agent_type} conducting research on the following topic:

**Task:** {title}
**Description:** {description}
{objectives_text}

I have gathered the following information from web searches:

{sources_text}

Please synthesize these findings into a comprehensive, scientifically rigorous, action-oriented research report with the following structure:

# {title}

## Executive Summary
[2-3 paragraph overview of key findings, conclusions, and recommendations]

## Introduction
[Context, scope, and objectives of the research]

## Research Methodology
[Brief description of research approach and sources]

## Findings & Analysis
[Detailed analysis organized by themes/topics. Reference specific sources. Include evidence and data.]

## Key Insights
[Most important discoveries and conclusions supported by evidence]

## Practical Applications
[How these findings can be applied in practice]

## Recommendations
[Specific, actionable recommendations with priority levels and implementation guidance]

## Limitations & Future Research
[Acknowledge limitations and suggest areas for deeper investigation]

## References
[Numbered list of all sources cited, formatted academically]

## Appendix (if applicable)
[Additional supporting data, tables, or detailed information]

**Important Guidelines:**
- Use evidence-based reasoning throughout
- Cite specific sources when making claims
- Provide actionable, practical recommendations
- Maintain scientific rigor and objectivity
- Structure content logically with clear headings
- Use professional, academic tone
- Include specific data points and examples from sources
- Ensure all claims are defensible and well-supported"""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            print(f"⚠️  AI synthesis error: {e}")
            return self._generate_basic_report(title, description, search_results)

    def _generate_basic_report(
        self,
        title: str,
        description: str,
        search_results: List[Dict]
    ) -> str:
        """Generate a basic report without AI synthesis"""

        sources_list = "\n".join([
            f"{i+1}. **{r['title']}**\n"
            f"   - URL: {r['url']}\n"
            f"   - {r['description']}\n"
            for i, r in enumerate(search_results)
        ])

        return f"""# Research Report: {title}

## Task Description
{description}

## Research Findings

Conducted web research and found {len(search_results)} relevant sources.

## Sources

{sources_list}

## Summary

Research completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}.
Found {len(search_results)} sources relevant to the topic.

## Next Steps

- Review the sources above for detailed information
- Conduct deeper analysis on specific findings
- Implement recommendations based on research

---
*Report generated by Agent Management Platform Research System*
"""

# Global instance
web_researcher = WebResearcher()
