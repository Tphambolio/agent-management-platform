# Agent Management Platform - Design Document

**Version**: 1.0
**Date**: 2025-11-07
**Status**: Design Phase

---

## Executive Summary

Build a professional **Agent Management Platform** (AMP) - a full-stack application that provides a graphical interface for managing, monitoring, and coordinating AI agents across multiple projects. Think of it as "GitHub Actions meets Jira meets Datadog" for AI agents.

## Goals

1. **Visual Agent Management**: Graphical dashboard to monitor agent status, assign tasks, view reports
2. **Project Agnostic**: Agents can work on any codebase, not just wildfire simulator
3. **Human-Friendly Reports**: Beautiful, interactive report rendering with syntax highlighting, charts, and navigation
4. **Professional Interface**: Modern web app with real-time updates, filtering, search
5. **Extensible**: Easy to add new agents, report types, and project configurations

---

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                        │
│  (React/Next.js + TailwindCSS + shadcn/ui)                  │
│                                                              │
│  - Agent Status Cards    - Report Viewer                    │
│  - Task Assignment       - Project Switcher                 │
│  - Live Logs             - Metrics & Charts                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API + WebSocket
┌──────────────────▼──────────────────────────────────────────┐
│                    Backend API Server                        │
│           (FastAPI + SQLAlchemy + Redis)                    │
│                                                              │
│  - Agent Orchestrator    - Task Queue                       │
│  - Report Aggregator     - WebSocket Manager                │
│  - Project Manager       - Authentication                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ Agent Protocol (JSON-RPC style)
┌──────────────────▼──────────────────────────────────────────┐
│                    Agent Runtime Layer                       │
│                                                              │
│  - Agent Wrapper (Python/Node/Go)                           │
│  - Task Executor                                            │
│  - Report Generator                                         │
│  - DNA Evolution System                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │ File System / Git
┌──────────────────▼──────────────────────────────────────────┐
│                    Target Projects                           │
│                                                              │
│  - wildfire-simulator-v2                                    │
│  - any-other-project                                        │
│  - customer-project-x                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack Recommendation

### Backend
- **Framework**: FastAPI (Python)
  - Async support for WebSockets
  - Automatic OpenAPI docs
  - Fast, modern Python framework

- **Database**: PostgreSQL
  - JSON support for flexible report storage
  - Full-text search for logs and reports
  - Production-ready scalability

- **Task Queue**: Redis + Celery
  - Async agent task execution
  - Retry mechanisms
  - Priority queues

- **Real-time**: WebSocket (FastAPI native)
  - Live agent status updates
  - Streaming logs
  - Progress notifications

### Frontend
- **Framework**: Next.js 15 + React 19
  - Server-side rendering for fast loads
  - Already used in your project
  - Great developer experience

- **UI Components**: shadcn/ui + TailwindCSS
  - Beautiful, accessible components
  - Customizable design system
  - Modern, professional look

- **State Management**: Zustand or React Query
  - Simple, performant state management
  - Built-in caching for API calls

- **Charts**: Recharts or Chart.js
  - Agent performance metrics
  - Report visualizations
  - Timeline views

- **Code Display**: Monaco Editor or Prism
  - Syntax-highlighted code in reports
  - Diff viewer for changes
  - File tree navigation

---

## Database Schema

### Tables

