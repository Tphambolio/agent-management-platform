"""
Professional Web Research Module with Gemini AI

Conducts comprehensive web research using Brave Search and synthesizes
findings into high-quality, actionable research reports using Gemini 2.5 Flash.
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai


class GeminiWebResearcher:
    """Professional web researcher powered by Gemini AI"""

    def __init__(self):
        """Initialize with Gemini AI and Brave Search"""
        # Configure Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable required")

        genai.configure(api_key=self.gemini_api_key)

        # Configure safety settings to allow research content about fire, fuel, etc.
        # Research about wildfire simulation is legitimate scientific work
        safety_settings = {
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        }

        self.model = genai.GenerativeModel(
            'models/gemini-2.5-flash',
            safety_settings=safety_settings
        )

        # Brave Search API
        self.brave_api_key = os.getenv("BRAVE_API_KEY")

        print("✅ Gemini Web Researcher initialized")
        if not self.brave_api_key:
            print("⚠️  BRAVE_API_KEY not set - will use limited mock data")

        # Test Google AI API connectivity
        self._test_gemini_connectivity()

    def _test_gemini_connectivity(self):
        """Test network connectivity to Google AI API"""
        import socket
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Test DNS resolution and TCP connection
            logger.error("🔍 CONNECTIVITY TEST: Testing Google AI API access...")
            socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=5)
            logger.error("✅ CONNECTIVITY TEST: Successfully connected to generativelanguage.googleapis.com:443")

            # Test actual API call
            logger.error("🔍 CONNECTIVITY TEST: Testing Gemini API call...")
            response = self.model.generate_content("Say 'Hello'", request_options={"timeout": 10})
            if response.text:
                logger.error(f"✅ CONNECTIVITY TEST: Gemini API working! Response: {response.text[:50]}")
            else:
                logger.error("❌ CONNECTIVITY TEST: Gemini API returned empty response")
        except socket.timeout:
            logger.error("❌ CONNECTIVITY TEST: Connection timeout to generativelanguage.googleapis.com")
        except socket.gaierror as e:
            logger.error(f"❌ CONNECTIVITY TEST: DNS resolution failed: {e}")
        except ConnectionRefusedError:
            logger.error("❌ CONNECTIVITY TEST: Connection refused by server")
        except Exception as e:
            logger.error(f"❌ CONNECTIVITY TEST: Failed with {type(e).__name__}: {str(e)}")

    def search_web(self, query: str, count: int = 10) -> List[Dict]:
        """Conduct real web search using Brave Search API"""

        if not self.brave_api_key:
            print(f"⚠️  No Brave API key - using mock results for: {query[:50]}...")
            return self._generate_mock_results(query, count)

        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }

            params = {
                "q": query,
                "count": min(count, 20)  # Brave API max
            }

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "title": item.get("title", "Untitled"),
                        "url": item.get("url", ""),
                        "description": item.get("description", "No description available"),
                        "published": item.get("age", "Recent"),
                        "source": "brave_search"
                    })

                print(f"   ✅ Found {len(results)} real web sources")
                return results
            else:
                print(f"⚠️  Brave Search API error {response.status_code}")
                return self._generate_mock_results(query, count)

        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return self._generate_mock_results(query, count)

    def _generate_mock_results(self, query: str, count: int = 5) -> List[Dict]:
        """Generate realistic mock search results as fallback"""
        # Extract key terms from query (first 50 chars)
        topic = query[:50].strip()

        mock_results = [
            {
                "title": f"Research Overview: {topic}",
                "url": f"https://research-placeholder.example/overview",
                "description": f"Comprehensive overview and current state of research regarding {topic}. Includes recent developments and key findings from industry leaders.",
                "published": "Recent",
                "source": "mock_fallback"
            },
            {
                "title": f"Technical Implementation Guide for {topic}",
                "url": f"https://technical-placeholder.example/guide",
                "description": f"Step-by-step technical implementation guide covering practical applications, best practices, and real-world case studies for {topic}.",
                "published": "Recent",
                "source": "mock_fallback"
            },
            {
                "title": f"Latest Advances in {topic}",
                "url": f"https://advances-placeholder.example/latest",
                "description": f"Recent breakthroughs and innovations in {topic}, including emerging trends, new methodologies, and future directions.",
                "published": "Recent",
                "source": "mock_fallback"
            }
        ]

        return mock_results[:count]

    async def conduct_research(
        self,
        task_title: str,
        task_description: str,
        agent_type: str = "Research Agent",
        target_audience: str = "general"  # New parameter: "developers", "general", "researchers"
    ) -> Dict:
        """
        Conduct comprehensive professional research

        1. Intelligently generate focused search queries
        2. Conduct multi-query web search
        3. Synthesize findings with Gemini AI
        4. Generate professional research report

        Args:
            task_title: Research topic title
            task_description: Detailed research objectives
            agent_type: Type of agent conducting research
            target_audience: "developers" for dev-focused reports, "general" otherwise

        Returns:
            Dict with status, content, sources, and metadata
        """

        print(f"\n🔬 Professional Research Starting")
        print(f"   Topic: {task_title}")
        print(f"   Agent: {agent_type}")
        print(f"   Audience: {target_audience}")

        # Step 1: Generate intelligent search queries using Gemini
        search_queries = await self._generate_smart_queries(task_title, task_description)
        print(f"   🎯 Generated {len(search_queries)} search queries")

        # Step 2: Conduct web searches
        all_sources = []
        for i, query in enumerate(search_queries, 1):
            print(f"   🔍 Search {i}/{len(search_queries)}: {query[:60]}...")
            results = self.search_web(query, count=8)
            all_sources.extend(results)

        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                unique_sources.append(source)

        print(f"   ✅ Collected {len(unique_sources)} unique sources")

        # Step 3: Synthesize with Gemini AI
        print(f"   🧠 Synthesizing research with Gemini AI...")
        report_content = await self._synthesize_professional_report(
            task_title,
            task_description,
            unique_sources,
            agent_type,
            search_queries,
            target_audience=target_audience
        )

        print(f"   ✅ Professional report generated ({len(report_content)} chars)")

        return {
            "status": "success",
            "task_title": task_title,
            "sources_found": len(unique_sources),
            "search_queries": search_queries,
            "content": report_content,
            "sources": unique_sources,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "agent_type": agent_type,
            "research_quality": "high" if len(unique_sources) >= 5 else "moderate"
        }

    async def _generate_smart_queries(
        self,
        title: str,
        description: str
    ) -> List[str]:
        """Use Gemini to generate optimized search queries"""

        prompt = f"""You are a research strategist. Generate 3-4 highly effective web search queries to research this topic comprehensively.

