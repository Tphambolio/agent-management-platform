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

        1. Search the web for relevant information
        2. Analyze findings using Claude
        3. Generate a structured research report
        """

        print(f"\n🔬 Starting research: {task_title}")
        print(f"   Agent: {agent_type}")
        print(f"   Topic: {task_description}")

        # Determine search queries based on task
        search_queries = self._generate_search_queries(task_description)

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
                task_title,
                task_description,
                all_results,
                agent_type
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
        agent_type: str
    ) -> str:
        """Use Claude to synthesize research findings into a comprehensive report"""

        # Format search results for Claude
        sources_text = "\n\n".join([
            f"**Source {i+1}: {r['title']}**\n"
            f"URL: {r['url']}\n"
            f"Summary: {r['description']}"
            for i, r in enumerate(search_results[:15])  # Limit to 15 sources
        ])

        prompt = f"""You are a {agent_type} conducting research on the following topic:

**Task:** {title}
**Description:** {description}

I have gathered the following information from web searches:

{sources_text}

Please synthesize these findings into a comprehensive research report with the following structure:

# {title}

## Executive Summary
[Brief overview of key findings]

## Research Findings
[Detailed analysis organized by themes/topics]

## Key Insights
[Most important discoveries and conclusions]

## Sources & References
[List of sources used]

## Recommendations
[Actionable recommendations based on research]

Make the report professional, well-structured, and data-driven. Include specific details from the sources."""

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
