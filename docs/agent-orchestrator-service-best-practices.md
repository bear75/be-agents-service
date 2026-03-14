# Executive Summary

A production-grade agent orchestrator service must be designed with a focus on simplicity, security, reliability, and observability.

## When repo teams or agents are confused

**MEMORY and REPORT are key.** Resolution order: **1) Use repo** (CLAUDE.md, repo docs, code). **2) Use DARWIN** (workspace memory, priorities, machine/agent-reports). **3) Ask me over Telegram.** Do not guess. See [AGENTS_WHEN_CONFUSED.md](AGENTS_WHEN_CONFUSED.md). The core best practice is to minimize unnecessary agency, favoring direct model calls or simple workflows and only escalating to complex multi-agent systems when justified. Where orchestration is needed, it should be as deterministic as possible, for example, using plan-and-execute or graph-based (e.g., LangGraph) workflows that separate the orchestration logic from the agent's reasoning. State management is critical; orchestration state should be persisted externally, not in the model's ephemeral context, with techniques for context compaction between steps and checkpointing for long-running tasks. Security must be paramount, extending beyond prompt injection to address threats like tool misuse, memory poisoning, and cascading failures. This requires a 'principle of least privilege' for all tools and data, sandboxing for risky operations, human-in-the-loop approvals for high-impact actions, and comprehensive audit trails. Observability should be standardized using emerging conventions like OpenTelemetry for GenAI, which provides a common language for tracing the entire 'Thought -> Tool Call -> Observation' loop, and must be augmented with continuous evaluation for quality, safety, and cost. Reliability is achieved through classic software engineering patterns, including timeouts, retries with backoff, circuit breakers, output validation, and designing for graceful degradation. Finally, the entire system must operate under a formal governance framework, aligning with standards like the NIST AI RMF and OWASP guidance, which involves versioning all components (prompts, tools, models), maintaining detailed audit logs, and conducting regular red teaming and compliance checks.

# Core Principles

The fundamental principles for designing and building effective agentic systems prioritize control, transparency, and deliberate simplicity over unconstrained autonomy. The primary guiding principle is to start with the simplest possible architecture; if a task can be reliably accomplished with a direct model call and well-engineered prompts, an agent is not needed. Agentic complexity should only be introduced when simpler solutions prove inadequate. When building agents, three core principles should be followed: 1) Maintain simplicity in the agent's design, such as by creating single-responsibility agents. 2) Prioritize transparency by making the agent's reasoning process visible, for example, by explicitly showing its plans and tool choices before execution. 3) Carefully craft the agent-computer interface (ACI) through comprehensive tool documentation, strong schemas, and rigorous testing to ensure reliable and predictable interactions. A crucial overarching principle is to separate the deterministic orchestration workflow from the ambiguous, non-deterministic reasoning of the LLM. This is often achieved using plan-and-execute or graph-based architectures, where a reliable process orchestrates steps, and the LLM's role is confined to reasoning within those individual, well-defined steps, blending intelligent capabilities with robust control.

# Architectural Design Patterns

## Pattern Name

Hierarchical Supervisor/Worker

## Description

This pattern involves a multi-agent architecture with a clear division of labor. A 'supervisor' or 'manager' agent is responsible for overall planning and task decomposition. It receives a complex, high-level goal, breaks it down into smaller, manageable sub-tasks, and delegates these sub-tasks to one or more specialized 'worker' or 'specialist' agents. Each worker agent is designed to excel at a specific function (e.g., data retrieval, code execution, content generation). The supervisor coordinates the workers, manages the flow of information between them, and synthesizes their outputs to achieve the final goal.

## When To Use

This pattern is most suitable for complex, cross-domain tasks that can be logically broken down into distinct steps requiring different skills, tools, or even different underlying LLMs. For example, a research task might involve one worker agent to search the web, another to analyze data, and a third to write a summary. It helps manage complexity by isolating responsibilities.

