"""Code Extraction and Skill Learning - Agents learn from their own code"""
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

class CodeExtractor:
    """Extracts code from reports and adds them to agent skills"""

    def __init__(self):
        self.dna_directory = Path("/home/rpas/agent-management-platform/.agents/dna")
        print("✅ Code Extractor initialized")

    def extract_code_blocks(self, markdown_content: str) -> List[Dict]:
        """
        Extract all Python code blocks from markdown content

        Returns list of code blocks with metadata
        """

        # Pattern to match Python code fences
        code_pattern = r'```python\n(.*?)```'

        code_blocks = []

        for match in re.finditer(code_pattern, markdown_content, re.DOTALL):
            code = match.group(1).strip()

            # Extract function/class names
            functions = re.findall(r'def\s+(\w+)\s*\(', code)
            classes = re.findall(r'class\s+(\w+)\s*[:(]', code)

            # Extract docstrings
            docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
            docstring = docstring_match.group(1).strip() if docstring_match else ""

            # Generate code ID
            code_id = hashlib.md5(code.encode()).hexdigest()[:12]

            code_blocks.append({
                "code_id": code_id,
                "code": code,
                "functions": functions,
                "classes": classes,
                "docstring": docstring,
                "lines": len(code.split('\n')),
                "extracted_at": datetime.utcnow().isoformat()
            })

        print(f"📦 Extracted {len(code_blocks)} code blocks")
        return code_blocks

    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code for syntax errors

        Returns (is_valid, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error on line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def categorize_code(self, code_block: Dict) -> str:
        """
        Categorize code by analyzing its content

        Returns: category (algorithm, data-processing, visualization, etc.)
        """

        code = code_block["code"].lower()

        # Simple categorization based on imports and keywords
        if 'matplotlib' in code or 'plot' in code or 'visualization' in code:
            return "visualization"
        elif 'numpy' in code or 'scipy' in code or 'calculation' in code:
            return "scientific-computing"
        elif 'pandas' in code or 'dataframe' in code:
            return "data-processing"
        elif 'rasterio' in code or 'geospatial' in code:
            return "geospatial-analysis"
        elif 'def ' in code and 'return' in code:
            return "algorithm"
        else:
            return "utility"

    def add_skill_to_genome(
        self,
        agent_name: str,
        skill_name: str,
        skill_description: str,
        code: str,
        category: str = "technical"
    ) -> bool:
        """
        Add a new skill to an agent's genome

        Args:
            agent_name: Name of the agent
            skill_name: Unique name for the skill
            skill_description: What the skill does
            code: The actual code implementing the skill
            category: technical or domain

        Returns:
            Success boolean
        """

        # Convert agent name to genome directory
        dir_name = agent_name.lower()\
            .replace(" agent", "")\
            .replace(" ", "-") + "-agent"

        genome_path = self.dna_directory / dir_name / "genome.json"

        if not genome_path.exists():
            print(f"⚠️  No genome found for {agent_name}")
            return False

        try:
            # Load existing genome
            with open(genome_path, 'r') as f:
                genome = json.load(f)

            # Add new skill
            if "skills" not in genome:
                genome["skills"] = {}
            if category not in genome["skills"]:
                genome["skills"][category] = {}

            # Create skill entry
            genome["skills"][category][skill_name] = {
                "description": skill_description,
                "code": code,
                "added": datetime.utcnow().isoformat(),
                "source": "code-extraction",
                "validated": True
            }

            # Update genome metadata
            if "agent_metadata" in genome:
                genome["agent_metadata"]["last_updated"] = datetime.utcnow().isoformat()

            # Save updated genome
            with open(genome_path, 'w') as f:
                json.dump(genome, f, indent=2)

            print(f"✅ Added skill '{skill_name}' to {agent_name}")
            return True

        except Exception as e:
            print(f"❌ Error adding skill: {e}")
            return False

    def learn_from_report(
        self,
        agent_name: str,
        report_content: str,
        task_title: str
    ) -> Dict:
        """
        Extract code from a report and add viable skills to agent's genome

        Returns summary of learning
        """

        print(f"\n🧠 Agent '{agent_name}' learning from report...")

        # Extract all code blocks
        code_blocks = self.extract_code_blocks(report_content)

        if not code_blocks:
            print("   No code blocks found in report")
            return {"skills_learned": 0, "code_blocks_found": 0}

        skills_learned = 0
        validated_count = 0
        failed_validation = []

        for block in code_blocks:
            # Validate code
            is_valid, error = self.validate_code(block["code"])

            if not is_valid:
                failed_validation.append({
                    "code_id": block["code_id"],
                    "error": error
                })
                continue

            validated_count += 1

            # Only create skills from code with functions or classes
            if not (block["functions"] or block["classes"]):
                continue

            # Generate skill name
            skill_name = block["functions"][0] if block["functions"] else block["classes"][0]

            # Get description from docstring or task
            description = block["docstring"] if block["docstring"] else f"Code from task: {task_title}"

            # Categorize
            category = self.categorize_code(block)

            # Add to genome
            success = self.add_skill_to_genome(
                agent_name=agent_name,
                skill_name=skill_name,
                skill_description=description[:200],  # Limit length
                code=block["code"],
                category="technical"
            )

            if success:
                skills_learned += 1

        print(f"   ✅ Learned {skills_learned} new skills")
        print(f"   ✅ Validated {validated_count}/{len(code_blocks)} code blocks")

        if failed_validation:
            print(f"   ⚠️  {len(failed_validation)} blocks failed validation")

        return {
            "skills_learned": skills_learned,
            "code_blocks_found": len(code_blocks),
            "validated": validated_count,
            "failed": failed_validation
        }

# Global instance
code_extractor = CodeExtractor()
