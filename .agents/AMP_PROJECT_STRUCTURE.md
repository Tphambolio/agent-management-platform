# Agent Management Platform - Project Structure

## Recommended Directory Structure

```
agent-management-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Configuration management
│   │   ├── database.py                # Database connection
│   │   │
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── task.py
│   │   │   ├── report.py
│   │   │   ├── project.py
│   │   │   └── log.py
│   │   │
│   │   ├── schemas/                   # Pydantic schemas (API contracts)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── task.py
│   │   │   ├── report.py
│   │   │   └── project.py
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── agents.py
│   │   │   ├── tasks.py
│   │   │   ├── reports.py
│   │   │   ├── projects.py
│   │   │   └── websocket.py
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py       # Agent lifecycle management
│   │   │   ├── task_service.py        # Task queue and execution
│   │   │   ├── report_service.py      # Report processing and rendering
│   │   │   └── project_service.py     # Project management
│   │   │
│   │   ├── agents/                    # Agent runtime layer
│   │   │   ├── __init__.py
│   │   │   ├── agent_wrapper.py       # Base agent wrapper
│   │   │   ├── agent_protocol.py      # Communication protocol
│   │   │   ├── agent_executor.py      # Execute agent tasks
│   │   │   └── agent_registry.py      # Discover and register agents
│   │   │
│   │   ├── utils/                     # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   ├── validators.py
│   │   │   └── formatters.py
│   │   │
│   │   └── templates/                 # Report templates
│   │       ├── report_html.jinja2
│   │       └── report_markdown.jinja2
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/
│   │   ├── test_agents.py
│   │   ├── test_tasks.py
│   │   └── test_reports.py
│   │
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js app directory
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Dashboard
│   │   │   │
│   │   │   ├── agents/
│   │   │   │   ├── page.tsx           # Agents list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Agent detail
│   │   │   │
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx           # Tasks list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Task detail
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   ├── page.tsx           # Reports library
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Report viewer
│   │   │   │
│   │   │   └── projects/
│   │   │       ├── page.tsx           # Projects list
│   │   │       └── [id]/
│   │   │           └── page.tsx       # Project detail
│   │   │
│   │   ├── components/                # React components
│   │   │   ├── ui/                    # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── agents/
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   ├── AgentList.tsx
│   │   │   │   ├── AgentStatusBadge.tsx
│   │   │   │   └── AgentMetrics.tsx
│   │   │   │
│   │   │   ├── tasks/
│   │   │   │   ├── TaskCard.tsx
│   │   │   │   ├── TaskForm.tsx
│   │   │   │   ├── TaskKanban.tsx
│   │   │   │   └── TaskTimeline.tsx
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   ├── ReportViewer.tsx
│   │   │   │   ├── ReportCard.tsx
│   │   │   │   ├── FindingsList.tsx
│   │   │   │   ├── CodeSnippet.tsx
│   │   │   │   └── ReportChart.tsx
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   │
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── SearchBar.tsx
│   │   │
│   │   ├── lib/                       # Utilities
│   │   │   ├── api.ts                 # API client
│   │   │   ├── websocket.ts           # WebSocket client
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useAgents.ts
│   │   │   ├── useTasks.ts
│   │   │   ├── useReports.ts
│   │   │   └── useWebSocket.ts
│   │   │
│   │   ├── store/                     # State management (Zustand)
│   │   │   ├── agentStore.ts
│   │   │   ├── taskStore.ts
│   │   │   └── uiStore.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css
│   │
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── shared/
│   ├── schemas/                       # Shared TypeScript/Python schemas
│   │   ├── agent.schema.json
│   │   ├── task.schema.json
│   │   └── report.schema.json
│   │
│   └── types/                         # TypeScript type definitions
│       ├── agent.types.ts
│       ├── task.types.ts
│       └── report.types.ts
│
├── docs/
│   ├── API.md                         # API documentation
│   ├── DEPLOYMENT.md                  # Deployment guide
│   └── DEVELOPMENT.md                 # Development setup
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── scripts/
│   ├── setup.sh                       # Initial setup script
│   ├── migrate-agents.sh              # Migrate existing agents
│   └── seed-db.sh                     # Seed database with sample data
│
├── .env.example
├── .gitignore
└── README.md
```

---

## Key Files Explained

### Backend

