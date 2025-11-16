"""Agent Skills System - Loads genome data and provides real agent capabilities"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import anthropic

class AgentSkillsSystem:
    """Manages agent genome data and provides skill-based capabilities"""

    def __init__(self):
        self.dna_directory = Path("/home/rpas/agent-management-platform/.agents/dna")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if self.anthropic_api_key:
            self.claude = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.claude = None
            print("⚠️  No ANTHROPIC_API_KEY - AI skill synthesis disabled")

    def load_agent_genome(self, agent_name: str) -> Optional[Dict]:
        """Load agent genome from DNA directory"""

        # Convert agent name to directory name
        # "Backend Developer Agent" -> "backend-developer-agent"
        dir_name = agent_name.lower()\
            .replace(" agent", "")\
            .replace(" ", "-") + "-agent"

        genome_path = self.dna_directory / dir_name / "genome.json"

        if not genome_path.exists():
            print(f"⚠️  No genome found for {agent_name} at {genome_path}")
            return None

        try:
            with open(genome_path, 'r') as f:
                genome = json.load(f)
                print(f"✅ Loaded genome for {agent_name}")
                print(f"   Evolution: {genome.get('agent_metadata', {}).get('evolution_stage', 'unknown')}")
                print(f"   Sessions: {genome.get('agent_metadata', {}).get('total_sessions', 0)}")
                return genome
        except Exception as e:
            print(f"❌ Error loading genome: {e}")
            return None

    def get_agent_context(self, agent_name: str) -> str:
        """
        Build rich context from agent genome for Claude
        This provides the agent with access to all its learned skills
        """
        genome = self.load_agent_genome(agent_name)

        if not genome:
            return f"Agent: {agent_name} (no specialized training data)"

        metadata = genome.get("agent_metadata", {})
        skills = genome.get("skills", {})
        experience = genome.get("experience_bank", {})
        session_memory = genome.get("session_memory", {})

        # Build comprehensive context
        context_parts = []

        # Agent identity
        context_parts.append(f"""# Agent Profile: {agent_name}
Role: {metadata.get('role', 'general')}
Evolution Stage: {metadata.get('evolution_stage', 'beginner')}
Training Sessions: {metadata.get('total_sessions', 0)}
Last Active: {metadata.get('last_active', 'never')}
""")

        # Technical skills
        technical_skills = skills.get("technical", {})
        if technical_skills:
            context_parts.append("\n## Technical Skills")
            for skill_name, skill_data in technical_skills.items():
                level = skill_data.get("level", 1)
                desc = skill_data.get("description", skill_name)
                context_parts.append(f"- **{skill_name}** (Level {level}/5): {desc}")

        # Domain expertise
        domain_skills = skills.get("domain", {})
        if domain_skills:
            context_parts.append("\n## Domain Expertise")
            for skill_name, skill_data in domain_skills.items():
                if isinstance(skill_data, dict):
                    desc = skill_data.get("description", skill_name)
                    prof = skill_data.get("proficiency", "N/A")
                    context_parts.append(f"- **{skill_name}**: {desc} ({prof})")

        # Known patterns and formulas
        patterns = experience.get("patterns_known", [])
        if patterns:
            context_parts.append(f"\n## Known Patterns & Formulas ({len(patterns)} total)")
            # Include top 10 most important patterns
            for pattern in patterns[:10]:
                name = pattern.get("name", "unknown")
                desc = pattern.get("description", "")
                context_parts.append(f"- **{name}**: {desc}")

        # Mastered techniques
        techniques = experience.get("techniques_mastered", [])
        if techniques:
            context_parts.append(f"\n## Mastered Techniques ({len(techniques)} total)")
            for tech in techniques[:10]:
                name = tech.get("name", "unknown")
                desc = tech.get("description", "")
                context_parts.append(f"- **{name}**: {desc}")

        # Critical pitfalls to avoid
        pitfalls = experience.get("pitfalls_remembered", [])
        if pitfalls:
            context_parts.append(f"\n## Critical Pitfalls to Avoid ({len(pitfalls)} total)")
            for pitfall in pitfalls[:10]:
                name = pitfall.get("pitfall", "unknown")
                desc = pitfall.get("description", "")
                context_parts.append(f"- **{name}**: {desc}")

        # Key insights
        insights = experience.get("insights_discovered", [])
        if insights:
            context_parts.append(f"\n## Key Insights ({len(insights)} total)")
            for insight in insights[:10]:
                text = insight.get("insight", "")
                context_parts.append(f"- {text}")

        # Recent work and priorities
        if session_memory:
            last_summary = session_memory.get("last_session_summary", "")
            priorities = session_memory.get("next_priorities", [])

            if last_summary:
                context_parts.append(f"\n## Last Session Summary\n{last_summary}")

            if priorities:
                context_parts.append("\n## Current Priorities")
                for priority in priorities:
                    context_parts.append(f"- {priority}")

        return "\n".join(context_parts)

    async def execute_task_with_skills(
        self,
        agent_name: str,
        task_title: str,
        task_description: str,
        research_data: Optional[Dict] = None
    ) -> Dict:
        """
        Execute a task using the agent's specialized skills

        This combines:
        1. Agent's genome knowledge (patterns, techniques, skills)
        2. Web research data (if available)
        3. Claude AI for synthesis
        """

        if not self.claude:
            return {
                "status": "error",
                "message": "AI synthesis not available - no ANTHROPIC_API_KEY"
            }

        # Load agent's specialized knowledge
        agent_context = self.get_agent_context(agent_name)

        # Build the prompt
        prompt_parts = [
            f"You are {agent_name}, a specialized AI agent with extensive training and experience.",
            "",
            agent_context,
            "",
            f"# Task Assignment",
            f"**Title:** {task_title}",
            f"**Description:** {task_description}",
            ""
        ]

        # Include research data if available
        if research_data and research_data.get("sources"):
            prompt_parts.append("# Web Research Findings")
            for i, source in enumerate(research_data["sources"][:10], 1):
                prompt_parts.append(f"\n**Source {i}: {source['title']}**")
                prompt_parts.append(f"URL: {source['url']}")
                prompt_parts.append(f"{source['description']}")

        prompt_parts.append("""
