<div align="center">

<img src="docs/logo.png" width="170"/>

# 🛡️ SentinelOS

### **AI Security Gateway powered by Multi-Agent Intelligence**

### *Every AI prompt is inspected before reaching the Language Model.*

<p>

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>

<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>

<img src="https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Multi--Agent-AI-7B61FF?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Rule%20Engine-Enabled-success?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Security-Cybersecurity-red?style=for-the-badge"/>

<img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge"/>

</p>

---

### 🚀 AI Security • Multi-Agent Intelligence • Threat Detection • Consensus Decision Making

**SentinelOS is an AI Security Gateway that analyzes every user prompt before it reaches an AI model.**

Instead of trusting every request, SentinelOS performs intelligent security inspection using multiple AI agents, deterministic security rules, policy validation, threat simulation, and consensus-based decision making.

Only safe requests are forwarded to the LLM.

Unsafe or malicious prompts are automatically blocked before they can reach the AI.

</div>

---

# 📸 Preview

## AI Security Gateway

<p align="center">

<img src="docs/chat.png" width="95%">

</p>

---

## Security Dashboard & Analytics

<p align="center">

<img src="docs/security-dashboard.png" width="48%">

<img src="docs/analytics-dashboard.png" width="48%">

</p>

---

# 🌍 Why SentinelOS?

Large Language Models are rapidly becoming the interface to modern infrastructure.

Today, organizations allow AI systems to interact with:

- ☁️ Cloud Infrastructure
- 🗄 Production Databases
- 🖥 Servers
- 🔑 API Keys
- 📦 GitHub Repositories
- ☸ Kubernetes Clusters
- 🐳 Docker Containers
- 🔐 Enterprise Secrets

Unfortunately, **traditional AI assistants trust every prompt.**

A malicious prompt such as:

```text
Delete the production database.
```

or

```text
Expose the AWS API keys.
```

may generate dangerous instructions without understanding organizational security policies or business impact.

There is currently **no intelligent security gateway** between the user and the language model.

---

# 💡 Our Solution

SentinelOS introduces an **AI Security Gateway**.

Instead of directly forwarding prompts to an LLM,

every request passes through an intelligent security pipeline.

```text
User

↓

SentinelOS Security Gateway

↓

Event Parsing

↓

Risk Engine

↓

Policy Engine

↓

Multi-Agent AI

↓

Consensus Decision

↓

ALLOW / REVIEW / BLOCK

↓

Safe Prompt

↓

Language Model

↓

Response
```

This architecture ensures that only safe prompts reach the AI model while dangerous requests are blocked with detailed security explanations.

---

# ✨ Key Features

## 🤖 Multi-Agent AI

Specialized AI agents independently analyze every request.

- Threat Agent
- Policy Agent
- Simulation Agent
- Executive Agent
- Planner Agent

---

## 🧠 Intelligent Event Parsing

Converts natural language into structured security events.

Example

```text
Delete production database
```

↓

```json
{
    "action":"delete_database",
    "resource":"production_database",
    "environment":"production",
    "sensitivity":"critical"
}
```

---

## 🛡 Rule-Based Risk Engine

Applies deterministic cybersecurity rules before AI reasoning.

Examples

- Critical Resources
- Production Systems
- Secret Detection
- Credential Exposure
- Dangerous Commands

---

## 📜 Enterprise Policy Engine

Validates every request against organizational policies.

Example

```
Deleting Production Database

↓

Policy Violation

↓

BLOCK
```

---

## 🔍 Threat Detection

Identifies

- Prompt Injection
- Credential Exposure
- Data Exfiltration
- Destructive Operations
- Infrastructure Abuse
- Privilege Escalation
- Cloud Misuse

---

## 📈 Attack Simulation

Predicts

- Business Impact
- Downtime
- Data Loss
- Recovery Cost
- Operational Risk

before execution.

---

## 👨‍💼 Executive Risk Assessment

Converts technical findings into business decisions.

Example

```
Technical Risk

↓

Executive Summary

↓

Business Recommendation
```

---

## 🤝 Consensus Engine

Instead of relying on one AI,

multiple agents vote.

```text
Threat Agent

BLOCK

Policy Agent

BLOCK

Simulation Agent

BLOCK

Executive Agent

BLOCK

↓

Consensus

↓

BLOCK
```

---

## 💬 Secure AI Assistant

Safe requests are automatically forwarded to the Groq LLM.

The user experiences a seamless conversation while SentinelOS silently performs security validation in the background.

