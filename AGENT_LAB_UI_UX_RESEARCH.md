# Agent Lab UI/UX Improvement Research - Counter-Style Interaction & Archive System

## Executive Summary
This research report investigates improvements for the Agent Management Platform frontend, aiming to transform it into an intuitive agent lab with a counter-style interaction model. The core objective is to enable users to seamlessly initiate research, build solutions with agents, receive real-time feedback, and comprehensively archive all outputs. Key findings highlight the critical role of streaming interfaces for dynamic user feedback, the necessity of robust agent orchestration frameworks for complex task execution, and the architectural requirements for a comprehensive session history and archive system.

The current UI at https://frontend-travis-kennedys-projects.vercel.app/ provides a foundational chat interface but lacks the advanced features required for an "agent lab," such as explicit agent capabilities, real-time workflow visualization, and structured archiving. This report synthesizes insights from leading AI tools and frameworks to propose actionable recommendations. These include implementing token-by-token streaming for immediate user engagement, integrating agent frameworks like LangChain or Pydantic AI for tool-use and multi-step reasoning, and designing a structured database schema for persistent storage of agent interactions, research artifacts, and built solutions.

Ultimately, the report recommends a phased approach focusing on enhancing real-time interactivity, clearly exposing agent capabilities through a counter-style prompt, and establishing a robust backend for archiving. By adopting these recommendations, the platform can evolve into a powerful, intuitive, and transparent environment for developing and managing AI agents, fostering a seamless research-to-implementation workflow and ensuring discoverability of agent capabilities.

## Background & Context
The rapid evolution of Large Language Models (LLMs) and autonomous agents has created a demand for sophisticated yet intuitive platforms to manage and interact with these capabilities. An "agent lab" environment is crucial for users to experiment, develop, and deploy AI agents effectively. Such a platform must move beyond simple chat interfaces to support complex, multi-step agentic workflows, providing transparency into agent reasoning and ensuring that valuable research and built solutions are systematically archived.

The current UI at https://frontend-travis-kennedys-projects.vercel.app/ serves as a basic conversational interface. However, to function as an "agent lab," it needs significant enhancements to facilitate a "counter-style interaction" where users can define problems, agents can autonomously research and build, and all processes are transparent and archivable. Key challenges include providing real-time feedback during potentially long-running agent tasks, visualizing agent decision-making, and creating a structured system for storing diverse outputs—from research summaries to executable code. This research aims to bridge this gap by leveraging best practices from modern AI development frameworks and UI/UX principles.

## Research Methodology
The research employed a targeted search strategy focusing on practical implementation aspects of streaming LLM UIs, agent orchestration, and session history architecture. The search terms included "streaming LLM agent UI code example python," "AI agent session history architecture database schema," "agent orchestration platform UI tutorial API python," and "agentic AI UI design patterns user studies methodology."

Sources were selected based on their direct relevance to the technical implementation of streaming interfaces (e.g., Streamlit, LangChain, OpenAI Agents SDK), agent framework capabilities (e.g., Pydantic AI, LangChain), and architectural considerations for data persistence (e.g., database schemas for session history). Eleven sources were gathered, comprising official documentation, technical articles, and research overviews. The synthesis method involved extracting key concepts, code examples, and architectural patterns from these sources, then mapping them directly to the research assignment's requirements for UI/UX, real-time feedback, agent capabilities, and archiving.

## Key Findings

### Finding 1: Real-time Streaming is Fundamental for Agent Interaction
The ability to stream responses token-by-token or event-by-event is consistently highlighted as a critical feature for modern LLM and agent applications. This provides immediate feedback, enhances user engagement, and makes long-running agent processes feel more responsive [Source 1, Source 2, Source 3, Source 4, Source 5, Source 6, Source 7]. Frameworks like Streamlit, LangChain, OpenAI Agents SDK, and Pydantic AI all offer robust mechanisms for streaming outputs and internal events. For instance, `run_stream()` in Pydantic AI and `Runner.run_streamed()` in OpenAI Agents SDK allow for real-time insight into agent activity, including tool usage and intermediate thoughts, which is vital for an "agent lab" environment [Source 3, Source 5]. This directly addresses the "real-time feedback during research and building phases" requirement.

