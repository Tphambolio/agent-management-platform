#!/usr/bin/env python3
"""
Agent DNA Commit Tool
Commits session to DNA genome - alternative to commit-dna.sh without jq dependency
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def commit_dna(agent_id: str, summary: str):
    """Commit a new session to the agent's DNA."""

    dna_file = Path(f".agents/dna/{agent_id}/genome.json")

    if not dna_file.exists():
        print(f"⚠️  DNA not found for {agent_id}")
        sys.exit(1)

    # Load genome
    with open(dna_file, "r") as f:
        genome = json.load(f)

    # Update metadata
    genome["agent_metadata"]["total_sessions"] += 1
    genome["session_memory"]["last_session_summary"] = summary

    # Save updated genome
    with open(dna_file, "w", encoding="utf-8") as f:
        json.dump(genome, f, indent=2, ensure_ascii=True)

    print(f"✓ DNA committed for {agent_id}")
    print(f"  Summary: {summary}")
    print(f"  Total sessions: {genome['agent_metadata']['total_sessions']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: commit-dna.py <agent_id> <summary>")
        sys.exit(1)

    commit_dna(sys.argv[1], sys.argv[2])
