
---

# 📜 Project Requirements Document (PRD)

**Project Name:** AI Summarizer  
**Lead Developer:** Dr. Arpita Paul  
**Framework:** BMAD (Build, Manage, Architect, Deploy)  
**Core Objective:** A private, local-first text summarization engine for scientific and narrative analysis.

---

## 1. Project Overview
A containerized microservices application that leverages local LLM inference (**Ollama**) to summarize text via a **FastAPI** backend and a **Streamlit** frontend. The system is designed to handle dense reports and narrative data without sending information to the cloud.

## 2. Technical Stack (The Strata)

| Layer | Technology | Responsibility |
| :--- | :--- | :--- |
| **Frontend** | Streamlit (Python) | User interface, text input, and Markdown rendering. |
| **Backend** | FastAPI (Python) | API orchestration, prompt engineering, and Ollama integration. |
| **Inference** | Ollama  | Local LLM hosting and execution (summarizer-model). |
| **Infrastructure** | Docker | Containerization and service orchestration. |

---

## 3. BMAD Implementation Strategy

### **A - Architect (Structure)**
The application follows a **three-tier microservices architecture**:
1.  **UI Tier:** Communicates with the Logic Tier via REST API.
2.  **Logic Tier:** Bridges the UI and the Inference engine. It is responsible for "cleaning" the text and wrapping it in a scientific summary prompt.
3.  **Inference Tier:** Runs as a standalone service, accessible only by the Logic Tier.

### **B - Build (Construction)**
* **Multi-Stage Builds:** Dockerfiles will be optimized to keep images lean.
* **Service Naming:** Internal DNS will allow services to communicate using hostnames: `http://api:8000` and `http://ollama:11434`.

### **M - Manage (Operational Logic)**
* **Environment Control:** All configurations (Port numbers, Model names) will be stored in a `.env` file.
* **Volume Persistence:** Ollama models will be stored in a Docker Volume to prevent re-downloading on container restart.

### **D - Deploy (Execution)**
* **Orchestration:** Deployment is a single-action command: `docker-compose up --build`.
* **Hardware:** Optimized for MacBook Air (M-series) using Apple Silicon acceleration where possible.

---

## 4. Functional Requirements

### **User Features**
* **Input Text:** A large text area for pasting reports or stories.
* **Summarization Toggle:** A button to trigger the inference process.
* **Result Display:** A dedicated area for the AI-generated summary.
* **Status Indicators:** Real-time feedback (spinners/toasts) while the model is processing.

### **System Features**
* **REST API:** A `/summarize` endpoint that accepts JSON payloads.
* **Prompt Template:** A pre-defined "Scientific Persona" prompt to ensure summaries are objective and concise.
* **Error Handling:** Graceful failure if the Ollama service is unreachable or the model is missing.

---

## 5. Success Criteria
* **Privacy:** 0% of user data leaves the local Docker network.
* **Portability:** The entire stack builds and runs on any machine with Docker installed.
* **Clarity:** The system successfully condenses text by at least 60% while retaining core facts.

---

## 6. Roadmap
1.  **Phase 1:** Setup Directory Structure & Environment files.
2.  **Phase 2:** Develop FastAPI Backend and test with local Ollama.
3.  **Phase 3:** Develop Streamlit Frontend.
4.  **Phase 4:** Dockerize and Orchestrate with Compose.

---