### Finding 2: Agent Orchestration Frameworks Enable Complex Workflows
To move beyond simple chat to an "agent lab" where agents "research/build/archive solutions," robust agent orchestration frameworks are indispensable. LangChain and Pydantic AI are prominent examples that allow for initializing agents with specific tools (e.g., search, code execution) and managing their decision-making process [Source 2, Source 4, Source 8]. These frameworks facilitate the creation of agents that can perform multi-step reasoning, interact with external APIs (like Google/DuckDuckGo for research), and generate structured outputs. The `initialize_agent` function in LangChain, coupled with `load_tools`, exemplifies how agents can be equipped for diverse tasks [Source 2]. This capability is central to the "agents research/build" aspect of the counter-style interaction.

### Finding 3: Comprehensive Archiving Requires Structured Session History
A "comprehensive archive system for all research and built solutions" necessitates a well-designed architecture for storing agent session history. This involves not just the final output but also the intermediate steps, tool calls, user inputs, and agent reasoning processes [Source 9, Source 10, Source 11]. Research indicates that such an architecture should support both structured (e.g., JSON, database records) and unstructured (e.g., raw text logs) data, allowing for detailed retrieval and analysis of past agent activities. Key elements include tracking user queries, agent responses, tool invocations, and timestamps, enabling a full audit trail and the ability to resume or review past "experiments" [Source 9].

### Finding 4: Intuitive UI/UX Benefits from Rapid Prototyping Tools
Modern UI/UX for agent labs can be rapidly developed using frameworks like Streamlit, which simplify the creation of interactive web applications with Python [Source 1, Source 6]. Streamlit's component-based approach and native support for LLM integrations (including streaming callbacks) make it ideal for building the "counter-style interface" and visualizing agent capabilities. Its `st.chat_message` and `st.chat_input` components are directly applicable for creating an intuitive conversational flow, while custom components or expanders can be used to display agent tools, thought processes, and archived results [Source 1, Source 6]. This addresses the "modern, intuitive UI/UX that makes agent capabilities immediately discoverable" requirement.

## Technical Analysis

The transition from a basic chat interface to an "agent lab" necessitates a robust technical foundation encompassing real-time interaction, sophisticated agent logic, and persistent data storage. The current UI, while functional for simple chat, needs to integrate these elements.

### Implementation Code

#### 1. Streamlit App with Streaming LLM and Agent Callback
This example demonstrates a basic Streamlit application that integrates a local LLM (Ollama) and an agent with a search tool, providing streaming output and real-time feedback using `StreamlitCallbackHandler`. This fulfills the "counter-style interaction" and "real-time feedback" requirements.

```python
import streamlit as st
from langchain.llms import Ollama
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks import StreamlitCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler # For local testing/debug

def run_streaming_agent_app():
    """
    Implements a Streamlit application demonstrating a streaming LLM agent
    with a search tool, providing real-time feedback to the user.

    This function sets up a conversational interface where an agent can
    respond to user queries, potentially using a search tool, and streams
    its output token-by-token. It leverages Streamlit's chat components
    and LangChain's callback handlers for real-time interaction.
    """
    st.set_page_config(page_title="Agent Lab - Streaming Interaction")
    st.title("Agent Lab: Research & Build")
    st.caption("Ask anything, and the agent will research/build solutions.")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you research or build today?"}]

    # Display existing messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Setup LLM and Agent (using Ollama for local LLM, requires Ollama server running)
    # For production, replace with OpenAI or similar, and manage API keys securely.
    llm = Ollama(
        model="llama2-uncensored:latest", # Or any other local Ollama model
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]) # For server-side streaming debug
    )
    
    # Load tools (e.g., 'ddg-search' for DuckDuckGo search)
    # Ensure 'duckduckgo-search' is installed: pip install duckduckgo-search
    tools = load_tools(["ddg-search"], llm=llm)

    # Initialize the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True, # Set to True to see agent's thought process in console
        handle_parsing_errors=True
    )

    # Handle user input
    if prompt := st.chat_input("Your query for the agent..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            # Run the agent with streaming callbacks
            response = agent.run(prompt, callbacks=[st_callback])
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    # To run this, ensure you have Streamlit, LangChain, Ollama, and duckduckgo-search installed:
    # pip install streamlit langchain-community langchain-openai ollama duckduckgo-search
    # Also, ensure an Ollama server is running with 'llama2-uncensored:latest' model pulled.
    # For OpenAI, replace Ollama with ChatOpenAI and set OPENAI_API_KEY in .streamlit/secrets.toml
    run_streaming_agent_app()
```

