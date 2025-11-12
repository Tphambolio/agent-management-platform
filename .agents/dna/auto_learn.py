"""
Autonomous Agent DNA Learning System
Automatically captures learnings from every action
"""

import json
import os
from pathlib import Path
from datetime import datetime
import functools


class AgentDNA:
    """Self-updating agent DNA that learns automatically"""

    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.dna_dir = Path(f".agents/dna/{agent_id}")
        self.genome_file = self.dna_dir / "genome.json"
        self.session_log = []
        self.auto_save_enabled = True

        # Load existing DNA or create new
        if self.genome_file.exists():
            with open(self.genome_file, "r") as f:
                self.genome = json.load(f)
            # Ensure compatibility with existing genomes
            self._ensure_genome_compatibility()
        else:
            self.genome = self._create_initial_genome()

    def _create_initial_genome(self):
        """Create initial DNA structure"""
        return {
            "agent_metadata": {
                "agent_id": self.agent_id,
                "created_date": datetime.now().isoformat(),
                "total_sessions": 0,
                "last_active": datetime.now().isoformat(),
            },
            "skills": {"technical": {}, "domain": {}},
            "experience_bank": {
                "patterns_known": [],
                "techniques_mastered": [],
                "pitfalls_remembered": [],
                "insights_discovered": [],
            },
            "session_memory": {
                "last_session_summary": "",
                "next_priorities": [],
                "work_in_progress": [],
            },
            "evolution_metrics": {
                "tasks_completed": 0,
                "patterns_created": 0,
                "learning_velocity": "developing",
                "total_learning_events": 0,
            },
        }

    def _ensure_genome_compatibility(self):
        """Ensure existing genome has all required fields"""
        # Ensure experience_bank has insights_discovered
        if "experience_bank" not in self.genome:
            self.genome["experience_bank"] = {
                "patterns_known": [],
                "techniques_mastered": [],
                "pitfalls_remembered": [],
                "insights_discovered": [],
            }

        if "insights_discovered" not in self.genome.get("experience_bank", {}):
            self.genome["experience_bank"]["insights_discovered"] = []

        # Ensure evolution_metrics has total_learning_events
        if "evolution_metrics" not in self.genome:
            self.genome["evolution_metrics"] = {
                "tasks_completed": 0,
                "patterns_created": 0,
                "learning_velocity": "developing",
                "total_learning_events": 0,
            }

        if "total_learning_events" not in self.genome.get("evolution_metrics", {}):
            self.genome["evolution_metrics"]["total_learning_events"] = 0

        # Ensure agent_metadata has last_active
        if "agent_metadata" not in self.genome:
            self.genome["agent_metadata"] = {
                "agent_id": self.agent_id,
                "created_date": datetime.now().isoformat(),
                "total_sessions": 0,
                "last_active": datetime.now().isoformat(),
            }

        if "last_active" not in self.genome.get("agent_metadata", {}):
            self.genome["agent_metadata"]["last_active"] = datetime.now().isoformat()

    def learn(self, category, content, metadata=None):
        """Automatically capture a learning event"""
        timestamp = datetime.now().isoformat()

        learning_event = {
            "timestamp": timestamp,
            "category": category,
            "content": content,
            "metadata": metadata or {},
        }

        # Add to appropriate DNA section
        if category == "pattern":
            pattern_obj = {
                "name": (
                    content
                    if isinstance(content, str)
                    else content.get("name", "unknown")
                ),
                "description": metadata.get("description", "") if metadata else "",
                "timestamp": timestamp,
            }

            # Check if pattern already exists
            existing_names = [
                p.get("name", "") if isinstance(p, dict) else p
                for p in self.genome["experience_bank"]["patterns_known"]
            ]

            pattern_name = pattern_obj["name"]
            if pattern_name not in existing_names:
                self.genome["experience_bank"]["patterns_known"].append(pattern_obj)
                self.genome["evolution_metrics"]["patterns_created"] += 1

        elif category == "insight":
            self.genome["experience_bank"]["insights_discovered"].append(
                {
                    "insight": content,
                    "timestamp": timestamp,
                    "context": metadata.get("context", "") if metadata else "",
                }
            )

        # Update metrics
        self.genome["evolution_metrics"]["total_learning_events"] += 1
        self.genome["agent_metadata"]["last_active"] = timestamp

        # Log to session
        self.session_log.append(learning_event)

        # Auto-save if enabled
        if self.auto_save_enabled:
            self.save()

        print(
            f"🧬 Agent DNA Updated: [{category}] {content if isinstance(content, str) else content.get('name', 'Unknown')}"
        )

    def task_completed(self, task_description):
        """Record task completion"""
        self.genome["evolution_metrics"]["tasks_completed"] += 1
        self.learn(
            "insight", f"Completed: {task_description}", {"type": "task_completion"}
        )

    def save(self):
        """Save DNA to disk"""
        self.dna_dir.mkdir(parents=True, exist_ok=True)

        with open(self.genome_file, "w") as f:
            json.dump(self.genome, f, indent=2)

    def commit_session(self, summary):
        """Commit session changes"""
        self.genome["agent_metadata"]["total_sessions"] += 1
        self.genome["session_memory"]["last_session_summary"] = summary

        # Save session log
        session_file = (
            self.dna_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(session_file, "w") as f:
            json.dump(
                {
                    "summary": summary,
                    "learning_events": self.session_log,
                    "timestamp": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

        self.save()
        print(f"✓ Session committed: {len(self.session_log)} learning events captured")
        self.session_log = []


# Global DNA instances
_agent_dna_cache = {}


def get_agent_dna(agent_id):
    """Get or create agent DNA instance"""
    if agent_id not in _agent_dna_cache:
        _agent_dna_cache[agent_id] = AgentDNA(agent_id)
    return _agent_dna_cache[agent_id]


# ============================================
# SELF-AUDIT INTEGRATION
# ============================================


def enable_self_awareness():
    """Enable self-audit capabilities for all agents"""
    try:
        from self_audit import add_self_audit_to_agent

        add_self_audit_to_agent()
    except ImportError:
        pass  # self_audit.py not available yet


# Enable self-awareness on module load
enable_self_awareness()