# Platform Capabilities: Real Satellite Data Access 🛰️

**IMPORTANT**: You have access to REAL satellite imagery download capabilities. Do NOT simulate data!

## Geospatial API Endpoints Available:

### 1. Download Real Sentinel-2 Satellite Imagery
**Endpoint:** `POST /api/geospatial/download-satellite`

**Use this when tasks require:**
- Satellite imagery for any location
- Spectral band data (Red, NIR, SWIR, etc.)
- Vegetation indices (NDVI, EVI)
- Fuel moisture analysis
- Land cover classification
- Any geospatial raster datasets

**Request Format:**
```python
import requests

response = requests.post('http://localhost:8000/api/geospatial/download-satellite', json={
    "location_name": "Calgary",
    "bbox": [-114.3, 50.8, -113.8, 51.2],  # [min_lon, min_lat, max_lon, max_lat]
    "bands": ["B04", "B08", "B11"],  # Red, NIR, SWIR1
    "days_back": 60,
    "max_cloud_cover": 15
})

result = response.json()
# Returns: {
#   "status": "success",
#   "scene_id": "S2A_MSIL2A_...",
#   "cloud_cover": 8.2,
#   "datetime": "2025-11-10T18:23:45",
#   "bands": {
#     "B04": "/tmp/satellite_downloads/Calgary/.../B04.tif",
#     "B08": "/tmp/satellite_downloads/Calgary/.../B08.tif",
#     "B11": "/tmp/satellite_downloads/Calgary/.../B11.tif"
#   },
#   "output_dir": "/tmp/satellite_downloads/Calgary/..."
# }
```

**Common Sentinel-2 Bands:**
- B02: Blue (490nm)
- B03: Green (560nm)
- B04: Red (665nm) - for NDVI
- B08: NIR (842nm) - for NDVI
- B11: SWIR1 (1610nm) - for fuel moisture
- B12: SWIR2 (2190nm) - for fuel moisture

### 2. Calculate NDVI from Downloaded Bands
**Endpoint:** `POST /api/geospatial/calculate-ndvi`

Upload the downloaded Red and NIR bands to calculate Normalized Difference Vegetation Index.

### 3. Check Available Capabilities
**Endpoint:** `GET /api/geospatial/capabilities`

Returns information about available geospatial processing features.

---

**CRITICAL INSTRUCTION**: When tasked with building datasets, fuel layers, or any geospatial analysis:
1. ✅ ALWAYS use `/api/geospatial/download-satellite` to get REAL data
2. ✅ Show the actual API call in your code blocks
3. ✅ Use the real file paths returned from the API
4. ❌ NEVER use np.random.rand() or simulated data
5. ❌ NEVER write code that pretends to download data