## Considerations

Implementing this pattern introduces significant coordination overhead. It is crucial to design explicit and robust mechanisms for context handoff between the supervisor and workers to ensure each agent has the necessary information. Validation gates are needed to check the output of each worker before it's used by another or integrated into the final result. This pattern is susceptible to cascading failures, where the failure of a single worker can halt the entire process. Therefore, robust error handling, state management, and monitoring for each agent are critical. Cost can also increase due to multiple model calls across the hierarchy.


# Security Governance Frameworks

## Framework Name

NIST AI Risk Management Framework (AI RMF 1.0)

## Focus Area

AI Risk Governance

## Best For

Executives, Governance Teams, and System Architects

## Description

A comprehensive framework designed to manage risks associated with artificial intelligence. It provides a structured approach with four core functions: Govern, Map, Measure, and Manage. For agentic systems, it serves as a governance backbone, helping organizations to define accountability, map the agent's surface area (LLM, tools, data), continuously measure risks through methods like red teaming and groundedness scoring, and manage those risks with guardrails and monitoring. It is particularly useful for aligning AI security practices with broader enterprise risk management.

## Framework Name

OWASP Top 10 for Large Language Model Applications

## Focus Area

LLM Application Vulnerabilities

## Best For

Security Teams, Developers, and Red Teams

## Description

A community-driven project that identifies the ten most critical security risks for applications using Large Language Models. It covers a range of vulnerabilities including Prompt Injection, Sensitive Information Disclosure, and Supply Chain Vulnerabilities. This framework provides actionable mitigation guidance and helps teams prioritize their security efforts when building and deploying any GenAI application, including agentic systems.

## Framework Name

OWASP Top 10 for Agentic Applications (ASI)

## Focus Area

Agent-Specific Security Risks

## Best For

AI Security Specialists, Agent Developers, and Architects

## Description

A specialized extension of the OWASP LLM Top 10, this initiative focuses on the unique, high-impact risks introduced by autonomous agentic systems. It identifies threats such as Memory & Context Poisoning (ASI06), Tool Misuse & Exploitation (ASI02), Identity & Privilege Abuse (ASI03), and Cascading Failures (ASI08). This framework is essential for threat modeling and implementing specific controls for systems where AI agents can act, query data, and manage their own memory.

## Framework Name

Model Context Protocol (MCP)

## Focus Area

Secure Tool Integration and Access

## Best For

Architects and Developers

## Description

A protocol and set of best practices for standardizing secure tool access for AI models and agents. MCP promotes a defense-in-depth security model with layers for networking, authentication, authorization (e.g., capability-based ACLs), validation, and monitoring. It provides specific guidance on mitigating attacks like Server-Side Request Forgery (SSRF), making it a critical framework for building robust and secure multi-tool ecosystems for agents.

## Framework Name

OpenTelemetry GenAI Semantic Conventions

## Focus Area

Observability and Auditing

## Best For

DevOps, SRE, and Security Operations Teams

## Description

A standard for instrumenting Generative AI applications to ensure consistent and portable observability. It defines semantic conventions for tracing, metrics, and logs related to AI operations, including model calls, tool execution, retrieval steps, and token usage. Adopting these conventions is a best practice for creating comprehensive audit trails (e.g., Thought -> Tool Call -> Observation -> Response) and integrating agent telemetry with SIEM systems for continuous security monitoring and incident response.


# Owasp Top 10 For Agentic Apps

## Risk Id

ASI01

## Risk Name

Agent Goal Hijack

## Description

This risk involves an attacker manipulating an agent's inputs, memory, or tool outputs to alter its original goal or mission. For example, a memory poisoning attack could permanently alter the agent's instructions, causing it to pursue a malicious objective instead of its intended one. This represents a fundamental compromise of the agent's purpose.

## Severity

Critical

## Risk Id

ASI02

## Risk Name

