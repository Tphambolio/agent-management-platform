"""Research Lab - AI Agent Research & Report Generation"""
import os
import anthropic
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class ResearchRequest(BaseModel):
    """Research request from user"""
    topic: str
    agent_type: str  # e.g., "Security Analyst", "Data Scientist"
    depth: str = "comprehensive"  # quick, standard, comprehensive
    output_format: str = "markdown"  # markdown, json, pdf
    
class ResearchLab:
    """AI-powered research lab using Claude"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️  No ANTHROPIC_API_KEY found - research features disabled")
    
    def get_agent_prompt(self, agent_type: str, topic: str, depth: str) -> str:
        """Generate specialized prompt based on agent type"""
        
        agent_prompts = {
            "Security Analyst": f"""You are a Security Analyst AI agent. 
Research the following topic and provide a comprehensive security analysis:

Topic: {topic}

Your analysis should include:
1. Security risks and vulnerabilities
2. Threat assessment
3. Mitigation strategies
4. Industry best practices
5. Compliance considerations
6. Recommended security controls

Depth: {depth}
Format: Professional security report with clear sections and actionable recommendations.""",

            "Data Scientist": f"""You are a Data Scientist AI agent.
Research and analyze the following topic:

Topic: {topic}

Your analysis should include:
1. Data sources and datasets available
2. Statistical analysis approach
3. Key metrics and KPIs
4. Visualization recommendations
5. Predictive insights
6. Actionable conclusions

Depth: {depth}
Format: Data-driven report with methodology, findings, and recommendations.""",

            "Project Architect": f"""You are a Project Architect AI agent.
Research and design a solution for:

Topic: {topic}

Your architectural analysis should include:
1. System requirements analysis
2. Architectural patterns and design
3. Technology stack recommendations
4. Scalability considerations
5. Integration points
6. Implementation roadmap

Depth: {depth}
Format: Technical architecture document with diagrams (described in text) and specifications.""",

            "Documentation Writer": f"""You are a Documentation Writer AI agent.
Research and document the following:

Topic: {topic}

Your documentation should include:
1. Executive summary
2. Detailed explanation
3. Use cases and examples
4. Best practices
5. Common pitfalls
6. References and resources

Depth: {depth}
Format: Professional technical documentation in clear, accessible language.""",

            "Performance Engineer": f"""You are a Performance Engineer AI agent.
Research performance aspects of:

Topic: {topic}

Your performance analysis should include:
1. Performance benchmarks and metrics
2. Bottleneck identification
3. Optimization strategies
4. Profiling recommendations
5. Scaling considerations
6. Performance monitoring approach

Depth: {depth}
Format: Performance engineering report with data-driven insights.""",

            "Code Reviewer": f"""You are a Code Reviewer AI agent.
Review and analyze:

Topic: {topic}

Your code review should include:
1. Code quality assessment
2. Security vulnerabilities
3. Performance issues
4. Best practices violations
5. Refactoring suggestions
6. Testing recommendations

Depth: {depth}
Format: Structured code review report with severity ratings.""",
        }
        
        # Default prompt for agents not in the map
        default_prompt = f"""You are a specialized AI agent with expertise in {agent_type}.
Research the following topic and provide a comprehensive analysis:

Topic: {topic}

Provide a thorough analysis from your area of expertise.
Depth: {depth}
Format: Professional report with clear structure and actionable insights."""
        
        return agent_prompts.get(agent_type, default_prompt)
    
    async def conduct_research(self, request: ResearchRequest) -> Dict:
        """Conduct AI research and generate report"""
        
        if not self.client:
            return {
                "status": "error",
                "error": "ANTHROPIC_API_KEY not configured",
                "suggestion": "Set environment variable: export ANTHROPIC_API_KEY=sk-ant-..."
            }
        
        try:
            # Generate specialized prompt
            prompt = self.get_agent_prompt(request.agent_type, request.topic, request.depth)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract report content
            report_content = message.content[0].text
            
            # Generate report metadata
            report = {
                "status": "success",
                "topic": request.topic,
                "agent_type": request.agent_type,
                "depth": request.depth,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(report_content.split()),
                "content": report_content,
                "format": request.output_format,
                "model": "claude-sonnet-4-20250514"
            }
            
            return report
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "topic": request.topic,
                "agent_type": request.agent_type
            }

# Singleton instance
research_lab = ResearchLab()