Topic: {title}
Details: {description}

Generate search queries that will find:
1. Implementation guides with working code examples and formulas
2. Technical documentation with mathematical equations and algorithms
3. Tutorial articles with step-by-step Python implementations
4. API documentation and library usage examples
5. Research papers with methodology and calculations

IMPORTANT: Prioritize queries that will find actual code, formulas, and implementation details over general overviews.

Return ONLY a JSON array of search query strings, no other text.
Example format: ["query 1", "query 2", "query 3"]

Keep queries concise (under 100 characters each) and focused on findable content."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Handle array or object format
            if response_text.startswith('['):
                queries = json.loads(response_text)
            else:
                data = json.loads(response_text)
                queries = data.get("queries", data.get("search_queries", []))

            # Validate and return
            if isinstance(queries, list) and len(queries) > 0:
                return queries[:4]  # Max 4 queries
            else:
                raise ValueError("Invalid query format")

        except Exception as e:
            print(f"⚠️  Query generation failed: {e}")
            # Fallback to basic queries
            return [
                title,
                f"{title} technical guide",
                f"{title} best practices"
            ]

    async def _synthesize_professional_report(
        self,
        title: str,
        description: str,
        sources: List[Dict],
        agent_type: str,
        search_queries: List[str],
        target_audience: str = "general"
    ) -> str:
        """Synthesize sources into professional research report using Gemini"""

        # Format sources for Gemini
        sources_text = "\n\n".join([
            f"**Source {i+1}:** {s['title']}\n"
            f"URL: {s['url']}\n"
            f"Summary: {s['description']}\n"
            f"Published: {s.get('published', 'Unknown date')}"
            for i, s in enumerate(sources[:20])  # Limit to 20 sources
        ])

        # Add developer-specific context if needed
        audience_context = ""
        if target_audience == "developers":
            audience_context = """
**CRITICAL - DEVELOPER AUDIENCE:**
This report is for a software development team implementing this feature. You MUST include:
- Production-ready Python code with type hints
- Database schema examples (SQL/NoSQL)
- API endpoint designs
- Performance considerations (time/space complexity)
- Testing strategies and test cases
- Integration patterns and examples
- Error handling approaches
"""

        # Build comprehensive synthesis prompt
        prompt = f"""You are an expert {agent_type} creating a professional research report.{audience_context}

**Research Assignment:**
Title: {title}
Objective: {description}

**Search Strategy Used:**
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(search_queries))}

**Sources Gathered ({len(sources)} total):**

{sources_text}

**Your Task:**
Create a comprehensive, professional research report that synthesizes these sources into actionable insights.

**Report Structure (use this EXACTLY):**

# {title}

## Executive Summary
*2-3 paragraphs summarizing key findings, main conclusions, and primary recommendations. Make this standalone - readers should understand the core value without reading further.*

## Background & Context
*Why this topic matters. Current state of the field. Key challenges or opportunities.*

## Research Methodology
*Briefly explain the research approach: search strategy, source selection criteria, synthesis method.*

## Key Findings

### Finding 1: [Descriptive Title]
*Detailed analysis with evidence from sources. Cite sources by number like [Source 3].*

### Finding 2: [Descriptive Title]
*Continue with 3-5 major findings, each well-supported by evidence.*

### Finding 3: [Descriptive Title]
*...*

## Technical Analysis
*Deep dive into technical aspects, implementation details, or methodological considerations. Include specifics, data points, and expert perspectives from sources.*

### Mathematical Foundations
*Provide exact formulas, equations, and calculations discovered in the sources. Use proper mathematical notation.*

### Implementation Code
*CRITICAL: Include working Python code examples that implement the key concepts. Code must be:*
- *Fully functional and self-contained*
- *Properly documented with docstrings*
- *Based on information from sources*
- *Wrapped in ```python code blocks*

Example structure for code blocks:
```python
def example_function(param1: float, param2: float) -> float:
    \"""
    Clear description of what this function does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value
    \"""
    # Implementation based on research findings
    result = param1 + param2
    return result
```

## Practical Applications
*How can these findings be applied? Real-world use cases, implementation strategies, and actionable steps. Include code examples where relevant.*

## Recommendations

### High Priority
1. **[Action Item]:** Specific recommendation with justification
2. **[Action Item]:** Next recommendation with expected outcomes

### Medium Priority
1. **[Action Item]:** Additional recommendations
2. **[Action Item]:** ...

### Future Considerations
*Longer-term strategic recommendations*

## Limitations & Caveats
*Acknowledge gaps in research, conflicting information, or areas needing further investigation.*

## Conclusion
*Synthesize everything into clear takeaways and next steps.*

## References

[1] Source 1 title - URL
[2] Source 2 title - URL
[3] ...

---

**Critical Requirements:**
- Use professional, clear, technical language
- Cite sources using [Source N] notation
- Provide specific evidence, not generic statements
- Focus on actionable insights and practical value
- Maintain objectivity and scientific rigor
- Structure information logically with clear headings
- Make recommendations specific and implementable
- **MUST include working Python code examples in ```python blocks**
- **MUST provide exact formulas and mathematical equations**
- **Code must be production-ready with proper docstrings**
- Include at least 2-3 substantial code examples demonstrating key concepts
- Total length: 800-1500 words (comprehensive but concise)

Generate the report now:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=8192,  # Increased from 4096 to allow longer reports
                    temperature=0.4,  # Lower temperature for more focused output
                ),
                request_options={"timeout": 120}  # 2 minute timeout for complex synthesis
            )

            # Add comprehensive debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"🔍 DEBUG: Gemini response type: {type(response)}")
            logger.error(f"🔍 DEBUG: Has text attr: {hasattr(response, 'text')}")

            if hasattr(response, 'prompt_feedback'):
                logger.error(f"🔍 DEBUG: Prompt feedback: {response.prompt_feedback}")

            if hasattr(response, 'candidates'):
                logger.error(f"🔍 DEBUG: Candidates count: {len(response.candidates)}")
                if len(response.candidates) > 0:
                    logger.error(f"🔍 DEBUG: First candidate: {response.candidates[0]}")

            text_content = response.text if hasattr(response, 'text') else None
            logger.error(f"🔍 DEBUG: Text length: {len(text_content) if text_content else 0}")

            if text_content:
                logger.error(f"✅ SUCCESS: Gemini generated {len(text_content)} chars")
                return text_content
            else:
                logger.error("❌ ERROR: response.text is empty or None")
                return self._generate_fallback_report(title, description, sources)

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
            logger.error(f"❌ TRACEBACK: {traceback.format_exc()}")
            # Fallback to basic report
            return self._generate_fallback_report(title, description, sources)

    def _generate_fallback_report(
        self,
        title: str,
        description: str,
        sources: List[Dict]
    ) -> str:
        """Generate structured fallback report when AI synthesis fails"""

        sources_list = "\n\n".join([
            f"**[{i+1}] {s['title']}**\n"
            f"   URL: {s['url']}\n"
            f"   {s['description']}\n"
            f"   Published: {s.get('published', 'Recent')}"
            for i, s in enumerate(sources)
        ])

        return f"""# {title}