Tool Misuse & Exploitation

## Description

This risk occurs when an agent uses its authorized tools in unintended or harmful ways, or when vulnerabilities in the tools themselves are exploited. An attacker could trick an agent into calling a tool with malicious parameters, leading to data exfiltration, system damage, or further system access. This highlights the need for strict input validation and sandboxing of tool execution.

## Severity

High

## Risk Id

ASI03

## Risk Name

Identity & Privilege Abuse

## Description

This risk covers scenarios where an agent's identity is spoofed or its permissions are escalated or abused. If an agent operates with excessive privileges, a compromise can have a wide blast radius. This underscores the importance of the principle of least privilege, binding agent permissions to user identity, and requiring human approvals for high-risk actions.

## Severity

High

## Risk Id

ASI05

## Risk Name

Unexpected Code Execution

## Description

This risk involves an agent being manipulated into executing arbitrary or malicious code. This can happen if the agent has access to tools like a code interpreter or shell access and is not properly sandboxed. A successful attack could lead to a full system compromise. The context shows this as a potential outcome of a chain-of-failure attack initiated by memory poisoning.

## Severity

Critical

## Risk Id

ASI06

## Risk Name

Memory & Context Poisoning

## Description

Described as a 'new frontier of Stateful attacks,' this risk involves an attacker corrupting an agent's long-term memory or short-term context. By injecting malicious or misleading information into the agent's persistence layer (e.g., a vector database), an attacker can cause lasting changes to the agent's behavior, leading to cross-session hijacking and making the attack permanent. This is a foundational risk that can enable other attacks like Agent Goal Hijack.

## Severity

Critical

## Risk Id

ASI08

## Risk Name

Cascading Failures

## Description

This risk pertains to multi-agent systems where an error or compromise in one agent can propagate and cause failures in other connected agents. This can lead to unpredictable and widespread system malfunction. It highlights the need for robust error handling, validation gates between agents, and isolating agent workloads.

## Severity

High

## Risk Id

ASI10

## Risk Name

Rogue Agents

## Description

This risk involves the creation or deployment of unauthorized agents within a system, or an existing agent becoming 'rogue' due to a severe compromise. A rogue agent could operate covertly to exfiltrate data, disrupt operations, or consume resources, acting against the interests of the system owner. This necessitates strong authentication, monitoring, and governance over agent creation and deployment.

## Severity

Critical


# Critical Security Threats And Mitigations

The security landscape for agentic systems expands significantly beyond traditional application security, introducing stateful and cascading risks. Key threats include **Prompt Injection**, where attackers manipulate LLM inputs to bypass safety controls or hijack agent goals; **Insecure Tool Usage (ASI02)**, where an agent is tricked into using its authorized tools for malicious purposes; and **Excessive Permissions**, leading to privilege abuse (ASI03) and a wide blast radius upon compromise. A particularly severe threat is **Memory Poisoning (ASI06)**, a stateful attack where an agent's long-term memory is corrupted with malicious data, leading to permanent goal hijacking and cross-session attacks. This can initiate a **Cascading Failure (ASI08)**, where one compromised agent triggers a chain reaction, potentially leading to **Unexpected Code Execution (ASI05)** if the agent has access to unsandboxed interpreters. Other critical threats include **Data Leakage** from insecure tool outputs, **Supply Chain Vulnerabilities** in underlying models or libraries, and network-level attacks like **Server-Side Request Forgery (SSRF)** when agents interact with external resources.

