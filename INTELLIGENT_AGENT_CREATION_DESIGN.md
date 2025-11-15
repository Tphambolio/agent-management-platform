# Intelligent Agent Creation System - Design Document

## Vision

Enable users to create sophisticated, self-learning agents through natural language descriptions. The system will automatically generate optimal agent configurations, assign relevant skills, and enable continuous self-improvement.

## Architecture

### 1. Agent Factory API

**New Endpoint:** `POST /api/agents/create-intelligent`

**Input:**
```json
{
  "description": "I need an agent that can analyze satellite imagery for wildfire detection and predict fire spread patterns",
  "requirements": [  // Optional
    "Must use Python",
    "Should integrate with NASA FIRMS data",
    "Needs to output GeoTIFF files"
  ],
  "initial_knowledge": {  // Optional
    "known_libraries": ["rasterio", "numpy", "scikit-learn"],
    "domain_context": "Canadian wildfire management"
  }
}
```

**Process Flow:**
```
User Description
    ↓
AI Analysis (Claude/Gemini)
    ↓
Generate Agent Profile
    - Name: "Satellite Imagery Analyst Agent"
    - Type: "domain_specialist"
    - Specialization: "Wildfire detection from satellite imagery with spread prediction"
    ↓
Generate Initial Genome
    - Technical Skills: rasterio, numpy, ML libraries
    - Domain Skills: Fire behavior, remote sensing
    - Starter Code: Template functions
    ↓
Create Database Record (PostgreSQL)
    ↓
Save Genome to .agents/dna/
    ↓
Return Agent Ready for Tasks
```

### 2. AI-Powered Agent Generator

**Component:** `backend/app/agent_factory.py`

**Responsibilities:**

#### 2.1 Agent Profile Generation
```python
async def generate_agent_profile(description: str, requirements: List[str] = None) -> AgentProfile:
    """
    Uses Claude/Gemini to analyze description and generate:
    - Agent name (human-readable)
    - Agent type (domain_specialist, developer, researcher, etc.)
    - Specialization (detailed description)
    - Recommended capabilities
    - Initial skill set
    """
```

**AI Prompt Template:**
```
You are an AI Agent Designer. Based on the user's description, design an optimal agent.

User Description: {description}
Requirements: {requirements}

Generate a JSON response with:
{
  "name": "Professional agent name ending with 'Agent'",
  "type": "domain_specialist|developer|researcher|coordinator|general",
  "specialization": "Detailed 1-2 sentence description",
  "capabilities": ["capability1", "capability2", ...],
  "recommended_skills": {
    "technical": [
      {"name": "python_data_analysis", "libraries": ["pandas", "numpy"]},
      {"name": "geospatial_processing", "libraries": ["rasterio", "gdal"]}
    ],
    "domain": [
      {"name": "wildfire_behavior", "proficiency": "intermediate"},
      {"name": "remote_sensing", "proficiency": "advanced"}
    ]
  },
  "starter_code_templates": [
    {
      "function_name": "analyze_satellite_image",
      "description": "Analyze satellite imagery for fire detection",
      "code": "def analyze_satellite_image(image_path: str) -> dict:\n    # Template implementation\n    pass"
    }
  ]
}
```

#### 2.2 Genome Generation
```python
def generate_initial_genome(agent_profile: AgentProfile) -> dict:
    """
    Creates a genome.json structure with:
    - agent_metadata (id, role, evolution_stage=beginner)
    - skills.technical (from recommended_skills)
    - skills.domain (from recommended_skills)
    - experience_bank (empty, ready to learn)
    - session_memory (empty)
    - evolution_metrics (initialized to 0)
    """
```