**`backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import agents, tasks, reports, projects, websocket
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agent Management Platform API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
def root():
    return {"message": "Agent Management Platform API", "version": "1.0"}
```

**`backend/app/agents/agent_wrapper.py`**
```python
import subprocess
import json
from pathlib import Path

class AgentWrapper:
    """Wrapper for executing agents in isolated environments"""

    def __init__(self, agent_name: str, agent_path: Path):
        self.name = agent_name
        self.path = agent_path
        self.process = None

    def execute_task(self, task: dict, project: dict) -> dict:
        """Execute a task with project context"""
        task_input = {
            "task": task,
            "project": project,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Write task to temp file
        task_file = Path(f"/tmp/task_{task['id']}.json")
        task_file.write_text(json.dumps(task_input))

        # Execute agent
        cmd = [
            "python", str(self.path),
            "--task-file", str(task_file),
            "--output", f"/tmp/report_{task['id']}.json"
        ]

        self.process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=task.get("timeout", 600)
        )

        # Read report
        report_file = Path(f"/tmp/report_{task['id']}.json")
        if report_file.exists():
            return json.loads(report_file.read_text())
        else:
            raise Exception(f"Agent failed: {self.process.stderr}")
```

### Frontend

**`frontend/src/components/agents/AgentCard.tsx`**
```typescript
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface AgentCardProps {
  agent: {
    id: string
    name: string
    type: string
    status: 'idle' | 'running' | 'error' | 'stopped'
    currentTask?: string
    progress?: number
  }
  onStop: () => void
  onViewLogs: () => void
}

export function AgentCard({ agent, onStop, onViewLogs }: AgentCardProps) {
  const statusColors = {
    idle: 'bg-gray-500',
    running: 'bg-green-500',
    error: 'bg-red-500',
    stopped: 'bg-yellow-500'
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">{agent.name}</CardTitle>
        <Badge className={statusColors[agent.status]}>
          {agent.status}
        </Badge>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-2">{agent.type}</p>

        {agent.currentTask && (
          <div className="mb-3">
            <p className="text-sm font-medium">Current Task:</p>
            <p className="text-sm text-gray-700">{agent.currentTask}</p>
            {agent.progress !== undefined && (
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${agent.progress}%` }}
                />
              </div>
            )}
          </div>
        )}

        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={onViewLogs}>
            View Logs
          </Button>
          {agent.status === 'running' && (
            <Button size="sm" variant="destructive" onClick={onStop}>
              Stop
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
```

**`frontend/src/app/page.tsx` (Dashboard)**
```typescript
import { AgentCard } from "@/components/agents/AgentCard"
import { TaskList } from "@/components/tasks/TaskList"
import { ReportCard } from "@/components/reports/ReportCard"
import { useAgents } from "@/hooks/useAgents"
import { useTasks } from "@/hooks/useTasks"
import { useReports } from "@/hooks/useReports"

export default function Dashboard() {
  const { agents } = useAgents()
  const { tasks } = useTasks({ limit: 5, status: 'running' })
  const { reports } = useReports({ limit: 5 })

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Agent Management Platform</h1>

      {/* Agent Status */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Active Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.filter(a => a.status === 'running').map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onStop={() => handleStopAgent(agent.id)}
              onViewLogs={() => handleViewLogs(agent.id)}
            />
          ))}
        </div>
      </section>

      {/* Active Tasks */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Running Tasks</h2>
        <TaskList tasks={tasks} />
      </section>

      {/* Recent Reports */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reports.map(report => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      </section>
    </div>
  )
}
```

---

## Environment Configuration

**`.env.example`**
```bash
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/amp_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here

# Agent Paths
AGENTS_BASE_PATH=/path/to/wildfire-simulator-v2/.agents
PROJECTS_BASE_PATH=/path/to/projects

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Database Migrations

**Initial migration (Alembic)**
```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## Docker Deployment

**`docker-compose.yml`**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: amp_db
      POSTGRES_USER: amp_user
      POSTGRES_PASSWORD: amp_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://amp_user:amp_password@postgres:5432/amp_db
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
      - ../wildfire-simulator-v2/.agents:/agents:ro
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_WS_URL: ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# With Docker
docker-compose up -d

# Access
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## Next Steps

1. Create the directory structure
2. Set up basic FastAPI backend
3. Set up Next.js frontend
4. Implement agent discovery and registration
5. Build task execution pipeline
6. Create report viewer