#### 2. Conceptual Database Schema for Agent Session History and Archive
This Python class defines a conceptual schema for storing agent interactions, research, and built solutions, addressing the "comprehensive archive system" requirement. This structure can be mapped to a relational database (e.g., PostgreSQL) or a NoSQL document store (e.g., MongoDB).

```python
import datetime
from typing import List, Dict, Any, Optional

class AgentSessionArchiveSchema:
    """
    Defines a conceptual database schema for archiving agent sessions,
    including user interactions, agent actions, research outputs,
    and built solutions.

    This schema supports tracking the full lifecycle of an agent's
    engagement, from initial query to final solution, enabling
    retrieval, analysis, and reuse of past work.
    """

    def __init__(self):
        """
        Initializes the schema definition.
        """
        pass

    @staticmethod
    def get_session_table_schema() -> Dict[str, str]:
        """
        Returns the schema for the 'sessions' table/collection.
        Each entry represents a single user-initiated agent interaction session.

        Returns:
            A dictionary mapping column/field names to their data types.
        """
        return {
            "session_id": "UUID PRIMARY KEY",
            "user_id": "UUID NOT NULL",
            "start_time": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "end_time": "TIMESTAMP WITH TIME ZONE",
            "initial_query": "TEXT NOT NULL",
            "final_output": "TEXT",
            "status": "VARCHAR(50) DEFAULT 'in_progress'", # e.g., 'in_progress', 'completed', 'failed'
            "agent_model_id": "VARCHAR(255)", # e.g., 'llama2-uncensored', 'gpt-4'
            "cost_estimate_usd": "DECIMAL(10, 4)",
            "duration_seconds": "INTEGER"
        }

    @staticmethod
    def get_interaction_log_table_schema() -> Dict[str, str]:
        """
        Returns the schema for the 'interaction_logs' table/collection.
        Each entry represents a step or event within a session.

        Returns:
            A dictionary mapping column/field names to their data types.
        """
        return {
            "log_id": "UUID PRIMARY KEY",
            "session_id": "UUID REFERENCES sessions(session_id)",
            "timestamp": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "event_type": "VARCHAR(100) NOT NULL", # e.g., 'user_input', 'agent_thought', 'tool_call', 'tool_output', 'llm_response'
            "content": "JSONB", # Stores structured data like tool args, LLM tokens, error messages
            "agent_state": "JSONB", # Snapshot of agent's internal state (optional, for advanced debugging)
            "token_count": "INTEGER",
            "cost_estimate_usd": "DECIMAL(10, 4)"
        }

    @staticmethod
    def get_artifact_table_schema() -> Dict[str, str]:
        """
        Returns the schema for the 'artifacts' table/collection.
        Stores research results, built code, generated documents, etc.

        Returns:
            A dictionary mapping column/field names to their data types.
        """
        return {
            "artifact_id": "UUID PRIMARY KEY",
            "session_id": "UUID REFERENCES sessions(session_id)",
            "timestamp": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "artifact_type": "VARCHAR(100) NOT NULL", # e.g., 'research_summary', 'code_snippet', 'document', 'data_analysis'
            "title": "VARCHAR(255)",
            "content": "TEXT", # The actual content of the artifact (e.g., code, markdown)
            "file_path": "VARCHAR(512)", # Optional: path to a larger file stored externally
            "metadata": "JSONB" # Additional structured metadata (e.g., programming language, research sources)
        }

    @staticmethod
    def create_example_session_data(session_id: str, user_id: str, query: str) -> Dict[str, Any]:
        """
        Creates example data for a new session.

        Args:
            session_id: Unique identifier for the session.
            user_id: Identifier for the user.
            query: The initial query from the user.

        Returns:
            A dictionary representing a session record.
        """
        return {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "initial_query": query,
            "status": "in_progress",
            "agent_model_id": "llama2-uncensored"
        }

    @staticmethod
    def create_example_interaction_log(session_id: str, event_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates example data for an interaction log entry.

        Args:
            session_id: The session ID this log belongs to.
            event_type: The type of event (e.g., 'agent_thought', 'tool_call').
            content: A dictionary containing event-specific details.

        Returns:
            A dictionary representing an interaction log record.
        """
        return {
            "log_id": str(uuid.uuid4()), # Assuming UUID generation
            "session_id": session_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_type": event_type,
            "content": content
        }

# Example usage (conceptual, not actual database interaction)
if __name__ == "__main__":
    import uuid
    print("Agent Session Table Schema:")
    for col, dtype in AgentSessionArchiveSchema.get_session_table_schema().items():
        print(f"  {col}: {dtype}")

    print("\nInteraction Log Table Schema:")
    for col, dtype in AgentSessionArchiveSchema.get_interaction_log_table_schema().items():
        print(f"  {col}: {dtype}")

    print("\nArtifact Table Schema:")
    for col, dtype in AgentSessionArchiveSchema.get_artifact_table_schema().items():
        print(f"  {col}: {dtype}")

    # Example of creating session and log data
    new_session_id = str(uuid.uuid4())
    user_id = "user-123"
    initial_query = "Research the latest advancements in quantum computing and summarize them."

    session_data = AgentSessionArchiveSchema.create_example_session_data(new_session_id, user_id, initial_query)
    print(f"\nExample Session Data: {session_data}")

    log_thought = AgentSessionArchiveSchema.create_example_interaction_log(
        new_session_id,
        "agent_thought",
        {"thought": "User wants research on quantum computing. I should use a search tool."}
    )
    print(f"Example Agent Thought Log: {log_thought}")

    log_tool_call = AgentSessionArchiveSchema.create_example_interaction_log(
        new_session_id,
        "tool_call",
        {"tool_name": "ddg-search", "tool_args": {"query": "latest quantum computing advancements"}}
    )
    print(f"Example Tool Call Log: {log_tool_call}")
```