**Generated Genome Structure:**
```json
{
  "agent_metadata": {
    "agent_id": "satellite-imagery-analyst-agent",
    "role": "satellite-imagery-analyst",
    "total_sessions": 0,
    "evolution_stage": "beginner",
    "created_at": "2025-11-15T16:00:00Z",
    "created_by": "intelligent-agent-factory",
    "original_description": "User's natural language description"
  },
  "skills": {
    "technical": {
      "python_data_analysis": {
        "level": 3,
        "description": "Data analysis with pandas and numpy",
        "libraries": ["pandas", "numpy"],
        "code": "# Starter template code",
        "added": "2025-11-15T16:00:00Z",
        "source": "agent-factory"
      },
      "analyze_satellite_image": {
        "level": 1,
        "description": "Analyze satellite imagery for fire detection",
        "code": "def analyze_satellite_image(image_path: str) -> dict:\n    pass",
        "added": "2025-11-15T16:00:00Z",
        "source": "agent-factory-template"
      }
    },
    "domain": {
      "wildfire_behavior": {
        "version": "1.0.0",
        "description": "Understanding of wildfire spread patterns",
        "proficiency": "intermediate",
        "acquired": "2025-11-15"
      }
    }
  },
  "experience_bank": {
    "patterns_known": [],
    "techniques_mastered": [],
    "pitfalls_remembered": [],
    "insights_discovered": []
  },
  "session_memory": {
    "last_session_summary": "Newly created agent, ready for first task",
    "next_priorities": ["Complete first task", "Learn domain-specific techniques"],
    "work_in_progress": []
  },
  "evolution_metrics": {
    "tasks_completed": 0,
    "patterns_created": 0,
    "learning_velocity": "beginner",
    "total_learning_events": 0
  }
}
```

### 3. Skill Self-Modification System

**Component:** `backend/app/skill_evolution.py`

**Purpose:** Allow agents to rewrite their own skills based on learning

#### 3.1 Skill Improvement Detection
```python
async def detect_skill_improvements(agent_id: str, report_content: str) -> List[SkillImprovement]:
    """
    Analyzes task report to find:
    - Better implementations of existing skills
    - Optimizations of current code
    - Bug fixes in skill code
    - New variations of existing skills
    """
```

**Process:**
1. Extract code from report
2. Compare with existing skills in genome
3. Identify improvements:
   - Same function signature, better algorithm
   - More error handling
   - Performance optimizations
   - Extended functionality

#### 3.2 Skill Rewriting
```python
async def rewrite_skill(
    agent_id: str,
    skill_name: str,
    new_code: str,
    reason: str
) -> SkillUpdateResult:
    """
    Rewrites an existing skill:
    1. Validate new code (syntax check)
    2. Preserve skill history (version control)
    3. Update genome with new code
    4. Increment skill level
    5. Add rewrite event to evolution history
    """
```

**Skill Versioning:**
```json
{
  "skills": {
    "technical": {
      "analyze_satellite_image": {
        "current_version": 3,
        "level": 4,
        "code": "def analyze_satellite_image(...):\n    # v3 implementation",
        "history": [
          {
            "version": 1,
            "code": "# Original template",
            "timestamp": "2025-11-15T16:00:00Z",
            "source": "agent-factory-template"
          },
          {
            "version": 2,
            "code": "# First improvement from task",
            "timestamp": "2025-11-15T17:30:00Z",
            "source": "task-learning",
            "improvement": "Added error handling"
          },
          {
            "version": 3,
            "code": "# Current version",
            "timestamp": "2025-11-15T18:45:00Z",
            "source": "skill-rewrite",
            "improvement": "Optimized for performance, 3x faster"
          }
        ]
      }
    }
  }
}
```

### 4. Enhanced Learning Pipeline

**Current Flow:**
```
Task → Research → Agent Execution → Report → Code Extraction → Add New Skills
```

**Enhanced Flow:**
```
Task → Research → Agent Execution → Report
    ↓
Code Extraction & Analysis
    ↓
[Fork] Two parallel processes:
    ↓                           ↓
Add New Skills          Improve Existing Skills
    ↓                           ↓
Update Genome          Version & Rewrite Skills
    ↓                           ↓
    └───────────[Merge]─────────┘
                ↓
    Evolution Metrics Update
                ↓
    Agent Level Up (if thresholds met)
```

**Level Up System:**
```python
def check_evolution_stage(agent_genome: dict) -> str:
    """
    Determines agent evolution stage based on:
    - tasks_completed
    - patterns_created
    - skills_count
    - skill_rewrites
    - learning_velocity

    Stages: beginner → intermediate → advanced → expert → master
    """
```