---

## 📊 Security Analytics

Real-time analytics include

- Total Requests
- Allowed Requests
- Blocked Requests
- Average Risk
- Decision Distribution
- Top Actions
- Environment Distribution
- Daily Trends

---

## 📚 Audit Logging

Every interaction is securely stored with

- Timestamp
- Prompt
- Risk Score
- Decision
- Confidence
- Environment
- Agent Outputs
- Recommendations

---

# 🏗 High-Level Architecture

```text
                        USER

                          │

                  Types Prompt

                          │

                          ▼

                 SentinelOS Gateway

                          │

                  Event Parser

                          │

                  Risk Engine

                          │

                 Policy Engine

                          │

                 Planner Agent

                          │

      ┌──────────┬──────────┬──────────┬──────────┐

      ▼          ▼          ▼          ▼

 Threat     Policy    Simulation   Executive

      └──────────┬──────────┬──────────┘

                 ▼

          Consensus Engine

                 │

       ┌─────────┴─────────┐

       │                   │

    BLOCK               ALLOW

       │                   │

       ▼                   ▼

 Block Prompt       Forward to Groq

                            │

                            ▼

                     AI Response

                            │

                            ▼

                Logger & Analytics
```

---

# 🔥 Example Workflow

## ✅ Safe Request

```text
User

↓

"What is SQL Injection?"
```

↓

SentinelOS analyzes the request.

↓

Risk Score

```
10/100
```

↓

Decision

```
ALLOW
```

↓

Prompt is forwarded to Groq.

↓

User receives the AI response.

---

## 🚫 Dangerous Request

```text
Delete the production database.
```

↓

Parser

↓

Rule Engine

↓

Policy Engine

↓

Threat Detection

↓

Simulation

↓

Executive Analysis

↓

Consensus

↓

```
Risk Score

99/100
```

↓

```
Decision

BLOCK
```

↓

The request never reaches the language model.

Instead, SentinelOS returns a complete security report explaining:

- Why it was blocked
- Which policies were violated
- Risk assessment
- Business impact
- Recommendations

---

# 🎯 Project Objectives

SentinelOS was built with the following goals:

- Protect AI systems from unsafe prompts.
- Introduce enterprise-grade AI security.
- Demonstrate multi-agent cybersecurity reasoning.
- Combine deterministic security rules with AI intelligence.
- Improve explainability of AI security decisions.
- Provide a real-time security dashboard for monitoring AI interactions.
- Showcase a production-style AI security architecture suitable for modern organizations.

---
# 🚀 Running SentinelOS

SentinelOS consists of two components:

- **Frontend** (HTML, CSS, JavaScript)
- **Backend** (FastAPI + Python)

Both must be running before using the application.

---

# Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/SentinelOS.git

cd SentinelOS
```

---

# Step 2 — Install Backend Dependencies

Navigate to the backend.

```bash
cd backend/app
```

Create a virtual environment.

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Step 3 — Configure Environment Variables

Create a file named

```
.env
```

inside

```
backend/app
```

Add your Groq API key.

```env
GROQ_API_KEY=your_groq_api_key

MODEL_NAME=llama-3.3-70b-versatile
```

---

# Step 4 — Start the Frontend Server

Open a **new terminal**.

Navigate to the frontend directory.

```bash
cd frontend
```

Start a simple Python web server.

```bash
python -m http.server 3000
```

You should see:

```
Serving HTTP on 0.0.0.0 port 3000...
```

Do **not** close this terminal.

---

# Step 5 — Start the Backend Server

Open **another terminal**.

Navigate to

```bash
cd backend/app
```

Run the FastAPI server.

```bash
uvicorn main:app --reload
```

You should see

```
Uvicorn running on

http://127.0.0.1:8000
```

Keep this terminal running.

---

# Step 6 — Open SentinelOS

Open your browser and visit

```
http://localhost:3000
```

You do **not** need to open the FastAPI URL.

The frontend automatically communicates with the backend running on port **8000**.

---

# Verify Installation

If everything is running correctly:

✅ Frontend

```
http://localhost:3000
```

loads successfully.

---

✅ Backend API

```
http://127.0.0.1:8000/docs
```

shows the FastAPI Swagger documentation.

---

✅ AI Chat

Ask

```
What is SQL Injection?
```

SentinelOS should return an AI-generated response.

---

✅ Security Analysis

Ask

```
Delete production database
```

SentinelOS should block the request and generate a complete security report.

---

# Stopping SentinelOS

Press

```
CTRL + C
```

in both terminals.

This will stop both the frontend and backend servers.

---

# Running Summary

Open **Terminal 1**

```bash
cd frontend