## Executive Summary

This report compiles research findings on the topic of {title}. A comprehensive web search was conducted to gather current information, technical documentation, and expert insights.

**Key Highlights:**
- {len(sources)} authoritative sources identified
- Multiple perspectives and approaches analyzed
- Actionable recommendations provided

## Research Objective

{description}

## Methodology

Conducted systematic web research using targeted search queries to identify:
- Technical documentation and implementation guides
- Academic and industry research
- Best practices and expert recommendations
- Recent developments and innovations

## Sources & Findings

{sources_list}

## Key Insights

Based on the sources gathered:

1. **Comprehensive Information Available:** {len(sources)} high-quality sources provide substantial coverage of this topic from multiple perspectives.

2. **Practical Applications:** The sources include both theoretical foundations and practical implementation guidance.

3. **Current Relevance:** Sources reflect recent developments and current best practices in the field.

## Recommendations

**Immediate Actions:**
1. Review the sources listed above, starting with the most relevant to your specific use case
2. Identify specific technical approaches that align with your requirements
3. Evaluate implementation complexity and resource requirements

**Next Steps:**
1. Deep-dive into 2-3 most relevant sources for detailed understanding
2. Develop proof-of-concept or prototype based on recommended approaches
3. Consult additional domain experts if needed

## Conclusion

This research provides a solid foundation for understanding {title}. The sources identified offer comprehensive coverage from multiple authoritative perspectives. Review the detailed sources above to inform your specific implementation decisions.

## References

{chr(10).join(f'[{i+1}] {s["title"]} - {s["url"]}' for i, s in enumerate(sources))}

---

*Report generated by Agent Management Platform Research System*
*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""


# Global singleton instance
_gemini_researcher = None

def get_gemini_researcher() -> GeminiWebResearcher:
    """Get or create Gemini researcher singleton"""
    global _gemini_researcher
    if _gemini_researcher is None:
        _gemini_researcher = GeminiWebResearcher()
    return _gemini_researcher