**Thresholds:**
- Beginner → Intermediate: 5 tasks, 10 skills, 5 patterns
- Intermediate → Advanced: 15 tasks, 25 skills, 15 patterns, 5 skill rewrites
- Advanced → Expert: 30 tasks, 50 skills, 30 patterns, 15 skill rewrites
- Expert → Master: 50+ tasks, 100+ skills, 50+ patterns, 30+ skill rewrites

### 5. Agent Specialization Refinement

**Component:** `backend/app/agent_refinement.py`

**Purpose:** Automatically refine agent's specialization based on actual work

```python
async def refine_specialization(agent_id: str):
    """
    Analyzes agent's task history and skills to generate updated specialization:
    1. Load all completed tasks
    2. Extract common themes and domains
    3. Identify most-used skills
    4. Generate new specialization text
    5. Update agent record and genome
    """
```

**Example Evolution:**
```
Initial: "Wildfire detection from satellite imagery with spread prediction"
    ↓ (After 10 tasks)
Refined: "Expert in multi-spectral satellite analysis for real-time wildfire detection,
          specializing in MODIS/VIIRS data processing and FBP-based spread modeling"
    ↓ (After 30 tasks)
Master: "Master-level wildfire intelligence analyst specializing in multi-sensor fusion
         (Landsat, MODIS, VIIRS), ML-based fire detection, and operational spread
         forecasting using Canadian FBP System. Expert in geospatial analytics and
         real-time alert systems."
```

## Implementation Plan

### Phase 1: Agent Factory Core (Week 1)
- [ ] Create `agent_factory.py` with AI-powered profile generation
- [ ] Implement genome generation from profile
- [ ] Add `POST /api/agents/create-intelligent` endpoint
- [ ] Test with various descriptions

### Phase 2: Skill Self-Modification (Week 2)
- [ ] Create `skill_evolution.py` with improvement detection
- [ ] Implement skill versioning system
- [ ] Add skill rewrite logic to learning pipeline
- [ ] Test skill evolution over multiple tasks

### Phase 3: Evolution System (Week 3)
- [ ] Implement evolution stage detection
- [ ] Add automatic specialization refinement
- [ ] Create evolution metrics dashboard
- [ ] Test full learning cycle

### Phase 4: Frontend Integration (Week 4)
- [ ] Create "Natural Language Agent Creation" form
- [ ] Add skill browser with version history
- [ ] Display evolution timeline
- [ ] Show skill improvement suggestions

## API Examples

### Creating an Intelligent Agent

**Request:**
```bash
curl -X POST https://agent-platform-backend-3g16.onrender.com/api/agents/create-intelligent \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I need an agent that can scrape research papers from arXiv, extract key findings, and create summaries with citations",
    "requirements": [
      "Must handle PDFs",
      "Should use BeautifulSoup for scraping",
      "Needs to format citations in APA style"
    ]
  }'
```

**Response:**
```json
{
  "agent": {
    "id": "uuid",
    "name": "Research Paper Analyst Agent",
    "type": "researcher",
    "specialization": "Automated research paper analysis with citation extraction and summarization",
    "status": "idle",
    "evolution_stage": "beginner",
    "skills_count": 8,
    "created_at": "2025-11-15T16:00:00Z"
  },
  "genome_path": ".agents/dna/research-paper-analyst-agent/genome.json",
  "initial_capabilities": [
    "PDF text extraction",
    "Web scraping with BeautifulSoup",
    "Citation formatting (APA)",
    "Natural language summarization",
    "arXiv API integration"
  ],
  "ready_for_tasks": true,
  "message": "Agent created successfully with 8 initial skills. Ready to start learning!"
}
```

### Viewing Skill Evolution

**Request:**
```bash
GET /api/agents/{agent_id}/skills/{skill_name}/history
```

**Response:**
```json
{
  "skill_name": "analyze_satellite_image",
  "current_version": 3,
  "current_level": 4,
  "versions": [
    {
      "version": 1,
      "created_at": "2025-11-15T16:00:00Z",
      "source": "agent-factory-template",
      "code_preview": "def analyze_satellite_image(image_path):\n    pass",
      "notes": "Initial template"
    },
    {
      "version": 2,
      "created_at": "2025-11-15T17:30:00Z",
      "source": "task-learning",
      "improvement": "Added NDVI calculation and error handling",
      "code_preview": "def analyze_satellite_image(image_path):\n    try:\n        # NDVI implementation\n    except...",
      "task_id": "task-uuid",
      "level_gained": 1
    },
    {
      "version": 3,
      "created_at": "2025-11-15T18:45:00Z",
      "source": "skill-rewrite",
      "improvement": "Optimized using vectorized numpy operations, 3x performance gain",
      "code_preview": "def analyze_satellite_image(image_path):\n    # Vectorized implementation",
      "performance_gain": "3x",
      "level_gained": 1
    }
  ],
  "total_improvements": 2,
  "performance_trend": "improving"
}
```

