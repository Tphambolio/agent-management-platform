#!/usr/bin/env python3
"""
Agent DNA Evolution Report Generator
Alternative to evolution-report.sh that doesn't require jq
"""
import json
import sys
from pathlib import Path


def generate_evolution_report(agent_id: str):
    """Generate comprehensive evolution report for an agent."""

    dna_file = Path(f".agents/dna/{agent_id}/genome.json")

    if not dna_file.exists():
        print(f"⚠️  DNA not found for {agent_id}")
        sys.exit(1)

    # Load genome
    with open(dna_file, "r") as f:
        genome = json.load(f)

    # Header
    print("╔════════════════════════════════════════════════════════════════╗")
    print(f"║        🧬 AGENT EVOLUTION REPORT: {agent_id:<29}║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Basic metrics
    metadata = genome.get("agent_metadata", {})
    print(f"Sessions completed: {metadata.get('total_sessions', 0)}")
    print(f"Role: {metadata.get('role', 'N/A')}")
    print(f"Created: {metadata.get('created_date', 'N/A')}")
    print()

    # Skills
    skills = genome.get("skills", {})
    technical_skills = skills.get("technical", {})
    domain_skills = skills.get("domain", {})
    total_skills = len(technical_skills) + len(domain_skills)

    print(f"Total Skills: {total_skills}")
    print(f"  - Technical: {len(technical_skills)}")
    print(f"  - Domain: {len(domain_skills)}")
    print()

    if technical_skills:
        print("Technical Skills:")
        for skill_name, skill_data in technical_skills.items():
            level = skill_data.get("level", 0)
            prof = skill_data.get("proficiency", "unknown")
            print(f"  • {skill_name}: Level {level} ({prof.upper()})")
        print()

    if domain_skills:
        print("Domain Knowledge:")
        for skill_name, skill_data in domain_skills.items():
            level = skill_data.get("level", 0)
            prof = skill_data.get("proficiency", "unknown")
            print(f"  • {skill_name}: Level {level} ({prof.upper()})")
        print()

    # Experience bank
    exp_bank = genome.get("experience_bank", {})
    patterns = exp_bank.get("patterns_known", [])
    techniques = exp_bank.get("techniques_mastered", [])
    pitfalls = exp_bank.get("pitfalls_remembered", [])

    print(f"Experience Bank:")
    print(f"  - Patterns Known: {len(patterns)}")
    print(f"  - Techniques Mastered: {len(techniques)}")
    print(f"  - Pitfalls Remembered: {len(pitfalls)}")
    print()

    # Evolution metrics
    metrics = genome.get("evolution_metrics", {})
    print(f"Evolution Metrics:")
    print(f"  - Learning Velocity: {metrics.get('learning_velocity', 'N/A').upper()}")
    print(f"  - Tasks Completed: {metrics.get('tasks_completed', 0)}")
    print(f"  - Patterns Created: {metrics.get('patterns_created', len(patterns))}")
    print()

    # Performance impact
    perf_impact = metrics.get("performance_impact", {})
    if perf_impact:
        print("Performance Impact:")
        for key, value in perf_impact.items():
            print(f"  - {key}: {value}")
        print()

    # Session history
    history = metadata.get("session_history", [])
    if history:
        print("Session History:")
        for session in history:
            sess_num = session.get("session", 0)
            date = session.get("date", "N/A")
            summary = session.get("summary", "N/A")
            tasks = session.get("tasks_completed", 0)
            print(f"  Session {sess_num} ({date}):")
            print(f"    Summary: {summary}")
            print(f"    Tasks: {tasks}")
        print()

    # Next priorities
    session_mem = genome.get("session_memory", {})
    priorities = session_mem.get("next_priorities", [])
    if priorities:
        print("Next Priorities:")
        for i, priority in enumerate(priorities, 1):
            print(f"  {i}. {priority}")
        print()

    # Footer
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              ✅ EVOLUTION REPORT COMPLETE                      ║")
    print("╚════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: evolution-report.py <agent_id>")
        sys.exit(1)

    generate_evolution_report(sys.argv[1])