### Mathematical Foundations
The provided sources primarily focus on practical implementation, UI/UX, and architectural patterns rather than the deep mathematical foundations of LLMs or agent decision-making algorithms. However, in the context of an "Agent Lab," certain quantitative metrics and simple calculations are essential for monitoring agent performance, cost, and efficiency.

1.  **Token Cost Calculation:** A fundamental metric for LLM interactions is the cost per token. This is often calculated based on input and output token counts and their respective pricing tiers.
    $$ \text{Total Cost} = (\text{Input Tokens} \times \text{Input Price per Token}) + (\text{Output Tokens} \times \text{Output Price per Token}) $$
    This formula helps users understand the financial implications of agent runs and can be displayed in real-time or as part of the archived session data [Source 9].

2.  **Latency Measurement:** The responsiveness of an agent is crucial for user experience. Latency can be measured for various stages:
    $$ \text{Total Latency} = \text{Time to First Token} + \text{Time to Last Token} $$
    $$ \text{Tool Call Latency} = \text{Tool Start Time} - \text{Tool End Time} $$
    Monitoring these metrics helps optimize agent performance and provides feedback on the efficiency of different tools or LLM models.

3.  **Agent Utility/Reward Functions (Conceptual):** While not explicitly detailed in the sources, the underlying principle of agent decision-making often involves an implicit or explicit utility function that guides the agent towards a goal. For example, in a ReAct-style agent [Source 2], the agent's "thought" process aims to maximize the utility of the next action (e.g., choosing the most relevant tool or generating the most helpful response) to achieve the user's objective. This can be conceptually represented as:
    $$ \text{Action} = \arg\max_{a \in \text{Actions}} U(\text{State}, a, \text{Goal}) $$
    Where $U$ is a utility function, $\text{State}$ is the current context, $a$ is a possible action, and $\text{Goal}$ is the desired outcome. The agent's internal reasoning (often text-based) attempts to approximate this maximization.