## Database Schema Updates

### New Table: `agent_evolution_events`

```sql
CREATE TABLE agent_evolution_events (
    id VARCHAR PRIMARY KEY,
    agent_id VARCHAR REFERENCES agents(id),
    event_type VARCHAR(50),  -- 'skill_added', 'skill_rewritten', 'level_up', 'specialization_refined'
    event_data JSON,
    skill_name VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    improvement_description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Purpose:** Track complete evolution history for analytics and rollback

### Updated Genome Metadata

```json
{
  "agent_metadata": {
    "agent_id": "satellite-imagery-analyst-agent",
    "creation_method": "intelligent-agent-factory",  // NEW
    "original_description": "User's description",     // NEW
    "evolution_stage": "expert",
    "evolution_history": [                            // NEW
      {
        "stage": "beginner",
        "achieved_at": "2025-11-15T16:00:00Z"
      },
      {
        "stage": "intermediate",
        "achieved_at": "2025-11-16T10:30:00Z",
        "tasks_completed": 5
      }
    ]
  }
}
```

## Security & Validation

### Code Validation Pipeline

1. **Syntax Check:** Compile Python code before adding to genome
2. **Sandboxed Execution:** Test code in isolated environment
3. **Dependency Analysis:** Verify all imports are allowed
4. **Security Scan:** Check for malicious patterns
5. **Performance Test:** Ensure code doesn't have infinite loops

### Skill Rewrite Approval (Optional)

```python
# Optional: Require human approval for critical rewrites
if skill.is_critical and not auto_approve:
    await request_human_approval(agent_id, skill_name, old_code, new_code, reason)
```

## Monitoring & Analytics

### Agent Performance Metrics

- **Learning Velocity:** Skills added per task
- **Skill Quality:** Average skill level across all skills
- **Evolution Speed:** Time between stage upgrades
- **Code Quality:** Syntax error rate in learned code
- **Rewrite Success Rate:** % of skill rewrites that improve performance

### Dashboard Widgets

1. **Agent Evolution Timeline:** Visual progression through stages
2. **Skill Heatmap:** Most-used and highest-level skills
3. **Learning Curve:** Skills count over time
4. **Specialization Cloud:** Word cloud of agent's domains
5. **Performance Trends:** Task completion time trending

## Future Enhancements

### 1. Agent Collaboration
- Agents can share skills with each other
- "Mentor" agents teach "student" agents
- Skill marketplace: Browse and import skills

### 2. Agent Forking
- Clone an agent with all its skills
- Create specialized variants of successful agents
- A/B test different agent configurations

### 3. Multi-Agent Projects
- Agents collaborate on complex tasks
- Automatic task decomposition and delegation
- Skill-based agent selection for subtasks

### 4. Explainable AI
- Agents explain why they chose specific skills
- Show reasoning process for skill rewrites
- Confidence scores for skill applications

## Success Criteria

✅ **User can create agent in <30 seconds** using natural language
✅ **Agent performs first task within 5 minutes** of creation
✅ **Agent learns at least 3 new skills** in first 5 tasks
✅ **Agent rewrites at least 1 skill** in first 10 tasks
✅ **Agent reaches "intermediate"** stage within 15 tasks
✅ **All agents persist** across deployments (PostgreSQL)
✅ **Zero manual skill assignment** required

## Conclusion

This Intelligent Agent Creation System transforms agent management from a manual configuration process into an AI-powered, self-evolving ecosystem. Users describe what they need in plain English, and the system creates, trains, and continuously improves agents automatically.

The key innovation is the **self-modifying genome** - agents don't just learn new skills, they actively improve their existing capabilities based on experience, creating a true evolutionary AI system.
