#!/usr/bin/env python3
"""Load all agents from .agents/dna directory into the database"""

import json
import os
import requests
from pathlib import Path

# API base URL
API_URL = "http://localhost:8002/api/agents"

# Path to DNA directory
DNA_DIR = Path("/home/rpas/agent-management-platform/.agents/dna")

# Agent type mapping
AGENT_TYPE_MAP = {
    "backend-developer": "developer",
    "frontend-truth": "developer",
    "software-architect": "architecture",
    "data-scientist": "analytics",
    "research-professor": "research",
    "qa-testing": "quality",
    "benchmark-analyst": "analytics",
    "fire-behavior-specialist": "specialist",
    "visualization-engineer": "developer",
    "weather-system": "specialist",
    "wildfire-analyst": "analytics",
    "self-audit-test": "quality"
}

def load_agent_genome(genome_path):
    """Load and parse agent genome.json file"""
    with open(genome_path, 'r') as f:
        return json.load(f)

def extract_capabilities(genome):
    """Extract capabilities from genome skills"""
    capabilities = []

    # Technical skills
    technical_skills = genome.get("skills", {}).get("technical", {})
    for skill_name, skill_data in list(technical_skills.items())[:5]:  # Top 5 skills
        capabilities.append(skill_data.get("description", skill_name.replace("_", " ").title()))

    # Domain skills
    domain_skills = genome.get("skills", {}).get("domain", {})
    for skill_name, skill_data in list(domain_skills.items())[:3]:  # Top 3 domain skills
        capabilities.append(skill_data.get("description", skill_name.replace("_", " ").title()))

    return capabilities[:8]  # Limit to 8 capabilities

def create_specialization(genome, agent_role):
    """Create specialization description from genome"""
    metadata = genome.get("agent_metadata", {})
    evolution_stage = metadata.get("evolution_stage", "beginner")
    total_sessions = metadata.get("total_sessions", 0)

    # Get top skill
    technical_skills = genome.get("skills", {}).get("technical", {})
    top_skill = list(technical_skills.keys())[0] if technical_skills else agent_role

    specialization = f"{evolution_stage.title()} level agent with {total_sessions} training sessions. "
    specialization += f"Specialized in {top_skill.replace('_', ' ')}."

    return specialization

def register_agent(agent_id, genome):
    """Register an agent via the API"""
    metadata = genome.get("agent_metadata", {})
    role = metadata.get("role", agent_id)

    # Map to agent type
    agent_type = AGENT_TYPE_MAP.get(role, "general")

    # Create agent name
    name = agent_id.replace("-agent", "").replace("-", " ").title() + " Agent"

    # Extract data
    specialization = create_specialization(genome, role)
    capabilities = extract_capabilities(genome)

    agent_data = {
        "name": name,
        "type": agent_type,
        "specialization": specialization,
        "capabilities": capabilities
    }

    try:
        response = requests.post(API_URL, json=agent_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registered: {name}")
            print(f"   Type: {agent_type}")
            print(f"   Skills: {len(capabilities)} capabilities")
            return result
        else:
            print(f"⚠️  Failed to register {name}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error registering {name}: {e}")
        return None

def main():
    """Load all agents from DNA directory"""
    print("🔬 Loading agents from DNA directory...")
    print(f"📁 DNA Directory: {DNA_DIR}\n")

    agent_count = 0

    # Find all agent directories with genome.json
    for agent_dir in DNA_DIR.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith("_"):
            genome_file = agent_dir / "genome.json"

            if genome_file.exists():
                try:
                    genome = load_agent_genome(genome_file)
                    result = register_agent(agent_dir.name, genome)
                    if result:
                        agent_count += 1
                    print()  # Blank line between agents
                except Exception as e:
                    print(f"⚠️  Error loading {agent_dir.name}: {e}\n")

    print(f"\n🎉 Loaded {agent_count} agents successfully!")
    print(f"\nView them at: http://localhost:3000/agents")

if __name__ == "__main__":
    main()
