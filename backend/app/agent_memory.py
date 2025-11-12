"""Agent Memory System - Tracks agent history, learnings, and evolving knowledge"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

class AgentMemory:
    """Manages agent memory: past tasks, learnings, patterns discovered"""

    def __init__(self):
        self.memory_dir = Path("/app/.agents/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ Agent Memory System initialized")
        print(f"   Memory storage: {self.memory_dir}")

    def _get_agent_memory_file(self, agent_id: str) -> Path:
        """Get the memory file path for an agent"""
        return self.memory_dir / f"{agent_id}_memory.json"

    def _load_memory(self, agent_id: str) -> Dict:
        """Load agent's memory from disk"""

        memory_file = self._get_agent_memory_file(agent_id)

        if not memory_file.exists():
            # Initialize new memory
            return {
                "agent_id": agent_id,
                "created_at": datetime.utcnow().isoformat(),
                "total_tasks": 0,
                "total_reports": 0,
                "task_history": [],
                "patterns_discovered": [],
                "insights": [],
                "skills_used": defaultdict(int),
                "performance_metrics": {
                    "average_task_duration": 0,
                    "total_sources_researched": 0,
                    "total_datasets_created": 0
                },
                "knowledge_graph": {
                    "topics": [],
                    "connections": []
                }
            }

        try:
            with open(memory_file, 'r') as f:
                memory = json.load(f)
                # Convert skills_used back to defaultdict
                if "skills_used" in memory and isinstance(memory["skills_used"], dict):
                    memory["skills_used"] = defaultdict(int, memory["skills_used"])
                return memory
        except Exception as e:
            print(f"⚠️  Error loading memory for {agent_id}: {e}")
            return self._load_memory.__defaults__[0]

    def _save_memory(self, agent_id: str, memory: Dict) -> None:
        """Save agent's memory to disk"""

        memory_file = self._get_agent_memory_file(agent_id)

        try:
            # Convert defaultdict to dict for JSON serialization
            if "skills_used" in memory and isinstance(memory["skills_used"], defaultdict):
                memory["skills_used"] = dict(memory["skills_used"])

            with open(memory_file, 'w') as f:
                json.dump(memory, f, indent=2, default=str)

            print(f"💾 Memory saved for agent {agent_id}")
        except Exception as e:
            print(f"❌ Error saving memory: {e}")

    def record_task_completion(
        self,
        agent_id: str,
        task_id: str,
        task_title: str,
        duration_seconds: float,
        sources_found: int,
        skills_utilized: List[str],
        report_id: Optional[str] = None
    ) -> None:
        """Record a completed task in agent's memory"""

        memory = self._load_memory(agent_id)

        # Add to task history
        task_record = {
            "task_id": task_id,
            "title": task_title,
            "completed_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration_seconds,
            "sources_found": sources_found,
            "skills_utilized": skills_utilized,
            "report_id": report_id
        }

        memory["task_history"].append(task_record)
        memory["total_tasks"] += 1
        if report_id:
            memory["total_reports"] += 1

        # Update skills usage tracking
        for skill in skills_utilized:
            memory["skills_used"][skill] += 1

        # Update performance metrics
        metrics = memory["performance_metrics"]
        metrics["total_sources_researched"] += sources_found

        # Recalculate average task duration
        total_duration = sum(t["duration_seconds"] for t in memory["task_history"])
        metrics["average_task_duration"] = total_duration / len(memory["task_history"])

        # Save updated memory
        self._save_memory(agent_id, memory)

        print(f"📝 Task recorded in memory for agent {agent_id}")
        print(f"   Total tasks: {memory['total_tasks']}")
        print(f"   Average duration: {metrics['average_task_duration']:.1f}s")

    def record_insight(
        self,
        agent_id: str,
        insight: str,
        context: str,
        source_task_id: Optional[str] = None
    ) -> None:
        """Record a new insight or learning"""

        memory = self._load_memory(agent_id)

        insight_record = {
            "insight": insight,
            "context": context,
            "source_task_id": source_task_id,
            "discovered_at": datetime.utcnow().isoformat()
        }

        memory["insights"].append(insight_record)
        self._save_memory(agent_id, memory)

        print(f"💡 New insight recorded for agent {agent_id}")

    def record_pattern(
        self,
        agent_id: str,
        pattern_name: str,
        pattern_description: str,
        confidence: str = "medium",
        evidence: Optional[List[str]] = None
    ) -> None:
        """Record a discovered pattern"""

        memory = self._load_memory(agent_id)

        pattern_record = {
            "name": pattern_name,
            "description": pattern_description,
            "confidence": confidence,
            "evidence": evidence or [],
            "discovered_at": datetime.utcnow().isoformat()
        }

        memory["patterns_discovered"].append(pattern_record)
        self._save_memory(agent_id, memory)

        print(f"🔍 Pattern recorded for agent {agent_id}: {pattern_name}")

    def get_agent_context_from_memory(self, agent_id: str) -> str:
        """
        Generate context string from agent's memory for use in prompts

        This provides the agent with access to its past work and learnings
        """

        memory = self._load_memory(agent_id)

        context_parts = []

        # Overview
        context_parts.append(f"""# Agent Memory - Task History & Learnings

**Total Tasks Completed:** {memory['total_tasks']}
**Total Reports Generated:** {memory['total_reports']}
**Average Task Duration:** {memory['performance_metrics'].get('average_task_duration', 0):.1f} seconds
**Total Sources Researched:** {memory['performance_metrics'].get('total_sources_researched', 0)}
""")

        # Recent tasks
        recent_tasks = memory["task_history"][-10:]  # Last 10 tasks
        if recent_tasks:
            context_parts.append("\n## Recent Task History")
            for task in recent_tasks:
                context_parts.append(
                    f"- **{task['title']}** ({task['duration_seconds']:.1f}s, "
                    f"{task['sources_found']} sources)"
                )

        # Most used skills
        skills_used = dict(memory.get("skills_used", {}))
        if skills_used:
            context_parts.append("\n## Most Utilized Skills")
            sorted_skills = sorted(skills_used.items(), key=lambda x: x[1], reverse=True)
            for skill, count in sorted_skills[:10]:
                context_parts.append(f"- **{skill}**: used {count} times")

        # Patterns discovered
        patterns = memory.get("patterns_discovered", [])
        if patterns:
            context_parts.append(f"\n## Patterns Discovered ({len(patterns)} total)")
            for pattern in patterns[-10:]:  # Last 10 patterns
                context_parts.append(
                    f"- **{pattern['name']}**: {pattern['description']} "
                    f"(confidence: {pattern.get('confidence', 'medium')})"
                )

        # Insights
        insights = memory.get("insights", [])
        if insights:
            context_parts.append(f"\n## Key Insights ({len(insights)} total)")
            for insight in insights[-10:]:  # Last 10 insights
                context_parts.append(f"- {insight['insight']}")

        return "\n".join(context_parts)

    def get_memory_summary(self, agent_id: str) -> Dict:
        """Get a summary of agent's memory for API responses"""

        memory = self._load_memory(agent_id)

        return {
            "agent_id": agent_id,
            "total_tasks": memory["total_tasks"],
            "total_reports": memory["total_reports"],
            "recent_tasks": memory["task_history"][-5:],  # Last 5
            "top_skills": dict(
                sorted(
                    dict(memory.get("skills_used", {})).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ),
            "patterns_count": len(memory.get("patterns_discovered", [])),
            "insights_count": len(memory.get("insights", [])),
            "performance_metrics": memory["performance_metrics"]
        }

    def clear_memory(self, agent_id: str) -> None:
        """Clear an agent's memory (use with caution!)"""

        memory_file = self._get_agent_memory_file(agent_id)
        if memory_file.exists():
            memory_file.unlink()
            print(f"🗑️  Memory cleared for agent {agent_id}")

    def export_memory(self, agent_id: str) -> Optional[Dict]:
        """Export agent's full memory for backup or analysis"""

        memory = self._load_memory(agent_id)
        return memory

    def import_memory(self, agent_id: str, memory_data: Dict) -> None:
        """Import memory data (for restoration or transfer)"""

        memory_data["agent_id"] = agent_id
        self._save_memory(agent_id, memory_data)
        print(f"📥 Memory imported for agent {agent_id}")

# Global instance
agent_memory = AgentMemory()
