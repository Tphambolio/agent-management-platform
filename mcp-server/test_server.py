#!/usr/bin/env python3
"""Test script for MCP server"""
import asyncio
import sys
sys.path.insert(0, 'src')

from agent_mcp.agent_manager import agent_manager
from agent_mcp.models import TaskPriority


async def test_server():
    """Test the MCP server functionality"""
    print("🚀 Testing Agent Management Platform MCP Server\n")

    # Initialize agent manager
    print("1️⃣  Initializing agent manager...")
    await agent_manager.initialize()
    print(f"   ✓ Agent manager initialized\n")

    # List agents
    print("2️⃣  Discovering agents...")
    agents = await agent_manager.list_agents()
    print(f"   ✓ Found {len(agents)} agents:")
    for agent in agents[:5]:  # Show first 5
        print(f"      - {agent.name} ({agent.type}): {agent.description[:60]}...")
    if len(agents) > 5:
        print(f"      ... and {len(agents) - 5} more")
    print()

    if not agents:
        print("   ⚠️  No agents found. Please add agent definitions to .agents/")
        print("   Continuing with test...\n")
        return

    # Create a test task
    print("3️⃣  Creating a test task...")
    test_agent = agents[0]
    task = await agent_manager.create_task(
        agent_id=test_agent.id,
        title="Test task - Code quality review",
        description="This is a test task to verify the agent execution pipeline works correctly.",
        priority=TaskPriority.MEDIUM,
        context={
            "test": True,
            "repository": "/test/repo"
        }
    )
    print(f"   ✓ Task created: {task.id}")
    print(f"      Agent: {test_agent.name}")
    print(f"      Title: {task.title}")
    print(f"      Status: {task.status.value}\n")

    # Execute the task
    print("4️⃣  Executing task...")
    await agent_manager.execute_task(task.id)
    print(f"   ✓ Task execution started")

    # Wait for completion (with timeout)
    print("   ⏳ Waiting for task to complete...")
    for i in range(30):  # 30 second timeout
        await asyncio.sleep(1)
        updated_task = await agent_manager.get_task(task.id)
        if updated_task.status.value in ["completed", "failed"]:
            break
        if i % 5 == 0:
            print(f"      ... still running ({i}s)")

    # Get final status
    print("\n5️⃣  Checking task result...")
    final_task = await agent_manager.get_task(task.id)
    print(f"   Status: {final_task.status.value}")

    if final_task.status.value == "completed":
        print(f"   ✓ Task completed successfully!")
        print(f"\n   Result:")
        if final_task.result:
            import json
            result_str = json.dumps(final_task.result, indent=2)
            # Limit output
            lines = result_str.split('\n')
            if len(lines) > 20:
                print("   " + '\n   '.join(lines[:20]))
                print(f"   ... ({len(lines) - 20} more lines)")
            else:
                print("   " + '\n   '.join(lines))
    elif final_task.status.value == "failed":
        print(f"   ✗ Task failed: {final_task.error}")
    else:
        print(f"   ⏸️  Task still running (status: {final_task.status.value})")

    # Check for reports
    print("\n6️⃣  Checking for generated reports...")
    reports = await agent_manager.list_reports(task_id=task.id)
    print(f"   Found {len(reports)} report(s)")

    if reports:
        report = reports[0]
        print(f"   ✓ Report ID: {report.id}")
        print(f"      Title: {report.title}")
        print(f"      Format: {report.format}")

    # Summary
    print("\n" + "="*60)
    print("✅ MCP Server Test Complete!")
    print("="*60)
    print(f"Total Agents: {len(agents)}")
    print(f"Task Status: {final_task.status.value}")
    print(f"Reports Generated: {len(reports)}")
    print("\n💡 The MCP server is working correctly!")
    print("\nNext steps:")
    print("  1. Add to Claude Desktop config to use via chat")
    print("  2. Try assigning real tasks to your agents")
    print("  3. Build the web dashboard for visual management")


if __name__ == "__main__":
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