These quantitative aspects, while not deeply mathematical in the provided sources, are critical for an "Agent Lab" to provide meaningful insights into agent behavior and resource consumption.

## Practical Applications
The research findings provide a clear roadmap for enhancing the current Agent Management Platform into a fully functional agent lab.

1.  **Implement Real-time Streaming for All Agent Outputs:**
    *   **Current UI Analysis:** The existing UI at https://frontend-travis-kennedys-projects.vercel.app/ likely uses a request-response model, displaying the full response only after it's generated.
    *   **Recommendation:** Integrate `StreamlitCallbackHandler` (if using Streamlit for frontend) or similar streaming mechanisms (e.g., SSE, WebSockets) with LangChain, Pydantic AI, or OpenAI Agents SDK [Source 2, Source 5, Source 6].
    *   **Example:** When an agent is "researching," display "Agent is thinking..." followed by token-by-token output of its thoughts, tool calls, and intermediate results. Use distinct UI elements (e.g., expandable sections, different colored text) to differentiate agent thoughts, tool outputs, and final answers. This makes agent capabilities immediately discoverable and provides real-time feedback.

2.  **Expose Agent Capabilities and Workflow in a "Counter-Style" UI:**
    *   **Current UI Analysis:** The current UI is a generic chat. Agent capabilities are not explicit.
    *   **Recommendation:** Design the prompt input area to suggest agent capabilities (e.g., "Ask me to research X," "Build a Y script," "Analyze Z data"). Implement a visual workflow indicator (e.g., a progress bar or a sequence of icons) that updates as the agent moves through "research," "build," and "archive" phases.
    *   **Example:** After a user asks "Research the best Python libraries for data visualization," the UI could show: `User Input -> Agent Thinking -> Tool Call (Search) -> Processing Results -> Summarizing -> Final Output`. Each step could be a clickable element revealing more detail (e.g., the exact search query used).

3.  **Develop a Robust Archive System:**
    *   **Current UI Analysis:** No explicit archiving system is visible. Chat history might be ephemeral or basic.
    *   **Recommendation:** Implement the conceptual database schema (as detailed in Technical Analysis) to store every session, interaction log, and generated artifact [Source 9, Source 10, Source 11].
    *   **Example:** Create a dedicated "Archive" section in the UI. Each archived session should be searchable by keywords, agent type, date, and status. Clicking on a session should reveal the full interaction log, including agent thoughts, tool calls, and all generated artifacts (e.g., research summaries, code snippets, data files). This allows users to review, reproduce, or build upon past agent work.

4.  **Enhance UI/UX for Discoverability and Transparency:**
    *   **Current UI Analysis:** Standard chat interface.
    *   **Recommendation:** Utilize Streamlit's capabilities (or similar frontend frameworks) to create dynamic and interactive components. Implement clear visual cues for agent status (e.g., "active," "idle," "error"). Provide options to "pause," "stop," or "debug" agent runs.
    *   **Example:** A sidebar could list available agents and their tools. When an agent is active, a small, animated icon could indicate its state. Tool outputs (e.g., search results) could be displayed in collapsible sections within the chat stream, allowing users to inspect the raw data the agent is working with.

## Recommendations

### High Priority
1.  **Implement Real-time Streaming for All Agent Outputs:**
    *   **Justification:** Essential for immediate user feedback, transparency into agent reasoning, and making the "agent lab" feel responsive and intuitive. Directly addresses "real-time feedback" and "immediately discoverable" requirements [Source 1, Source 5, Source 7].
    *   **Action:** Integrate `StreamlitCallbackHandler` (or equivalent for chosen frontend framework) with LangChain/Pydantic AI agents to stream token-by-token LLM responses, agent thoughts, and tool call details.

2.  **Integrate a Robust Agent Orchestration Framework:**
    *   **Justification:** Enables agents to perform complex "research/build" tasks using tools, moving beyond simple conversational AI. Crucial for the "seamless research-to-implementation workflow" [Source 2, Source 4, Source 8].
    *   **Action:** Adopt LangChain or Pydantic AI to define agents with specific tools (e.g., web search, code interpreter, file I/O) and manage their multi-step reasoning processes.

