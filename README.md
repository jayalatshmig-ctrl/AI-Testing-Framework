# AI Testing Framework

## Project Overview
This repository contains a hands-on AI Testing Framework developed using Python and locally hosted Large Language Models (LLMs) through Ollama.

The framework focuses on testing AI-generated responses for consistency, quality, and reliability.

## Technologies Used
- Python
- Ollama
- Qwen 2.5 (3B)
- REST API (Python Requests)
- JSON
- Git and GitHub

## Projects

### Day 12 – Consistency Testing
**Objective:** Evaluate whether an AI model provides consistent answers.

Key features:
- Repeated response testing
- Textual consistency validation
- Paraphrase consistency testing
- JSON-based test data
- Execution report generation

### Day 13 – LLM-as-a-Judge
**Objective:** Evaluate AI-generated responses using an LLM as an automated judge.

Key features:
- Relevance evaluation
- Accuracy evaluation
- Completeness evaluation
- Clarity evaluation
- Structured JSON scoring
- Judge response validation
- PASS, FAIL, REVIEW, INVALID and ERROR reporting

## Project Structure

```text
AI-Testing-Framework/
│
├── Day-12-Consistency-Testing/
│   ├── day12_pharaphase_consistencyTesting.py
│   ├── day12_pharaphase_consistency_testing.json
│   └── consistency_report.json
│
├── Day-13-LLM-as-a-Judge/
│   ├── day13_llm_judge.py
│   ├── day13_judge_test_cases.json
│   └── day13_judge_execution_report.json
│
└── README.md
```

## Prerequisites
- Python installed
- Ollama installed and running
- Qwen 2.5 3B model downloaded
- Python Requests library

## Setup

Install the required Python library:

```bash
pip install requests
```

Download the model:

```bash
ollama pull qwen2.5:3b
```

Start Ollama and execute the Python scripts from their respective project folders.

### Day 12

```bash
python day12_pharaphase_consistencyTesting.py
```

### Day 13

```bash
python day13_llm_judge.py
```

## Learning Objectives
- AI response validation
- LLM consistency testing
- LLM-as-a-Judge evaluation
- Python-based test automation
- JSON-driven test execution
- AI testing report generation

## Future Enhancements
- Hallucination testing
- RAG testing
- Agentic AI testing
- Jenkins CI/CD integration
- Advanced AI evaluation metrics

## Author
AI Testing | QA Automation | Python