Actionable mitigation strategies must be multi-layered. **Identity and Access Management** is foundational, enforcing the principle of least privilege for all tools, data, and APIs. **Human-in-the-loop (HITL) approvals** must be implemented for any high-risk action, such as code execution or external data writes. **Sandboxing and Isolation** are critical; high-risk tools like code interpreters and web browsers must be run in isolated, ephemeral environments with restricted network egress. To counter memory poisoning, persistence layers must be protected, memory should be segregated per tenant, and all writes should be logged, monitored, and potentially require approval. All **inputs and outputs**, especially to and from tools, must be strictly validated and sanitized, and LLM outputs should be constrained to structured schemas before execution. For inter-agent and tool communication, secure protocols like **Model Context Protocol (MCP)** should be used to provide authentication, authorization, and SSRF defenses. Finally, a continuous security posture must be maintained through **Adversarial Testing and Red Teaming** before and during production, and comprehensive **Audit Trails** that log the entire agent lifecycle (Thought -> Tool Call -> Observation -> Response) should be integrated with SIEM systems for continuous monitoring and incident response.

# Identity And Access Management

Effective Identity and Access Management (IAM) is a cornerstone of securing agentic systems. The paramount best practice is the **principle of least privilege**, ensuring that an agent has only the minimum permissions necessary to perform its tasks. This principle should be applied across all resources, including tools, APIs, data sources, and file systems. A crucial aspect of this is to **bind agent permissions to the identity of the end-user** initiating the request; the agent should not have more access than the user it is acting for. Results returned by the agent should also be scoped and trimmed based on the user's permissions.

To manage tool access, permissions should be granularly scoped. Instead of granting broad access, use **capability-based Access Control Lists (ACLs)**, as recommended by frameworks like the Model Context Protocol (MCP), to define exactly what actions an agent can perform with a given tool. For sensitive actions, such as writing to a database, executing code, or interacting with the filesystem, permissions should not be granted by default. Instead, a **human-in-the-loop (HITL) approval flow** must be implemented, requiring explicit user confirmation before the action is executed. Platforms like OpenAI explicitly recommend keeping tool approvals enabled for this reason.

For authentication and credential management, agents should use **dedicated, short-lived credentials** managed through a secure secret vault, rather than using long-lived API keys or shared service accounts. All service-to-service traffic between agents and tools must be authenticated. Furthermore, **network isolation** provides another layer of access control; agents and their tools should be deployed within private networks (e.g., VNets) with restricted egress, and private endpoints should be used to access sensitive data sources, preventing broad network exposure.

# Agent Observability Pillars

The five pillars of agent observability expand upon the traditional three pillars of software observability (metrics, logs, and traces) to address the unique challenges of non-deterministic, agentic AI systems. The pillars are: 1) **Continuous Monitoring & Metrics**: This involves tracking key performance indicators like latency, error rates, and cost, often broken down per agent or per run. It also includes monitoring for performance drift over time. 2) **Tracing**: This provides end-to-end visibility into the agent's execution flow, capturing the entire sequence of 'Thought -> Tool Call -> Observation -> Response'. This is crucial for debugging complex, multi-step workflows and understanding the agent's reasoning process. 3) **Logging**: This involves capturing structured logs of inputs, outputs (prompts and responses), tool interactions, and state changes. For compliance and security, these logs form a comprehensive audit trail. 4) **Evaluation**: This is a new, AI-specific pillar that involves continuously assessing the quality, safety, and correctness of the agent's output. This can be done through automated methods like LLM-as-judge, scoring against 'golden datasets', and checking for groundedness, as well as through human-in-the-loop (HITL) reviews. 5) **Governance**: This pillar focuses on ensuring that agents operate within defined safety, compliance, and ethical boundaries. It involves enforcing policies, managing permissions, tracking artifact versions (prompts, models, tools), and maintaining auditability to align with frameworks like the NIST AI RMF. Together, these five pillars empower teams to detect issues, verify standards, optimize performance, and maintain trust and accountability in their AI agents.

# Opentelemetry For Ai Standards

OpenTelemetry (OTel) has established a set of semantic conventions specifically for Generative AI to standardize the telemetry data produced by AI agent and LLM applications, enabling portable and consistent observability. These conventions, while still in development, provide a structured approach for instrumenting every part of an agentic workflow. The conventions cover three main signal types: Spans, Metrics, and Events.

