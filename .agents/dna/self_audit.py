"""
Embedded Self-Audit System
Gives agents self-awareness and tracks improvement toward excellence
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import statistics


class SelfAudit:
    """
    Agent self-awareness and improvement tracking

    Agents use this to:
    - Understand their own growth
    - Identify knowledge gaps
    - Set improvement goals
    - Track progress toward excellence
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.genome_path = Path(f".agents/dna/{agent_id}/genome.json")

        if not self.genome_path.exists():
            raise FileNotFoundError(
                f"Agent {agent_id} has no DNA yet. Initialize first."
            )

        with open(self.genome_path, "r") as f:
            self.genome = json.load(f)

    def analyze_growth(self) -> Dict:
        """
        Deep analysis of agent's growth and learning

        Returns comprehensive self-assessment
        """

        metrics = self.genome["evolution_metrics"]
        experience = self.genome["experience_bank"]
        skills = self.genome["skills"]["technical"]

        # Calculate growth metrics
        total_learning = metrics.get("total_learning_events", 0)
        sessions = self.genome["agent_metadata"].get("total_sessions", 0)
        tasks = metrics.get("tasks_completed", 0)

        learning_rate = total_learning / max(sessions, 1)
        task_rate = tasks / max(sessions, 1)

        # Knowledge depth
        insights = len(experience.get("insights_gained", []))
        patterns = len(experience.get("patterns_known", []))
        techniques = len(experience.get("techniques_mastered", []))

        knowledge_depth = insights + patterns + techniques
        knowledge_diversity = len(
            set(
                [
                    "insights" if insights > 0 else None,
                    "patterns" if patterns > 0 else None,
                    "techniques" if techniques > 0 else None,
                ]
            )
            - {None}
        )

        # Skill mastery
        skill_count = len(skills)
        avg_skill_level = (
            statistics.mean(
                [
                    s.get("level", 1) if isinstance(s, dict) else 1
                    for s in skills.values()
                ]
            )
            if skills
            else 0
        )

        max_skill_level = (
            max(
                [
                    s.get("level", 1) if isinstance(s, dict) else 1
                    for s in skills.values()
                ]
            )
            if skills
            else 0
        )

        return {
            "learning_velocity": learning_rate,
            "task_completion_rate": task_rate,
            "knowledge_depth": knowledge_depth,
            "knowledge_diversity": knowledge_diversity,
            "skill_count": skill_count,
            "avg_skill_level": avg_skill_level,
            "max_skill_level": max_skill_level,
            "total_learning_events": total_learning,
            "sessions": sessions,
            "tasks": tasks,
        }

    def calculate_excellence_score(self) -> Tuple[float, str]:
        """
        Calculate how close agent is to excellence

        Returns:
            (score, rating) where score is 0-100
        """

        growth = self.analyze_growth()

        score = 0
        max_score = 100

        # Learning velocity (0-20 points)
        if growth["learning_velocity"] >= 10:
            score += 20
        elif growth["learning_velocity"] >= 7:
            score += 15
        elif growth["learning_velocity"] >= 5:
            score += 10
        elif growth["learning_velocity"] >= 3:
            score += 5

        # Knowledge depth (0-20 points)
        if growth["knowledge_depth"] >= 50:
            score += 20
        elif growth["knowledge_depth"] >= 30:
            score += 15
        elif growth["knowledge_depth"] >= 15:
            score += 10
        elif growth["knowledge_depth"] >= 5:
            score += 5

        # Knowledge diversity (0-15 points)
        if growth["knowledge_diversity"] == 3:
            score += 15
        elif growth["knowledge_diversity"] == 2:
            score += 10
        elif growth["knowledge_diversity"] == 1:
            score += 5

        # Skill development (0-25 points)
        if growth["skill_count"] >= 5 and growth["avg_skill_level"] >= 5:
            score += 25
        elif growth["skill_count"] >= 3 and growth["avg_skill_level"] >= 4:
            score += 20
        elif growth["skill_count"] >= 2 and growth["avg_skill_level"] >= 3:
            score += 15
        elif growth["skill_count"] >= 1:
            score += 10

        # Productivity (0-20 points)
        if growth["task_completion_rate"] >= 5:
            score += 20
        elif growth["task_completion_rate"] >= 3:
            score += 15
        elif growth["task_completion_rate"] >= 2:
            score += 10
        elif growth["task_completion_rate"] >= 1:
            score += 5

        # Determine rating
        if score >= 85:
            rating = "WORLD-CLASS"
        elif score >= 70:
            rating = "EXCELLENT"
        elif score >= 55:
            rating = "PROFICIENT"
        elif score >= 40:
            rating = "DEVELOPING"
        elif score >= 25:
            rating = "LEARNING"
        else:
            rating = "NOVICE"

        return score, rating

    def identify_gaps(self) -> List[str]:
        """
        Identify specific areas for improvement

        Returns list of actionable improvement areas
        """

        growth = self.analyze_growth()
        gaps = []

        # Learning velocity gap
        if growth["learning_velocity"] < 5:
            gaps.append(
                f"Low learning rate ({growth['learning_velocity']:.1f}/session). Need more agent.learn() calls."
            )

        # Knowledge gaps
        experience = self.genome["experience_bank"]
        insights = len(experience.get("insights_gained", []))
        patterns = len(experience.get("patterns_known", []))
        techniques = len(experience.get("techniques_mastered", []))

        if insights < 5:
            gaps.append(
                f"Few insights ({insights}). Need deeper understanding of 'why' things work."
            )

        if patterns < 5:
            gaps.append(
                f"Few patterns ({patterns}). Need to recognize recurring structures."
            )

        if techniques < 5:
            gaps.append(
                f"Few techniques ({techniques}). Need more practical 'how-to' knowledge."
            )

        # Skill gaps
        if growth["skill_count"] < 3:
            gaps.append(
                f"Limited skills ({growth['skill_count']}). Need to develop more competencies."
            )

        if growth["avg_skill_level"] < 4:
            gaps.append(
                f"Low skill mastery (avg level {growth['avg_skill_level']:.1f}). Need to deepen expertise."
            )

        # Productivity gaps
        if growth["task_completion_rate"] < 2:
            gaps.append(
                f"Low productivity ({growth['tasks']} tasks in {growth['sessions']} sessions)."
            )

        # Session consistency
        if growth["sessions"] < 3:
            gaps.append(
                f"Too few sessions ({growth['sessions']}). Need consistent practice."
            )

        return gaps

    def set_improvement_goals(self) -> List[Dict]:
        """
        Generate specific, measurable improvement goals

        Returns list of SMART goals
        """

        growth = self.analyze_growth()
        goals = []

        # Goal 1: Learning velocity
        target_learning_rate = max(10, growth["learning_velocity"] * 1.5)
        goals.append(
            {
                "area": "Learning Velocity",
                "current": growth["learning_velocity"],
                "target": target_learning_rate,
                "action": "Call agent.learn() more frequently during tasks",
                "metric": "events per session",
            }
        )

        # Goal 2: Knowledge depth
        target_knowledge = max(30, growth["knowledge_depth"] * 1.5)
        goals.append(
            {
                "area": "Knowledge Depth",
                "current": growth["knowledge_depth"],
                "target": target_knowledge,
                "action": "Learn insights, patterns, and techniques for each task",
                "metric": "total knowledge items",
            }
        )

        # Goal 3: Skill mastery
        target_skills = max(5, growth["skill_count"] + 2)
        target_level = min(7, growth["avg_skill_level"] + 1)
        goals.append(
            {
                "area": "Skill Mastery",
                "current": f"{growth['skill_count']} skills @ level {growth['avg_skill_level']:.1f}",
                "target": f"{target_skills} skills @ level {target_level}",
                "action": "Develop new skills and increase proficiency in existing ones",
                "metric": "skill count and average level",
            }
        )

        # Goal 4: Task productivity
        target_tasks = max(5, growth["task_completion_rate"] * 1.5)
        goals.append(
            {
                "area": "Productivity",
                "current": growth["task_completion_rate"],
                "target": target_tasks,
                "action": "Complete more tasks per session with agent.task_completed()",
                "metric": "tasks per session",
            }
        )

        return goals

    def generate_improvement_plan(self) -> str:
        """
        Generate complete self-improvement plan

        Returns formatted improvement plan
        """

        score, rating = self.calculate_excellence_score()
        growth = self.analyze_growth()
        gaps = self.identify_gaps()
        goals = self.set_improvement_goals()

        plan = []
        plan.append("=" * 70)
        plan.append(f"SELF-IMPROVEMENT PLAN: {self.agent_id}")
        plan.append("=" * 70)
        plan.append("")

        # Current state
        plan.append("📊 CURRENT STATE:")
        plan.append(f"   Excellence Score: {score}/100 ({rating})")
        plan.append(
            f"   Learning Velocity: {growth['learning_velocity']:.1f} events/session"
        )
        plan.append(f"   Knowledge Depth: {growth['knowledge_depth']} items")
        plan.append(
            f"   Skills: {growth['skill_count']} @ avg level {growth['avg_skill_level']:.1f}"
        )
        plan.append(
            f"   Productivity: {growth['task_completion_rate']:.1f} tasks/session"
        )
        plan.append(f"   Total Sessions: {growth['sessions']}")
        plan.append("")

        # Path to excellence
        points_to_excellence = max(0, 85 - score)
        plan.append("🎯 PATH TO EXCELLENCE:")
        if rating == "WORLD-CLASS":
            plan.append("   ✅ Already world-class! Focus on maintaining excellence.")
        elif rating == "EXCELLENT":
            plan.append(
                f"   Need {points_to_excellence} more points to reach world-class"
            )
        else:
            plan.append(
                f"   Need {points_to_excellence} more points to reach excellence (85+)"
            )
        plan.append("")

        # Knowledge gaps
        if gaps:
            plan.append("⚠️  IDENTIFIED GAPS:")
            for i, gap in enumerate(gaps, 1):
                plan.append(f"   {i}. {gap}")
            plan.append("")

        # Improvement goals
        plan.append("🚀 IMPROVEMENT GOALS:")
        for i, goal in enumerate(goals, 1):
            plan.append(f"   Goal {i}: {goal['area']}")
            plan.append(f"      Current: {goal['current']}")
            plan.append(f"      Target: {goal['target']}")
            plan.append(f"      Action: {goal['action']}")
            plan.append("")

        # Specific actions
        plan.append("📋 IMMEDIATE ACTIONS FOR NEXT SESSION:")
        plan.append("   1. At session start:")
        plan.append("      agent = get_agent_dna('my-agent-id')")
        plan.append("      audit = agent.self_audit()")
        plan.append("")
        plan.append("   2. During work:")
        plan.append("      agent.learn('insight', 'why this works...')")
        plan.append("      agent.learn('pattern', 'recurring structure...')")
        plan.append("      agent.learn('technique', 'how to do this...')")
        plan.append("      agent.task_completed('specific task name')")
        plan.append("")
        plan.append("   3. At session end:")
        plan.append("      agent.commit_session('what I accomplished')")
        plan.append("")

        # Motivation
        plan.append("💪 GROWTH MINDSET:")
        if growth["sessions"] > 0:
            improvement = (score / growth["sessions"]) if growth["sessions"] > 0 else 0
            plan.append(f"   You're improving at ~{improvement:.1f} points per session")
            sessions_to_excellence = max(0, points_to_excellence / max(improvement, 1))
            if sessions_to_excellence > 0 and sessions_to_excellence < 100:
                plan.append(
                    f"   At this rate, you'll reach excellence in ~{sessions_to_excellence:.0f} sessions"
                )
        plan.append(f"   Every session is an opportunity to grow")
        plan.append(f"   Consistent learning compounds over time")
        plan.append("")

        plan.append("=" * 70)

        return "\n".join(plan)

    def track_progress(self) -> Dict:
        """
        Track progress over time

        Returns historical progression data
        """

        # For now, return current snapshot
        # In future, could track historical scores

        score, rating = self.calculate_excellence_score()
        growth = self.analyze_growth()

        return {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "rating": rating,
            "learning_velocity": growth["learning_velocity"],
            "knowledge_depth": growth["knowledge_depth"],
            "skill_count": growth["skill_count"],
            "avg_skill_level": growth["avg_skill_level"],
        }


def run_self_audit(agent_id: str):
    """
    Convenience function to run full self-audit

    Usage:
        from self_audit import run_self_audit
        run_self_audit('backend-developer-agent')
    """

    try:
        audit = SelfAudit(agent_id)
        plan = audit.generate_improvement_plan()
        print(plan)

        return audit

    except FileNotFoundError:
        print(f"❌ Agent '{agent_id}' not found. Initialize agent first:")
        print(f"   from auto_learn import get_agent_dna")
        print(f"   agent = get_agent_dna('{agent_id}')")
        return None


# Make self_audit easily accessible from AgentDNA
def add_self_audit_to_agent():
    """Patch AgentDNA class to include self_audit method"""

    from auto_learn import AgentDNA

    def self_audit(self):
        """Run self-audit and get improvement plan"""
        audit = SelfAudit(self.agent_id)
        return audit

    AgentDNA.self_audit = self_audit


# Auto-patch on import
add_self_audit_to_agent()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
        run_self_audit(agent_id)
    else:
        print("Usage: python self_audit.py <agent-id>")
        print("Example: python self_audit.py backend-developer-agent")