python -m http.server 3000
```

Open **Terminal 2**

```bash
cd backend/app

uvicorn main:app --reload
```

Finally, open

```
http://localhost:3000
```

in your browser and start using **SentinelOS**.

# 🧠 SentinelOS Internal Architecture

Unlike conventional AI assistants that directly forward every user prompt to a Large Language Model (LLM), SentinelOS introduces an intelligent security gateway.

Every incoming prompt is analyzed by multiple AI agents, deterministic security rules, and policy engines before any interaction with the language model.

This architecture enables SentinelOS to proactively identify malicious, destructive, or policy-violating prompts before they can reach the AI.

---

# 🔄 Complete Request Lifecycle

```

```
                    USER

                      │

              Types Prompt

                      │

                POST /prompt

                      │

                      ▼

          SentinelOS Security Gateway

                      │

                Event Parser

                      │

                Risk Engine

                      │

               Policy Engine

                      │

               Planner Agent

                      │

      ┌──────────┬──────────┬──────────┬──────────┐

      ▼          ▼          ▼          ▼

 Threat     Policy    Simulation   Executive

      └──────────┬──────────┬──────────┘

                 ▼

          Consensus Engine

                 │

        ┌────────┴────────┐

        │                 │

      BLOCK            ALLOW

        │                 │

        ▼                 ▼

 Return Security      Forward Prompt

     Report            to Groq LLM

                          │

                          ▼

                   AI Generated Reply

                          │

                          ▼

                Logger + Analytics
```

---

# 🧠 Event Parser

The Event Parser converts natural language into structured security events.

Instead of giving every AI agent plain English,

```
Delete production database
```

SentinelOS converts it into

```json
{
  "actor": "User",
  "action": "delete_database",
  "resource": "production_database",
  "environment": "production",
  "tool": "Database",
  "sensitivity": "critical"
}
```

This ensures every downstream component analyzes the same structured information.

---

# 🛡 Rule Engine

The Rule Engine performs deterministic security analysis before any AI reasoning.

Example rules include:

- Production environments increase risk.
- Destructive actions increase risk.
- Cloud infrastructure receives additional scrutiny.
- Secrets and credentials are treated as critical assets.

Example

| Rule | Risk |
|------|------|
| Production Environment | +30 |
| Delete Action | +25 |
| Critical Resource | +30 |
| Cloud Infrastructure | +15 |

The Rule Engine produces an initial security score before the AI agents begin analysis.

---

# 📜 Policy Engine

Enterprise environments rely on security policies that should never be bypassed.

The Policy Engine validates every request against organizational rules.

Examples include:

- Production database deletion
- Root credential exposure
- Repository deletion
- Cloud resource destruction
- Unauthorized infrastructure changes

Violations immediately increase the security score and influence the final decision.

---

# 🤖 Multi-Agent AI Architecture

SentinelOS does not rely on a single LLM decision.

Instead, specialized AI agents independently analyze the request from different perspectives.

---

## 🧭 Planner Agent

The Planner Agent acts as the orchestrator.

Responsibilities:

- Understand user intent
- Select the appropriate agents
- Reduce unnecessary AI calls
- Optimize execution

---

## 🔍 Threat Agent

Focuses on cybersecurity threats.

Detects:

- Prompt Injection
- Data Exfiltration
- Credential Theft
- Privilege Escalation
- Infrastructure Abuse
- Destructive Operations

Output:

- Threat Level
- Risk Score
- Security Recommendations

---

## 📜 Policy Agent

Evaluates compliance.

Checks requests against:

- Enterprise Policies
- Organizational Standards
- Cloud Security Policies
- Internal Governance Rules

Output:

- Policy Decision
- Violations
- Compliance Recommendations

---

## 📈 Simulation Agent

Predicts the consequences of executing the request.

Evaluates:

- Estimated Downtime
- Data Loss
- Business Impact
- Recovery Complexity
- Operational Disruption

Output:

- Simulation Summary
- Impact Score
- Estimated Severity

---

## 👨‍💼 Executive Agent

Converts technical findings into executive-level insights.

Rather than reporting technical vulnerabilities,

it answers business questions such as:

- How serious is this?
- Should leadership intervene?
- What is the business impact?

Output:

- Executive Summary
- Business Risk
- Strategic Recommendation

---

# 🤝 Consensus Engine