**Spans:**
- **Model Spans:** Represent a client call to a generative AI model. The span name should follow the format `{gen_ai.operation.name} {gen_ai.request.model}`. Key attributes include `gen_ai.operation.name` (e.g., 'chat', 'completion'), `gen_ai.provider.name`, `gen_ai.request.model`, and `gen_ai.response.model`.
- **Agent Spans:** Represent the overarching operation of an AI agent.
- **Tool Spans:** Represent the execution of a tool by an agent. The span name should be `execute_tool {gen_ai.tool.name}`. This allows for precise monitoring of tool performance and usage.
- **Conversation ID:** The attribute `gen_ai.conversation.id` is recommended to link all related spans within a single conversation or session, which is crucial for tracing complex interactions in systems like OpenAI Assistant threads or AWS Bedrock agent sessions.

**Metrics:**
Standardized metrics are defined to monitor cost and performance consistently across different models and providers.
- `gen_ai.client.token.usage`: Measures the number of input and output tokens, which is essential for cost tracking.
- `gen_ai.client.operation.duration`: Measures the latency of LLM calls.
- `gen_ai.server.time_per_output_token`: A server-side metric to gauge model generation speed.
These metrics are enriched with attributes like `gen_ai.provider.name` and `gen_ai.request.model` for detailed analysis.

**Events:**
The specification also defines conventions for events, allowing for fine-grained logging of occurrences within a span's lifetime.

Adopting these conventions allows developers to use any OTel-compatible observability platform to gain deep insights into their AI systems, from high-level performance down to individual tool calls and token usage, ensuring a comprehensive audit trail ('Thought -> Tool Call -> Observation -> Response') and facilitating interoperability.

# Observability Platforms And Tools

## Platform Name

LangSmith / LangFuse

## Capabilities

Provides framework-native, end-to-end observability and tracing for applications built with LangChain and LangChain.js (LangSmith) or other Python frameworks (LangFuse). Capabilities include detailed tracing of agent steps (thoughts, tool calls, observations), logging of prompts and responses, and running evaluations on datasets to track quality and regressions.

## Best For

Development teams using the LangChain or LangFuse frameworks who need deep, integrated visibility into the entire lifecycle of their agentic applications, from debugging to evaluation.

## Platform Name

Azure AI Foundry

## Capabilities

An enterprise-grade platform offering a suite of tools for agent observability and governance. Key capabilities include an 'AI Red Teaming Agent' to scan for vulnerabilities before production, a unified dashboard for continuous monitoring of live traffic, tracing, and running continuous evaluations to detect drift or regressions. It integrates governance as a core component.

## Best For

Enterprise AI operations and security teams focused on pre-production validation, continuous production monitoring, and ensuring the safety, compliance, and reliability of multi-agent workflows.


# State And Memory Management

Effective state and memory management in an agent orchestrator involves treating the model's context window as ephemeral and stateless. The core principle is to externalize and persist the orchestration state—including task progress, tool results, and critical decisions—in a durable store. This approach is crucial for reliability and recovery. To handle the limited context windows of LLMs, techniques such as summarization or selective pruning should be used to compact the context passed between agents or across different steps of a workflow. For long-running and complex tasks, checkpointing is a vital practice. Frameworks like LangGraph provide built-in persistence primitives and checkpointers that save the state of the graph, ensuring that workflows can be resumed and are reproducible across deployments. A clear distinction should be made between conversational/session state and long-term knowledge. For long-term memory, the recommended practice is to use explicit, query-time retrieval mechanisms like Retrieval-Augmented Generation (RAG), vector stores, or knowledge graphs, rather than allowing agents to write to memory automatically. This must be paired with strong memory governance, including memory isolation per user/tenant, implementing Time-to-Live (TTL) and retention policies, strict access controls, tracking data provenance, and establishing approval flows for memory writes. Security is paramount, as persistence layers are vulnerable to stateful attacks like 'Memory Poisoning' and cross-session hijacking. Therefore, it is essential to protect these layers, segregate memory and RAG data per tenant, and log all read/write operations for auditing.