```sql
-- Projects that agents can work on
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  git_url TEXT,
  local_path TEXT NOT NULL,
  description TEXT,
  agent_config JSONB, -- Project-specific agent settings
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Registered agents
CREATE TABLE agents (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  type VARCHAR(50) NOT NULL, -- 'domain', 'dev-team', 'coordination'
  expertise TEXT[], -- ['fbp', 'fire-science', 'python']
  status VARCHAR(20) DEFAULT 'idle', -- idle, running, error, stopped
  current_task_id UUID REFERENCES tasks(id),
  config JSONB,
  dna_path TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_active_at TIMESTAMP
);

-- Task queue and history
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  agent_id UUID REFERENCES agents(id),
  title VARCHAR(500) NOT NULL,
  description TEXT,
  task_type VARCHAR(50), -- 'review', 'fix', 'analyze', 'optimize', 'test'
  priority INTEGER DEFAULT 5, -- 1-10
  status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
  input_data JSONB,
  output_data JSONB,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(255) -- user who created task
);

-- Agent execution logs
CREATE TABLE agent_logs (
  id BIGSERIAL PRIMARY KEY,
  agent_id UUID REFERENCES agents(id),
  task_id UUID REFERENCES tasks(id),
  level VARCHAR(20), -- debug, info, warning, error
  message TEXT,
  metadata JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Generated reports
CREATE TABLE reports (
  id UUID PRIMARY KEY,
  task_id UUID REFERENCES tasks(id) NOT NULL,
  agent_id UUID REFERENCES agents(id) NOT NULL,
  project_id UUID REFERENCES projects(id) NOT NULL,
  report_type VARCHAR(100), -- 'performance', 'security', 'code-review', etc.
  title VARCHAR(500),
  summary TEXT,
  content JSONB NOT NULL, -- Full report data
  format VARCHAR(20) DEFAULT 'json', -- json, markdown, html
  file_path TEXT, -- Path to report file if saved
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent performance metrics
CREATE TABLE agent_metrics (
  id BIGSERIAL PRIMARY KEY,
  agent_id UUID REFERENCES agents(id),
  task_id UUID REFERENCES tasks(id),
  execution_time_seconds FLOAT,
  memory_usage_mb FLOAT,
  cpu_usage_percent FLOAT,
  exit_code INTEGER,
  errors_count INTEGER DEFAULT 0,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Agent Management

```
GET    /api/agents                     # List all agents
GET    /api/agents/:id                 # Get agent details
POST   /api/agents/:id/start           # Start an agent
POST   /api/agents/:id/stop            # Stop an agent
GET    /api/agents/:id/status          # Get current status
GET    /api/agents/:id/logs            # Get agent logs (paginated)
```

### Task Management

```
POST   /api/tasks                      # Create new task
GET    /api/tasks                      # List tasks (filter by status, agent, project)
GET    /api/tasks/:id                  # Get task details
PUT    /api/tasks/:id                  # Update task
DELETE /api/tasks/:id                  # Cancel/delete task
POST   /api/tasks/:id/assign           # Assign task to agent
GET    /api/tasks/:id/logs             # Get task execution logs
```

### Reports

```
GET    /api/reports                    # List reports (filter, search, paginate)
GET    /api/reports/:id                # Get report details
GET    /api/reports/:id/render         # Render report as HTML/Markdown
DELETE /api/reports/:id                # Delete report
GET    /api/reports/export             # Export multiple reports
```

### Projects

```
GET    /api/projects                   # List projects
POST   /api/projects                   # Register new project
GET    /api/projects/:id               # Get project details
PUT    /api/projects/:id               # Update project config
DELETE /api/projects/:id               # Remove project
GET    /api/projects/:id/agents        # Get compatible agents
```

### Real-time

```
WS     /ws/agents/:id                  # WebSocket for agent status updates
WS     /ws/tasks/:id                   # WebSocket for task progress
WS     /ws/logs                        # WebSocket for streaming logs
```

---

## Agent Communication Protocol

### Task Format (JSON)

```json
{
  "task_id": "uuid",
  "project": {
    "id": "uuid",
    "name": "wildfire-simulator-v2",
    "path": "/path/to/project",
    "git_branch": "main",
    "language": "python",
    "metadata": {}
  },
  "agent": {
    "name": "fbp-algorithm-agent",
    "type": "domain-specialist"
  },
  "task": {
    "type": "review",
    "title": "Review FBP calculations for accuracy",
    "description": "Audit src/core/fbp_calculator.py...",
    "priority": 8,
    "deadline": "2025-11-08T12:00:00Z",
    "files_to_check": [
      "src/core/fbp_calculator.py",
      "tests/test_fbp_validation.py"
    ],
    "context": {
      "recent_changes": "...",
      "related_issues": ["#123"]
    }
  },
  "output_requirements": {
    "report_format": "json",
    "include_recommendations": true,
    "include_code_samples": true,
    "severity_levels": ["critical", "high", "medium", "low"]
  }
}
```

### Report Format (JSON)

```json
{
  "report_id": "uuid",
  "task_id": "uuid",
  "agent": "fbp-algorithm-agent",
  "project": "wildfire-simulator-v2",
  "timestamp": "2025-11-07T18:30:00Z",
  "execution_time": "45 seconds",

  "summary": {
    "status": "completed",
    "findings_count": 12,
    "critical_issues": 2,
    "recommendations_count": 8
  },

  "findings": [
    {
      "id": "FIND-001",
      "severity": "critical",
      "category": "scientific-accuracy",
      "title": "BUI equation crushes fire spread at extreme values",
      "description": "...",
      "location": {
        "file": "src/core/fbp_calculator.py",
        "lines": [117, 162],
        "function": "calculate_bui_effect"
      },
      "evidence": {
        "code_snippet": "...",
        "test_results": "..."
      },
      "impact": "HIGH - Megafire predictions unreliable",
      "recommendation": "Cap BUI at 80 for effect calculation"
    }
  ],

  "recommendations": [
    {
      "id": "REC-001",
      "priority": "P0",
      "title": "Fix BUI effect equation",
      "description": "...",
      "effort_estimate": "2 hours",
      "files_to_modify": ["src/core/fbp_calculator.py"],
      "code_sample": "..."
    }
  ],

  "metrics": {
    "files_analyzed": 15,
    "lines_of_code": 2451,
    "tests_run": 39,
    "tests_passed": 37,
    "tests_failed": 2
  },

  "attachments": [
    {
      "type": "chart",
      "title": "ROS vs BUI comparison",
      "data": {...}
    }
  ]
}
```

---

## Frontend Design

### Key Pages

#### 1. Dashboard (Home)
- Agent status cards (idle/running/error)
- Active tasks list
- Recent reports
- System health metrics

#### 2. Agents Page
- Table/grid of all agents
- Filters: type, status, expertise
- Quick actions: start, stop, assign task
- Agent detail modal with:
  - Current task
  - Recent history
  - Performance metrics
  - DNA evolution graph

#### 3. Tasks Page
- Kanban board or table view
- Columns: Pending, Running, Completed, Failed
- Create task button with form:
  - Select project
  - Select agent(s)
  - Task type and priority
  - Description and files
- Task detail view with:
  - Progress timeline
  - Live logs
  - Generated reports

#### 4. Reports Page
- Searchable, filterable report library
- Report cards with preview
- Report viewer with:
  - Syntax-highlighted code
  - Collapsible sections
  - Charts and visualizations
  - Export options (PDF, Markdown, JSON)

#### 5. Projects Page
- List of registered projects
- Add new project form
- Project detail with:
  - Compatible agents
  - Recent tasks
  - Project-specific config

### UI Components

```typescript
// Agent Status Card
<AgentCard
  agent={agent}
  status="running"
  currentTask="Reviewing FBP calculations"
  progress={65}
  onStop={() => {}}
  onViewLogs={() => {}}
