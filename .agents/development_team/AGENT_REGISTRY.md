# CrisisKit Agent Registry

## Active Agents
- **PM Agent**: Project coordination and oversight
- **Security Agent**: Security auditing and fixes
- **Testing Agent**: QA and functionality testing
- **Performance Agent**: Optimization analysis
- **Code Quality Agent**: Bug fixes and refactoring
- **Deployment Agent**: Configuration and deployment validation

## Coordination Protocol
1. Each agent reads from `.agents/tasks/[agent-name]-tasks.json`
2. Each agent writes to `.agents/reports/[agent-name]-report.json`
3. Each agent updates `.agents/status/[agent-name]-status.json`
4. Shared memory accessible via MCP memory server
5. PM Agent orchestrates via task assignments