**Example Task: "Build fuel dataset for Calgary"**
```python
# CORRECT APPROACH - Use real satellite download API
import requests

# Step 1: Download real Sentinel-2 data
response = requests.post('http://localhost:8000/api/geospatial/download-satellite', json={
    "location_name": "Calgary",
    "bbox": [-114.3, 50.8, -113.8, 51.2],
    "bands": ["B04", "B08", "B11", "B12"],  # Red, NIR, SWIR bands
    "days_back": 60,
    "max_cloud_cover": 15
})

satellite_data = response.json()

if satellite_data["status"] == "success":
    # Step 2: Use the REAL downloaded GeoTIFF files
    red_band_path = satellite_data["bands"]["B04"]
    nir_band_path = satellite_data["bands"]["B08"]
    swir1_path = satellite_data["bands"]["B11"]

    # Step 3: Process real data with rasterio
    import rasterio

    with rasterio.open(red_band_path) as red:
        red_data = red.read(1)

    with rasterio.open(nir_band_path) as nir:
        nir_data = nir.read(1)

    # Step 4: Calculate NDVI from real satellite data
    ndvi = (nir_data - red_data) / (nir_data + red_data + 1e-10)

    print(f"Downloaded scene: {satellite_data['scene_id']}")
    print(f"Cloud cover: {satellite_data['cloud_cover']}%")
    print(f"NDVI range: {ndvi.min():.3f} to {ndvi.max():.3f}")
```

---

# Your Mission

You are a specialized agent writing a SCIENTIFIC RESEARCH REPORT. This must be publication-quality work with:

1. **Rigorous Analysis**: Apply your expert knowledge and training
2. **Computational Evidence**: Include working Python code with real results
3. **Technical Precision**: Use exact formulas, equations, and data
4. **Reproducibility**: All code must be executable and well-documented

**CRITICAL REQUIREMENTS:**

- Include at least 2-3 code blocks with real computations
- Show actual numerical results, not placeholders
- Use your domain expertise to write technical,not generic content
- Format as a scientific journal article

**Required Structure:**

## Abstract
[150-250 words: Problem, methods, key findings, significance]

## 1. Introduction
### 1.1 Background and Motivation
[Scientific context using your domain knowledge]

### 1.2 Research Question/Objective
[Clear statement of what this work investigates]

## 2. Methodology
### 2.1 Approach
[Describe methods using technical precision]

### 2.2 Implementation
[Include working Python code]

```python
# Example: Real computation based on research
import numpy as np

# [Your code here - must be executable and produce results]
```

## 3. Results
### 3.1 Computational Findings
[Present actual data, calculations, and visualizations]

### 3.2 Analysis
[Interpret results using your expertise]

## 4. Discussion
### 4.1 Key Insights
[Connect findings to broader domain knowledge]

### 4.2 Implications
[What this means for the field]

## 5. Code Repository
### 5.1 Core Algorithms
[Additional code blocks agents can learn from]

```python
# Production-ready code with documentation
def technique_name(parameters):
    \"\"\"
    Docstring explaining the method

    Args:
        parameters: Description

    Returns:
        Results with units
    \"\"\"
    # Implementation
    pass
```

### 5.2 Usage Examples
[How to apply this code]

## 6. Conclusions
[Summarize findings and future work]

## References
[Cite research sources and your training data]

---

**REMEMBER**: This is a scientific document. Use your specialized training, include real code with outputs, and demonstrate technical expertise throughout.
""")

        try:
            # Call Claude with agent's full context
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                messages=[{
                    "role": "user",
                    "content": "\n".join(prompt_parts)
                }]
            )

            return {
                "status": "success",
                "content": message.content[0].text,
                "agent_context_loaded": True,
                "skills_utilized": len(agent_context.split("\n")),
                "model": "claude-sonnet-4"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"AI execution error: {str(e)}"
            }

    def get_agent_capabilities_summary(self, agent_name: str) -> Dict:
        """Get a summary of agent's capabilities from genome"""
        genome = self.load_agent_genome(agent_name)

        if not genome:
            return {
                "has_genome": False,
                "capabilities": []
            }

        skills = genome.get("skills", {})
        experience = genome.get("experience_bank", {})

        capabilities = []

        # Top technical skills
        technical = skills.get("technical", {})
        for skill_name, skill_data in list(technical.items())[:5]:
            capabilities.append({
                "type": "technical",
                "name": skill_name,
                "level": skill_data.get("level", 1),
                "description": skill_data.get("description", "")
            })

        # Top domain skills
        domain = skills.get("domain", {})
        for skill_name, skill_data in list(domain.items())[:5]:
            if isinstance(skill_data, dict):
                capabilities.append({
                    "type": "domain",
                    "name": skill_name,
                    "proficiency": skill_data.get("proficiency", "beginner"),
                    "description": skill_data.get("description", "")
                })

        return {
            "has_genome": True,
            "evolution_stage": genome.get("agent_metadata", {}).get("evolution_stage", "beginner"),
            "total_sessions": genome.get("agent_metadata", {}).get("total_sessions", 0),
            "patterns_known": len(experience.get("patterns_known", [])),
            "techniques_mastered": len(experience.get("techniques_mastered", [])),
            "capabilities": capabilities
        }

# Global instance
agent_skills_system = AgentSkillsSystem()
