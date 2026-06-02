# OmniLocal AI

A privacy-first, local AI desktop assistant built with **Tauri**, **React**, and **LangChain**.

## Features
- **Local Brain:** Powered by Ollama (`gemma4:e4b`).
- **Web-Synapse:** Agentic search via DuckDuckGo.
- **Forge-Shell:** Local Python interpreter for math and data analysis.
- **Premium UI:** Dark mode, glassmorphism, and structured Markdown output.

## Prerequisites
1. **Ollama:** Must be running with `gemma4:e4b` pulled.
2. **Python 3.10+**: For the LangChain sidecar.
3. **Node.js & npm**: For the Tauri frontend.
4. **Rust**: (Required for building the final `.app` or `.exe`).

## How to Run

### 1. Start the Python Sidecar
```bash
cd src-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # Or install the packages manually
python main.py
```

### 2. Start the Frontend (Tauri Dev)
```bash
cd ..
npm install
npm run tauri dev
```

## Structure
- `/src`: React frontend (Vite + Tailwind).
- `/src-python`: LangChain orchestration logic.
- `/src-tauri`: Rust-based desktop shell.