/>

// Task Assignment Form
<TaskForm
  projects={projects}
  agents={agents}
  onSubmit={(task) => {}}
/>

// Report Viewer
<ReportViewer
  report={report}
  renderMode="interactive" // or 'pdf', 'markdown'
  onExport={() => {}}
/>
```

---

## Implementation Phases

### Phase 1: Core Backend (Week 1)
- [ ] Set up FastAPI project structure
- [ ] Create database schema and migrations
- [ ] Implement agent management endpoints
- [ ] Implement task queue system
- [ ] Create agent wrapper script
- [ ] Test with 2-3 existing agents

### Phase 2: Frontend Foundation (Week 2)
- [ ] Set up Next.js project
- [ ] Create dashboard layout
- [ ] Build agent status cards
- [ ] Implement task list view
- [ ] Add WebSocket connection
- [ ] Basic report viewer

### Phase 3: Advanced Features (Week 3)
- [ ] Report rendering engine (syntax highlighting, charts)
- [ ] Task assignment workflow
- [ ] Project management UI
- [ ] Search and filtering
- [ ] Export functionality

### Phase 4: Project Agnostic (Week 4)
- [ ] Project configuration system
- [ ] Agent protocol standardization
- [ ] Multi-project support
- [ ] Agent DNA integration
- [ ] Performance metrics dashboard

### Phase 5: Polish & Deploy (Week 5)
- [ ] Authentication/authorization
- [ ] Error handling and monitoring
- [ ] Documentation
- [ ] Docker deployment
- [ ] CI/CD pipeline

---

## Technical Considerations

### 1. Agent Isolation
- Run agents in separate processes or containers
- Sandbox for security
- Resource limits (CPU, memory, time)

### 2. Project Context Injection
- Mount project directory read-only
- Provide git context (branch, commit, diff)
- Include project metadata (language, frameworks)

### 3. Real-time Updates
- WebSocket for live status
- Server-Sent Events as fallback
- Optimistic UI updates

### 4. Report Storage
- Store full report JSON in database
- Cache rendered HTML/Markdown
- File attachments in object storage (S3/local)

### 5. Scalability
- Horizontal scaling with load balancer
- Redis for distributed task queue
- Read replicas for database

---

## Security Considerations

- **Authentication**: JWT tokens or session-based auth
- **Authorization**: Role-based access (admin, viewer, operator)
- **Agent Sandboxing**: Prevent malicious code execution
- **API Rate Limiting**: Prevent abuse
- **Audit Logs**: Track all task creations and agent actions
- **Secret Management**: Vault for API keys, credentials

---

## Example User Flows

### Flow 1: Code Review Request

1. User clicks "New Task" button
2. Selects project: "my-python-app"
3. Selects agents: "code-quality-agent", "security-agent"
4. Fills in:
   - Task type: "Code Review"
   - Priority: High
   - Description: "Review authentication module"
   - Files: `src/auth/*.py`
5. Clicks "Assign Task"
6. Dashboard shows tasks as "Pending" → "Running"
7. Live logs stream in task detail page
8. When complete, reports appear in Reports tab
9. User clicks report to view findings
10. Report shows:
    - 3 security issues (highlighted code)
    - 5 code quality suggestions
    - Recommendations with code samples

### Flow 2: Multi-Project Agent

1. User registers new project "customer-api"
2. Configures project:
   - Language: Python
   - Framework: FastAPI
   - Agents: performance-agent, testing-agent
3. Creates task: "Analyze API performance"
4. Performance agent executes on customer-api codebase
5. Generates report with bottlenecks and optimizations
6. User reviews report in dashboard
7. Exports report as PDF for customer

---

## Success Metrics

- ✅ Agents can work on any project without modification
- ✅ Reports are easily readable and navigable
- ✅ Task assignment takes < 30 seconds
- ✅ Real-time updates with < 1 second latency
- ✅ Support for 25+ agents concurrently
- ✅ Report search finds results in < 2 seconds
- ✅ 99.9% uptime for dashboard

---

## Next Steps

1. **Review & Approve Design**: Discuss architecture and tech stack
2. **Set Up Projects**: Create backend and frontend repos
3. **Build MVP**: Implement Phase 1-2 (basic agent management + UI)
4. **Iterate**: Add features based on usage feedback
5. **Scale**: Optimize for production deployment

---

## References

- Your existing agent system: `.agents/`
- Report examples: `.agents/development_team/reports/`
- Agent prompts: `.agents/domain_agents/*.txt`
- Multi-agent docs: `MULTI_AGENT_SYSTEM_README.md`