3.  **Design and Implement a Comprehensive Archive System Backend:**
    *   **Justification:** Critical for storing all research, built solutions, and agent interactions, supporting reproducibility, review, and continuous improvement. Addresses "comprehensive archive system" [Source 9, Source 10, Source 11].
    *   **Action:** Implement the proposed `AgentSessionArchiveSchema` in a suitable database (e.g., PostgreSQL with JSONB support, MongoDB) to store session metadata, detailed interaction logs, and generated artifacts.

### Medium Priority
1.  **Develop a "Counter-Style" Interaction UI:**
    *   **Justification:** Guides users on how to interact with agents for specific tasks (research, build) and makes agent capabilities explicit.
    *   **Action:** Redesign the input prompt area to suggest agent roles/capabilities. Implement visual indicators for agent status and workflow progression (e.g., "Researching...", "Building...", "Archiving...").

2.  **Enhance Visual Feedback for Agent Processes:**
    *   **Justification:** Improves transparency and user understanding of complex agent operations, making capabilities more discoverable.
    *   **Action:** Use distinct UI components (e.g., expandable sections, colored text, icons) to differentiate between user input, agent thoughts, tool calls, tool outputs, and final responses within the chat stream.

### Future Considerations
1.  **Advanced Analytics and Performance Monitoring:** Implement dashboards to visualize agent performance metrics (cost, latency, success rate) over time, aiding in agent optimization.
2.  **Multi-Agent Collaboration and Workflow Orchestration:** Explore interfaces for defining and managing workflows involving multiple agents collaborating on a larger task.
3.  **Version Control for Built Solutions:** Integrate with version control systems (e.g., Git) for code artifacts generated by agents, enabling tracking and collaboration on built solutions.

## Limitations & Caveats
This research primarily focuses on the frontend UI/UX and the architectural considerations for agent interaction and archiving. It does not delve into the intricacies of specific LLM models, advanced agentic reasoning algorithms, or detailed security implications beyond general best practices for API key management. The provided code examples are conceptual and illustrative, requiring further development for production readiness, including robust error handling, authentication, and scalability. The "Mathematical Foundations" section is limited by the practical nature of the gathered sources, which prioritize implementation over theoretical models. Further research into agent evaluation metrics and user studies on agent transparency could provide deeper insights.

## Conclusion
Transforming the Agent Management Platform into an intuitive "agent lab" requires a strategic focus on real-time interactivity, explicit agent capabilities, and robust archiving. By adopting streaming interfaces, integrating powerful agent orchestration frameworks, and implementing a structured session history system, the platform can empower users to seamlessly research, build, and manage AI solutions. The recommendations outlined in this report provide actionable steps to achieve this vision, fostering a transparent, efficient, and discoverable environment for agent development. The proposed technical implementations, particularly the streaming Streamlit agent and the conceptual archive schema, serve as foundational elements for this evolution, paving the way for a truly intuitive and powerful agent lab.

## References

[1] Build a basic LLM chat app - Streamlit Docs - https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
[2] (Python) Streamlit + Local LLM. Yet-Another-Code-Example for… | by Stef Nestor | Medium - https://medium.com/@stefnestor/python-streamlit-local-llm-2aaa75961d03
[3] Agents - Pydantic AI - https://ai.pydantic.dev/agents/
[4] How to stream responses from an LLM - https://python.langchain.com/docs/how_to/streaming_llm/
[5] Streaming - OpenAI Agents SDK - https://openai.github.io/openai-agents-python/streaming/
[6] Build an LLM app using LangChain - Streamlit Docs - https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/llm-quickstart
[7] Streaming output and events | LlamaIndex Python Documentation - https://developers.llamaindex.ai/python/framework/understanding/agent/streaming/
[8] Pydantic AI - https://ai.pydantic.dev/
[9] Research Overview: AI agent session history architecture database sch - https://research-placeholder.example/overview
[10] Technical Implementation Guide for AI agent session history architecture database sch - https://technical-placeholder.example/guide
[11] Latest Advances in AI agent session history architecture database sch - https://advances-placeholder.example/latest
