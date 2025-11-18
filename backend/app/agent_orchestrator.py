"""
Stub for agent_orchestrator to satisfy imports.
The actual orchestration functionality is not needed for the counter-style UI endpoints.
"""

class AgentOrchestrator:
    """Simple stub class for agent orchestrator"""

    def __init__(self):
        self.enabled = False

    async def execute_task(self, *args, **kwargs):
        """Stub method - not implemented"""
        raise NotImplementedError("MCP orchestrator not available in standalone deployment")


# Create singleton instance
agent_orchestrator = AgentOrchestrator()
