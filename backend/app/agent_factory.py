"""
Intelligent Agent Creation System

Creates agents from natural language descriptions using Gemini AI.
Generates complete agent profiles with starter skills and genome.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Import Gemini client
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed")


class AgentFactory:
    """Factory for creating intelligent agents from natural language descriptions"""

    def __init__(self):
        """Initialize the agent factory with Gemini"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai required for AgentFactory")

        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.dna_dir = Path(__file__).parent.parent.parent / ".agents" / "dna"

        print("✅ Agent Factory initialized with Gemini 2.5 Flash (FREE)")

    async def generate_agent_profile(
        self,
        description: str,
        requirements: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate agent profile from natural language description

        Args:
            description: User's natural language description of what the agent should do
            requirements: Optional list of specific requirements

        Returns:
            Dict with agent profile (name, type, specialization, capabilities, skills)
        """

        # Build prompt for Gemini
        prompt = self._build_profile_prompt(description, requirements)

        try:
            # Call Gemini
            response = self.model.generate_content(prompt)

            # Parse JSON response
            response_text = response.text.strip()

            # Extract JSON from markdown if needed
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            profile = json.loads(response_text)

            # Validate profile
            self._validate_profile(profile)

            return profile

        except Exception as e:
            print(f"❌ Gemini profile generation failed: {e}")
            raise ValueError(f"Failed to generate agent profile: {str(e)}")

    def _build_profile_prompt(self, description: str, requirements: Optional[List[str]]) -> str:
        """Build the Gemini prompt for agent profile generation"""

        requirements_text = ""
        if requirements:
            requirements_text = f"\n\nSpecific Requirements:\n" + "\n".join(f"- {req}" for req in requirements)

        prompt = f"""You are an AI Agent Designer. Based on the user's description, design an optimal intelligent agent.

User Description: {description}{requirements_text}

Create a complete agent profile that will enable this agent to excel at its intended tasks.

Generate a JSON response with this EXACT structure:
{{
  "name": "Professional agent name ending with 'Agent' (e.g., 'Satellite Imagery Analyst Agent')",
  "type": "Choose ONE: domain_specialist, developer, researcher, coordinator, or general",
  "specialization": "Detailed 1-2 sentence description of what this agent does",
  "capabilities": ["capability1", "capability2", "capability3"],
  "recommended_skills": {{
    "technical": [
      {{
        "name": "skill_name",
        "description": "What this skill does",
        "libraries": ["library1", "library2"],
        "level": 3
      }}
    ],
    "domain": [
      {{
        "name": "domain_skill_name",
        "description": "Domain knowledge description",
        "proficiency": "intermediate"
      }}
    ]
  }},
  "starter_code_templates": [
    {{
      "function_name": "main_task_function",
      "description": "Primary function the agent will use",
      "code": "def function_name(param1, param2):\\n    \\"\\"\\"Docstring\\"\\"\\"\\n    # Implementation\\n    return result"
    }}
  ]
}}

Important:
- Make the agent specialized and focused
- Include 3-5 technical skills and 2-3 domain skills
- Add 2-3 starter code templates as examples
- Use descriptive, professional names
- Ensure all code templates are valid Python with docstrings
- Technical skill levels: 1-5 (1=beginner, 5=expert)
- Domain proficiency: beginner, intermediate, advanced, expert

Return ONLY the JSON, no other text."""

        return prompt

    def _validate_profile(self, profile: Dict) -> None:
        """Validate the generated agent profile"""
        required_fields = ["name", "type", "specialization", "capabilities",
                          "recommended_skills", "starter_code_templates"]

        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Missing required field: {field}")

        # Validate type
        valid_types = ["domain_specialist", "developer", "researcher", "coordinator", "general"]
        if profile["type"] not in valid_types:
            raise ValueError(f"Invalid type: {profile['type']}. Must be one of {valid_types}")

        # Validate skills structure
        skills = profile["recommended_skills"]
        if "technical" not in skills or "domain" not in skills:
            raise ValueError("recommended_skills must have 'technical' and 'domain' keys")

    def generate_genome(self, profile: Dict, description: str) -> Dict:
        """
        Generate initial genome.json from agent profile

        Args:
            profile: Agent profile from generate_agent_profile()
            description: Original user description

        Returns:
            Complete genome dictionary ready to save
        """

        # Create agent ID from name
        agent_id = profile["name"].lower().replace(" ", "-").replace("agent", "agent")
        role = agent_id.replace("-agent", "")

        # Build genome structure
        genome = {
            "agent_metadata": {
                "agent_id": agent_id,
                "role": role,
                "total_sessions": 0,
                "evolution_stage": "beginner",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "created_by": "intelligent-agent-factory",
                "creation_method": "natural-language-description",
                "original_description": description,
                "last_active": datetime.utcnow().isoformat() + "Z"
            },
            "skills": {
                "technical": {},
                "domain": {}
            },
            "experience_bank": {
                "patterns_known": [],
                "techniques_mastered": [],
                "pitfalls_remembered": [],
                "insights_discovered": []
            },
            "session_memory": {
                "last_session_summary": "Newly created agent via intelligent agent factory. Ready for first task assignment.",
                "next_priorities": [
                    "Complete first task to begin learning",
                    "Build domain knowledge",
                    "Develop specialized techniques"
                ],
                "work_in_progress": []
            },
            "evolution_metrics": {
                "tasks_completed": 0,
                "patterns_created": 0,
                "learning_velocity": "beginner",
                "total_learning_events": 0,
                "skills_learned": 0,
                "skill_rewrites": 0
            }
        }

        # Add technical skills from profile
        for skill in profile["recommended_skills"]["technical"]:
            skill_name = skill["name"]
            genome["skills"]["technical"][skill_name] = {
                "level": skill.get("level", 3),
                "description": skill["description"],
                "libraries": skill.get("libraries", []),
                "added": datetime.utcnow().isoformat() + "Z",
                "source": "agent-factory",
                "validated": True
            }

        # Add domain skills from profile
        for skill in profile["recommended_skills"]["domain"]:
            skill_name = skill["name"]
            genome["skills"]["domain"][skill_name] = {
                "version": "1.0.0",
                "description": skill["description"],
                "proficiency": skill.get("proficiency", "intermediate"),
                "acquired": datetime.utcnow().strftime("%Y-%m-%d")
            }

        # Add starter code templates as technical skills
        for template in profile["starter_code_templates"]:
            func_name = template["function_name"]
            genome["skills"]["technical"][func_name] = {
                "level": 1,
                "description": template["description"],
                "code": template["code"],
                "added": datetime.utcnow().isoformat() + "Z",
                "source": "agent-factory-template",
                "validated": True,
                "is_template": True
            }

        return genome

    def save_genome(self, genome: Dict) -> str:
        """
        Save genome to .agents/dna/ directory

        Args:
            genome: Complete genome dictionary

        Returns:
            Path to saved genome file
        """
        agent_id = genome["agent_metadata"]["agent_id"]
        agent_dir = self.dna_dir / agent_id

        # Create directory
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Save genome.json
        genome_path = agent_dir / "genome.json"
        with open(genome_path, 'w') as f:
            json.dump(genome, f, indent=2)

        print(f"✅ Genome saved: {genome_path}")
        return str(genome_path)

    async def create_intelligent_agent(
        self,
        description: str,
        requirements: Optional[List[str]] = None
    ) -> Dict:
        """
        Complete intelligent agent creation pipeline

        Args:
            description: Natural language description of agent purpose
            requirements: Optional specific requirements

        Returns:
            Dict with agent details and creation summary
        """

        print(f"🤖 Creating intelligent agent from description...")
        print(f"   Description: {description[:100]}...")

        # Step 1: Generate profile using Gemini
        print("🧠 Generating agent profile with Gemini AI...")
        profile = await self.generate_agent_profile(description, requirements)

        print(f"✅ Profile generated:")
        print(f"   Name: {profile['name']}")
        print(f"   Type: {profile['type']}")
        print(f"   Skills: {len(profile['recommended_skills']['technical'])} technical, "
              f"{len(profile['recommended_skills']['domain'])} domain")

        # Step 2: Generate genome
        print("🧬 Generating agent genome...")
        genome = self.generate_genome(profile, description)

        total_skills = len(genome["skills"]["technical"]) + len(genome["skills"]["domain"])
        print(f"✅ Genome generated with {total_skills} initial skills")

        # Step 3: Save genome to filesystem
        print("💾 Saving genome to .agents/dna/...")
        genome_path = self.save_genome(genome)

        # Step 4: Prepare agent data for database
        agent_data = {
            "id": str(uuid.uuid4()),
            "name": profile["name"],
            "type": profile["type"],
            "specialization": profile["specialization"],
            "capabilities": profile["capabilities"],
            "config": {
                "created_by": "intelligent-agent-factory",
                "original_description": description,
                "genome_path": genome_path,
                "evolution_stage": "beginner"
            },
            "prompt_file": None,
            "status": "idle"
        }

        # Return complete result
        result = {
            "agent": agent_data,
            "profile": profile,
            "genome": genome,
            "genome_path": genome_path,
            "skills_count": total_skills,
            "technical_skills": len(genome["skills"]["technical"]),
            "domain_skills": len(genome["skills"]["domain"]),
            "starter_templates": len(profile["starter_code_templates"]),
            "ready_for_tasks": True,
            "evolution_stage": "beginner",
            "message": f"Agent '{profile['name']}' created successfully with {total_skills} initial skills!"
        }

        print(f"🎉 Agent creation complete!")
        return result


# Singleton instance
_agent_factory = None

def get_agent_factory() -> AgentFactory:
    """Get or create AgentFactory singleton"""
    global _agent_factory
    if _agent_factory is None:
        _agent_factory = AgentFactory()
    return _agent_factory