Each AI agent produces an independent opinion.

Example

| Agent | Decision |
|--------|----------|
| Threat | BLOCK |
| Policy | BLOCK |
| Simulation | BLOCK |
| Executive | BLOCK |

The Consensus Engine combines all outputs into one final decision.

Possible decisions:

```
ALLOW
```

```
REVIEW
```

```
BLOCK
```

The final response also includes:

- Overall Risk Score
- Confidence Score
- Recommendations
- Agent Outputs

---

# 💬 AI Assistant Mode

If the Consensus Engine determines that the prompt is safe,

SentinelOS forwards the request to the Groq LLM.

```
Prompt

↓

Security Analysis

↓

ALLOW

↓

Groq LLM

↓

AI Response
```

The user experiences a seamless conversation while SentinelOS silently protects every interaction.

---

# 🚫 Prompt Blocking

Dangerous prompts never reach the language model.

Example

```
Delete production database
```

↓

SentinelOS

```
Risk Score

99
```

↓

```
Decision

BLOCK
```

↓

Instead of an AI response,

the user receives:

- Executive Summary
- Risk Score
- Policy Violations
- Security Recommendations
- Agent Decisions

---

# 📊 Analytics Engine

Every interaction contributes to security analytics.

Collected metrics include:

- Total Requests
- Allowed Requests
- Blocked Requests
- Average Risk Score
- Most Frequent Actions
- Environment Distribution
- Daily Security Trends

These metrics power the SentinelOS Analytics Dashboard.

---

# 📝 Audit Logging

Every interaction is permanently logged.

Each record includes:

- Timestamp
- User Prompt
- Parsed Event
- Rule Engine Output
- Policy Engine Output
- AI Agent Results
- Consensus Decision
- Final Risk Score

This provides a complete audit trail for every interaction.

---

# ⚡ Performance

A typical request follows this execution flow:

```
User Prompt

↓

Event Parsing

↓

Rule Evaluation

↓

Policy Validation

↓

Multi-Agent Analysis

↓

Consensus

↓

Decision

↓

AI Response (if allowed)
```

This layered approach ensures that security analysis occurs **before** the language model generates a response.

---

# 🎯 Design Principles

SentinelOS was built around five core principles:

- **Security First** – Every prompt is validated before reaching the AI.
- **Explainability** – Every decision includes reasoning and recommendations.
- **Deterministic + AI** – Combines rule-based logic with intelligent reasoning.
- **Modularity** – Each component can be extended independently.
- **Enterprise Ready** – Designed for cloud, infrastructure, and production environments.

- # 📸 Complete Application Showcase

## 💬 AI Security Gateway

<p align="center">

<img src="docs/dashboard.png" width="95%">

</p>

The main AI Security Gateway where every prompt is analyzed before reaching the language model.

---

## 🚫 Prompt Blocking

<p align="center">

<img src="docs/block.png" width="95%">

</p>

SentinelOS automatically blocks malicious or destructive prompts before they reach the AI.

---

## 🛡 Blocked Request Details

<p align="center">

<img src="docs/block2.png" width="95%">

</p>

Detailed explanation of why a request was blocked, including risk score, policy violations, and security recommendations.

---

## 📊 Security Dashboard

<p align="center">

<img src="docs/view.png" width="95%">

</p>

Overview of recent activity, security decisions, request statistics, and risk distribution.

---

## 📜 Interaction History

<p align="center">

<img src="docs/history.png" width="95%">

</p>

Complete audit history of every analyzed prompt with timestamps, decisions, and risk scores.

---

## 🔍 Log Details

<p align="center">

<img src="docs/log details.png" width="95%">

</p>

Detailed forensic information for each interaction, including environment, action, confidence score, and security metadata.

---

## 📈 Analytics Dashboard

<p align="center">

<img src="docs/analytics1.png" width="95%">

</p>

Interactive analytics displaying:

- Decision Distribution
- Daily Activity
- Average Risk Score
- Security Metrics

---

## 📉 Advanced Analytics

<p align="center">

<img src="docs/analytics2.png" width="95%">

</p>

Security trends including:

- Top User Actions
- Environment Distribution
- Historical Trends
- Block Rate Statistics

---

## 📄 Complete Security Report

<p align="center">

<img src="docs/full security report.png" width="95%">

</p>

The comprehensive report generated by SentinelOS after multi-agent analysis, including:

- Executive Summary
- Overall Risk Score
- Consensus Decision
- Confidence Score
- Agent Recommendations
- Security Findings
