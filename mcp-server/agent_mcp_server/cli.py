"""CLI tool for Agent Management Platform MCP Server"""
import argparse
import sys
from pathlib import Path

from .database import init_db, get_db
from .models import Agent, Task, Report, Project
from .agent_executor import AgentExecutor


def cmd_init(args):
    """Initialize database"""
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")


def cmd_sync(args):
    """Sync agents from filesystem to database"""
    print("Syncing agents from filesystem...")
    executor = AgentExecutor(args.agents_dir)
    executor.sync_agents_to_db()
    print("✓ Agents synced")

    # Show synced agents
    with get_db() as db:
        agents = db.query(Agent).all()
        print(f"\nTotal agents: {len(agents)}")
        for agent in agents:
            print(f"  - {agent.name} ({agent.type}) - {agent.status.value}")


def cmd_list_agents(args):
    """List all agents"""
    with get_db() as db:
        agents = db.query(Agent).all()

        if not agents:
            print("No agents found. Run 'sync' first.")
            return

        print(f"\nTotal agents: {len(agents)}\n")
        print(f"{'Name':<30} {'Type':<15} {'Status':<10} {'Specialization'}")
        print("-" * 80)

        for agent in agents:
            print(f"{agent.name:<30} {agent.type:<15} {agent.status.value:<10} {agent.specialization}")


def cmd_list_tasks(args):
    """List all tasks"""
    with get_db() as db:
        query = db.query(Task)

        if args.agent:
            agent = db.query(Agent).filter(Agent.name == args.agent).first()
            if agent:
                query = query.filter(Task.agent_id == agent.id)

        if args.project:
            query = query.filter(Task.project_id == args.project)

        if args.status:
            query = query.filter(Task.status == args.status)

        tasks = query.order_by(Task.created_at.desc()).limit(50).all()

        if not tasks:
            print("No tasks found.")
            return

        print(f"\nTotal tasks: {len(tasks)}\n")
        print(f"{'ID':<12} {'Agent':<20} {'Title':<30} {'Status':<12}")
        print("-" * 80)

        for task in tasks:
            print(f"{task.id[:8]}... {task.agent_id[:16]:<20} {task.title[:28]:<30} {task.status.value:<12}")


def cmd_list_reports(args):
    """List all reports"""
    with get_db() as db:
        query = db.query(Report)

        if args.project:
            query = query.filter(Report.project_id == args.project)

        reports = query.order_by(Report.created_at.desc()).limit(50).all()

        if not reports:
            print("No reports found.")
            return

        print(f"\nTotal reports: {len(reports)}\n")
        print(f"{'ID':<12} {'Agent':<20} {'Title':<40}")
        print("-" * 80)

        for report in reports:
            print(f"{report.id[:8]}... {report.agent_id[:16]:<20} {report.title[:38]:<40}")


def cmd_create_project(args):
    """Create a new project"""
    import uuid
    with get_db() as db:
        project = Project(
            id=str(uuid.uuid4()),
            name=args.name,
            description=args.description or "",
            repository_path=args.repo_path
        )
        db.add(project)
        db.commit()
        print(f"✓ Created project: {args.name} ({project.id})")


def cmd_list_projects(args):
    """List all projects"""
    with get_db() as db:
        projects = db.query(Project).all()

        if not projects:
            print("No projects found.")
            return

        print(f"\nTotal projects: {len(projects)}\n")
        print(f"{'Name':<30} {'Repository Path':<50}")
        print("-" * 85)

        for project in projects:
            print(f"{project.name:<30} {project.repository_path or 'N/A':<50}")


def cmd_status(args):
    """Show system status"""
    with get_db() as db:
        agents = db.query(Agent).all()
        tasks = db.query(Task).all()
        reports = db.query(Report).all()
        projects = db.query(Project).all()

        print("\n=== Agent Management Platform Status ===\n")
        print(f"Agents:   {len(agents)}")
        print(f"Tasks:    {len(tasks)}")
        print(f"Reports:  {len(reports)}")
        print(f"Projects: {len(projects)}")
        print()

        # Agent status breakdown
        from collections import Counter
        status_counts = Counter(agent.status.value for agent in agents)
        print("Agent Status:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        print()

        # Task status breakdown
        task_status_counts = Counter(task.status.value for task in tasks)
        print("Task Status:")
        for status, count in task_status_counts.items():
            print(f"  {status}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Management Platform CLI"
    )
    parser.add_argument(
        "--agents-dir",
        default="/home/rpas/wildfire-simulator-v2/.agents",
        help="Path to agents directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    parser_init = subparsers.add_parser("init", help="Initialize database")
    parser_init.set_defaults(func=cmd_init)

    # sync command
    parser_sync = subparsers.add_parser("sync", help="Sync agents from filesystem")
    parser_sync.set_defaults(func=cmd_sync)

    # list-agents command
    parser_list_agents = subparsers.add_parser("list-agents", help="List all agents")
    parser_list_agents.set_defaults(func=cmd_list_agents)

    # list-tasks command
    parser_list_tasks = subparsers.add_parser("list-tasks", help="List tasks")
    parser_list_tasks.add_argument("--agent", help="Filter by agent name")
    parser_list_tasks.add_argument("--project", help="Filter by project ID")
    parser_list_tasks.add_argument("--status", help="Filter by status")
    parser_list_tasks.set_defaults(func=cmd_list_tasks)

    # list-reports command
    parser_list_reports = subparsers.add_parser("list-reports", help="List reports")
    parser_list_reports.add_argument("--project", help="Filter by project ID")
    parser_list_reports.set_defaults(func=cmd_list_reports)

    # create-project command
    parser_create_project = subparsers.add_parser("create-project", help="Create a new project")
    parser_create_project.add_argument("name", help="Project name")
    parser_create_project.add_argument("--description", help="Project description")
    parser_create_project.add_argument("--repo-path", help="Repository path")
    parser_create_project.set_defaults(func=cmd_create_project)

    # list-projects command
    parser_list_projects = subparsers.add_parser("list-projects", help="List projects")
    parser_list_projects.set_defaults(func=cmd_list_projects)

    # status command
    parser_status = subparsers.add_parser("status", help="Show system status")
    parser_status.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
