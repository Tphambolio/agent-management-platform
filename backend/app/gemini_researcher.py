"""Gemini-Powered Research Module - FREE API Alternative"""
import os
import google.generativeai as genai
from typing import Dict, List, Optional


class GeminiResearcher:
    """Automated research using Google Gemini API (FREE tier available)"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use Gemini Pro for fast, free research
            self.model = genai.GenerativeModel('gemini-pro')
            self.available = True
            print("✅ Gemini AI initialized (FREE tier)")
        else:
            self.model = None
            self.available = False
            print("⚠️  No GEMINI_API_KEY found - research disabled")

    def generate_research_report(
        self,
        topic: str,
        agent_type: str = "Research Assistant",
        search_results: Optional[List[Dict]] = None,
        depth: str = "comprehensive"
    ) -> str:
        """
        Generate comprehensive research report using Gemini

        Args:
            topic: Research topic
            agent_type: Type of agent conducting research
            search_results: Optional web search results
            depth: quick | standard | comprehensive

        Returns:
            Markdown-formatted research report
        """
        if not self.available:
            return self._generate_fallback_report(topic, agent_type)

        # Build context from search results
        context = ""
        if search_results:
            context = "\n\n# Web Research Findings\n"
            for i, result in enumerate(search_results[:10], 1):
                context += f"\n**Source {i}: {result.get('title', 'Untitled')}**\n"
                context += f"URL: {result.get('url', 'N/A')}\n"
                context += f"{result.get('description', 'No description')}\n"

        # Create research prompt
        prompt = f"""You are a {agent_type} conducting scientific research.

# Research Topic
{topic}

{context}

# Your Task: Generate a COMPREHENSIVE SCIENTIFIC RESEARCH REPORT

**Required Structure:**

## Executive Summary
[150-250 words: Problem, approach, key findings, significance]

## 1. Introduction
### 1.1 Background and Context
[Explain why this topic matters]

### 1.2 Research Objectives
[Clear statement of what you're investigating]

## 2. Methodology
### 2.1 Research Approach
[Describe your analysis method]

### 2.2 Data Sources
[List and evaluate sources of information]

## 3. Findings
### 3.1 Key Discoveries
[Present main findings with evidence]

### 3.2 Analysis
[Interpret findings with technical precision]

### 3.3 Quantitative Results
[Include any calculations or metrics]

## 4. Discussion
### 4.1 Implications
[What these findings mean for the field]

### 4.2 Limitations
[Acknowledge gaps and constraints]

### 4.3 Future Directions
[Recommend next steps]

## 5. Conclusions
[Summarize key takeaways and recommendations]

## 6. References
[Cite all sources used]

---

**Important Requirements:**
- Use technical precision and domain expertise
- Include specific examples and evidence
- Provide actionable recommendations
- Format professionally with clear sections
- Cite sources where applicable

Generate the complete report now."""

        try:
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )

            return response.text

        except Exception as e:
            print(f"⚠️  Gemini API error: {e}")
            return self._generate_fallback_report(topic, agent_type)

    def _generate_fallback_report(self, topic: str, agent_type: str) -> str:
        """Generate basic report when API is unavailable"""
        return f"""# Research Report: {topic}

**Agent:** {agent_type}
**Status:** ⚠️ Limited Report (No API Key Available)

## Summary

This is a placeholder report generated without AI assistance.

To enable full automated research reports:
1. Get a free Gemini API key from https://makersuite.google.com/app/apikey
2. Add to Render environment variables: `GEMINI_API_KEY=your-key-here`
3. Redeploy the service

## Topic Overview

Research topic: {topic}

## Recommendations

- Configure Gemini API for comprehensive automated research
- Free tier includes 60 requests per minute
- No credit card required for free tier

## Next Steps

1. Obtain API key
2. Configure environment
3. Re-run research task

---

*This report was generated without AI assistance. Enable Gemini API for full functionality.*
"""


# Singleton instance
gemini_researcher = GeminiResearcher()