# Reliability And Error Handling

Building robust and reliable agentic systems requires implementing a multi-layered error handling and resilience strategy. For dependencies on external services like LLMs and tools, standard reliability patterns such as timeouts, retries with exponential backoff, and circuit breakers are essential to prevent system-wide failures. Instead of failing silently, orchestrators should be designed for graceful degradation, which can involve skipping optional steps, falling back to simpler heuristic methods, or switching to alternative, potentially smaller models. A critical practice is to validate the output of each agent before it is propagated to a downstream component. If an output is identified as low-confidence, malformed, or off-topic, the orchestrator should have logic to request clarification, retry the step, or halt the workflow and surface a clear error to the user or a monitoring system. For long-running or multi-agent workflows, using checkpoints and enabling resumability is crucial for recovering from failures without losing progress; this is a core feature of frameworks like LangGraph. When agents perform actions that modify external state (e.g., writing to a database), it is best to design idempotent tool operations. Furthermore, the system should include compensating actions and rollback procedures to undo external writes in case of failure. Finally, integrating a Human-in-the-Loop (HITL) process for ambiguous, high-impact, or high-risk decisions—through mechanisms like approval queues, review UIs, and defined escalation paths—adds a critical layer of safety and reliability.

# Performance And Cost Optimization

Optimizing the performance and cost of an agent orchestrator involves a combination of strategic model selection, efficient resource utilization, and continuous monitoring. A key technique is to assign the right model for each task; smaller, cheaper, and faster models should be used for simpler sub-tasks like data extraction, classification, or formatting, while reserving large, frontier models for steps that demand complex reasoning and planning. To control expenses, it is crucial to monitor token consumption and overall cost on a per-agent and per-orchestration-run basis. This can be standardized using OpenTelemetry GenAI semantic conventions, which define metrics like `gen_ai.client.token.usage`. Implementing caching strategies for prompts, retrieved context from RAG systems, and intermediate results can significantly reduce redundant API calls and computation. To improve perceived latency for the end-user, orchestrators should stream partial outputs as they are generated. Performance can also be enhanced by parallelizing independent sub-tasks, though this must be managed with rate limiting and concurrency controls to avoid overwhelming downstream services. Where applicable, batching compatible requests can further improve efficiency. Finally, controlling token budgets by using context compaction techniques between agent handoffs serves the dual purpose of managing costs and staying within model context limits.

# Testing And Evaluation Strategies

## Strategy Name

Adversarial Testing / AI Red Teaming

## Description

This strategy involves proactively simulating attacks to identify and validate vulnerabilities in agentic systems before they are exploited in production. It tests for risks like prompt injection, tool misuse, memory poisoning, and cascading failures in multi-agent workflows. It is a critical step for ensuring the security and robustness of agents.

## Example Tool

Azure AI Foundry’s AI Red Teaming Agent

## Strategy Name

Offline Evaluation on Golden Datasets

## Description

This involves creating a curated 'golden dataset' of inputs and expected high-quality outputs for core tasks. This dataset is used in CI/CD pipelines to run regression evaluations, ensuring that changes to prompts, models, or tools do not degrade performance, quality, or safety. It provides a baseline for measuring correctness.

## Example Tool

LangSmith or other evaluation frameworks

## Strategy Name

LLM-as-Judge Evaluation

## Description

This method uses a powerful large language model (the 'judge') to score the quality of an agent's output based on a predefined rubric. It's a scalable way to automate the evaluation of subjective qualities like helpfulness, coherence, or adherence to a specific persona, which can be difficult to measure with traditional metrics.

## Example Tool

Custom evaluation scripts using a frontier model API

