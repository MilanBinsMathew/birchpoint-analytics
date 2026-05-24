# Project Plan: Enterprise FinOps AI Analyst

## Overview
This document outlines the step-by-step plan to build an advanced, open-source Financial Analysis AI. By combining Visual AI (ColPali), Time-Aware Memory (Temporal GraphRAG), and a Multi-Agent team (LangGraph), this system will read complex Indian financial filings (BSE/NSE), understand historical trends, and answer complex financial questions with pinpoint accuracy.

---

## Phase 1: Foundation & Data Collection (Weeks 1-2)
**Goal:** Gather data and set up the core environment.
* **Task 1.1: System Setup.** Install Python, Docker, and initialize the Git repository.
* **Task 1.2: Data Sourcing.** Write a simple script to download public PDF financial reports (Quarterly Earnings, Balance Sheets) for a set of target companies from the BSE/NSE websites.
* **Task 1.3: Document Conversion.** Instead of extracting text (which breaks tables), convert PDF pages into high-resolution images. This prepares them for our Visual AI.

## Phase 2: The Visual Retrieval Engine (Weeks 3-4)
**Goal:** Enable the AI to "see" documents like a human, preserving tables and charts.
* **Task 2.1: Implement ColPali.** Set up the ColPali Vision-Language Model. Process the PDF images through this model to generate visual embeddings (mathematical representations of the images).
* **Task 2.2: Vector Database Setup.** Install and configure **Qdrant** (Open Source). Store the visual embeddings here so the system can quickly search for relevant pages later.

## Phase 3: The Time-Aware Memory Graph (Weeks 5-6)
**Goal:** Build a relationship map (Knowledge Graph) that understands time (e.g., Q1 vs. Q2).
* **Task 3.1: Graph Database Setup.** Launch **Neo4j** via Docker.
* **Task 3.2: Entity Extraction.** Use a fast local AI (like Llama-3-8B) to read summaries and extract facts: Companies, Competitors, Financial Metrics, and Quarters.
* **Task 3.3: Temporal Linking.** Insert these facts into Neo4j. Crucially, attach a `valid_from` and `valid_to` date to every relationship. This prevents the AI from mixing up 2024 revenue with 2025 revenue.

## Phase 4: The Agent Team (LangGraph) (Weeks 7-8)
**Goal:** Create a team of AI agents that work together to answer questions.
* **Task 4.1: The Router Agent.** Build the "manager." When a user asks a question, this agent decides if it needs to look at the visual PDFs, the Graph database, or both.
* **Task 4.2: The Financial Analyst Agent.** This agent writes Python code to do the math (e.g., calculating Year-over-Year growth from the retrieved data) to ensure zero mathematical hallucinations.
* **Task 4.3: The Critic Agent.** Build a self-correction loop. Before showing the answer to the user, this agent double-checks the math and the source documents. If it's wrong, it tells the Analyst to try again.

## Phase 5: Premium Enterprise UI (Weeks 9-10)
**Goal:** Build a beautiful, trustworthy interface.
* **Task 5.1: Chainlit Integration.** Connect the LangGraph team to a Chainlit frontend.
* **Task 5.2: Enterprise Styling.** Apply custom CSS and a configuration file to make it look like a premium hedge-fund tool (deep navy backgrounds, subtle gold/teal accents, clean typography).
* **Task 5.3: Deployment.** Containerize the entire stack with Docker Compose and deploy to a cloud provider (e.g., RunPod or a local server with a GPU).

---
*End of Plan*