## Strategy Name

Groundedness Scoring

## Description

Specifically for Retrieval-Augmented Generation (RAG) systems, this evaluation measures whether the agent's response is factually supported by the retrieved context. It is essential for preventing hallucinations and ensuring the agent provides trustworthy information based only on the provided source documents.

## Example Tool

Microsoft Foundry Agent Service (as part of Continuous Evaluation)

## Strategy Name

Continuous Evaluation on Live Traffic

## Description

This strategy involves applying evaluation metrics (such as quality scores, safety checks, and groundedness) to a sample of real-world production traffic. It allows teams to monitor for performance drift, regressions, or emerging safety issues in real-time and set up alerts to be notified of problems immediately.

## Example Tool

Azure AI Foundry


# Key Orchestration Frameworks And Interfaces

## Name

LangChain/LangGraph

## Type

Framework

## Description

A popular open-source framework for developing applications powered by language models. LangGraph is a library built on top of LangChain that allows for the creation of stateful, multi-agent applications as cyclical graphs. It is particularly noted for its built-in persistence layer and checkpointers, which enable durable, resumable, and fault-tolerant agentic workflows.

## Name

Microsoft Azure AI Foundry

## Type

Platform

## Description

A platform service for building and operating AI agents. It provides a comprehensive environment that integrates a NIST-based security governance framework for managing risks like memory poisoning. Key features include advanced agent observability, continuous monitoring, and an AI Red Teaming service to simulate attacks and validate the security of multi-agent workflows before production.

## Name

OpenAI Assistants

## Type

Platform

## Description

A feature of the OpenAI API that allows developers to build agent-like experiences with persistent threads and access to tools like Code Interpreter and Retrieval. Safety best practices for this platform emphasize enabling explicit tool approvals, where end-users must confirm every operation an agent attempts to perform, providing a human-in-the-loop guardrail.

## Name

Model Context Protocol (MCP)

## Type

Protocol

## Description

A standardized protocol designed to facilitate secure and interoperable communication between language models and external tools or services. It promotes a defense-in-depth security model with layers for authentication, authorization (e.g., using capability-based ACLs), input/output validation, and monitoring. It also includes best practices for mitigating security risks like Server-Side Request Forgery (SSRF).

## Name

OpenTelemetry GenAI Semantic Conventions

## Type

Standard/Protocol

## Description

A set of standards within the OpenTelemetry project for instrumenting generative AI applications to ensure consistent and portable observability. It defines semantic conventions for tracing and metrics related to LLM calls, tool execution, token usage, and conversation tracking. Adopting these conventions allows for end-to-end visibility across different frameworks and vendor platforms.


# Common Pitfalls And Anti Patterns

When implementing agent orchestration, several common pitfalls and anti-patterns can undermine the system's reliability, security, and efficiency. A primary mistake is creating unnecessary complexity by defaulting to a multi-agent architecture when a simpler approach, like a direct model call or a single agent, would suffice. For concurrent or parallel patterns, a critical anti-pattern is allowing agents to share and modify the same state directly, which can lead to race conditions and unpredictable behavior; state should be managed externally and passed explicitly. Another pitfall is ignoring resource constraints (like API rate limits, memory, or CPU) when designing concurrent orchestration, which can lead to system instability and failures. From a reliability standpoint, a common error is failing to design for graceful degradation; the system should not fail silently but should have fallbacks, retry mechanisms, or the ability to skip optional steps. Security anti-patterns include neglecting the expanded threat surface of agentic systems, such as failing to protect long-term memory from 'poisoning' attacks, granting excessive permissions to tools, not sandboxing risky operations, and overlooking the potential for cascading failures where an error in one agent triggers a chain reaction of faults across the system. Finally, a governance anti-pattern is to treat the agent as a black box, replacing auditable processes with unconstrained AI, rather than blending intelligence with deterministic control and governance.
