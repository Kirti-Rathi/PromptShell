<h1 align="center" style="font-size: 32px;">
  >_ PromptShell
  <sup>
    <span style="font-size: 14px; color: #666;">v0.1.1</span>
  </sup>
</h1>

<p align="center" style="font-size: 18px;">The Intelligent Terminal | Context-Aware Natural Language Commands</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=flat&logo=windows&logoColor=white" height="25" style="margin-right: 4px;"> 
  <img src="https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black" height="25" style="margin-right: 4px;">
  <img src="https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white" height="25">
</p>

<a href="https://pepy.tech/project/promptshell/">
  <img src="https://static.pepy.tech/badge/promptshell" height="20">
</a>

https://github.com/user-attachments/assets/c2ba7d09-83ea-4d10-a825-92c30f28c0bd

---

### CLI Options

#### `--version`

The `--version` flag allows users to check the installed version of the package directly from the terminal.

Current version: `PromptShell v0.1.1`

## ✨ Features

### 🚀 Redefine Your Terminal Experience

- ⚡**Natural Language to Shell Commands**: Converts plain English queries into accurate shell commands.

- 🖥️**Cross-Platform Compatibility**: Works seamlessly across Windows, Linux, and macOS.

- 🤖**Hybrid AI-Model Support**: Supports both local (Ollama) and cloud-based (Groq, OpenAI, Google, etc.) LLMs for flexibility.

- 🔒**Privacy-First Approach**: Defaults to local models and runs completely offline, so that no data leaves your device unless you enable cloud APIs.

- 🎯**Context-Aware Execution**: Remembers command history, tracks files, and adapts suggestions accordingly.

- ⚠️**Secure Command Execution**: Blocks dangerous commands and asks for confirmation.

- 🛠️**Intelligent Debugging & Auto-Correction**: Identifies error, autonomously debugs issues and suggests corrected command.

- 🔍**Smart Autocompletion**: Provides tab completions for files and folder present in working directory.

- 🤖 **Direct Execution & Queries**: Directly execute shell commands with '!' (e.g., !ls -la), or Ask shell-related questions using '?' (e.g., How do I create a new SSH key?).

- 🐳 **Built-in Support for Git, Docker, and Dev Tools**: Seamlessly understands and executes Git, Docker, Kubernetes, and package manager commands.

---

## 📥 Installation

### Prerequisites

- Python 3.9+
- `pip` (Windows)
- `pipx` (Linux & macOS)

### Installation Steps

#### Windows:

```bash
pip install promptshell
```

#### Linux & macOS:

```bash
pipx ensurepath  # Ensure pipx is in PATH (Linux/macOS)
pipx install promptshell
```

### Run PromptShell

```bash
promptshell
```

---

## ⚙️ Configuration

- Local models need 4GB+ RAM (llama3:8b) to 16GB+ (llama3:70b)
- API performance varies by provider (deepseek-r1-distill-llama-70b in Groq is recommended)
- Response quality depends on selected model capabilities

### Local Configuration

```bash
# Install Ollama for local LLM's
$ curl -fsSL https://ollama.com/install.sh | sh   # Linux
$ brew install ollama   # MacOS
$ winget install Ollama.Ollama    # Windows (via Powershell Administrator)

# Verify Installation
$ ollama --version

# Get base model
$ ollama pull <model_name>
```

### First-Time Setup

```bash
# Interactive configuration wizard

$ --config

? Select operation mode: (Use arrow keys)
 » local (Privacy-first, needs 4GB+ RAM)
   api (Faster but requires internet)

# If local mode is selected
? Choose local model: (Use arrow keys) # lists ollama models installed on your system
 » llama3.1:8b
   llama3:8b-instruct-q4_1
   deepseek-r1:latest
   mistral:latest

# If API mode is selected
? API provider selection: (Use arrow keys)
 » Groq
   OpenAI
   Google
   Anthropic
   Fireworks
   OpenRouter
   Deepseek

? Select model for Groq: (Use arrow keys)
 » llama-3.1-8b-instant
   deepseek-r1-distill-llama-70b
   gemma2-9b-it
   llama-3.3-70b-versatile
   llama3-70b-8192
   llama3-8b-8192
   mixtral-8x7b-32768
   Custom model...

? Enter API key for Groq: #[hidden input]

✅ Configuration updated!
Saved to /home/username/.config/PromptShell/promptshell_config.conf   # (Linux & macOS)
Saved to C:\Users\username\AppData\Roaming\PromptShell\promptshell_config.conf   #(Windows)

Active model: #[Selected-model]
Configuration updated!
```

---

## 🛠 Usage

### Basic Commands

```bash
# Start the PromptShell REPL
$ promptshell

# Execute natural language queries
$ backup all .txt files in a folder named backup

# Directly execute raw shell commands (bypassing AI processing) with '!'
$ !mkdir backup && copy *.txt backup\

# Ask questions by prefixing or suffixing your query with '?'
$ What’s the command to list all hidden files?

# Configure or change the LLM provider
$ --config

# View help and usage instructions
$ --help

# Clear the terminal screen
$ clear

# Exit PromptShell
$ quit
```

---

## 🌟 Examples

### Convert Plain English Queries into Accurate Shell Commands

![shell](https://imgur.com/kf2Flao.png)

### Ask Questions, Execute Commands Directly, and Ensure Secure Execution

![ques](https://imgur.com/NqmJ6L1.png)

### Seamless Integration with Git, Docker, and Developer Tools

![Git](https://imgur.com/2YwxXoz.png)

### Generate Code Snippets Using Prompts and Save Directly to Desired Locations

![code](https://imgur.com/hM5jBvQ.png)

---

## 🚧 Development Status

PromptShell is currently in **alpha stage** of development.

**Known Limitations:**

- Ollama models may hallucinate and produce inaccurate responses.
- Some API providers may have rate limits or require paid plans.
- User-defined command aliases and shortcuts are not yet supported.

**Roadmap**:

- [x] Local LLM support
- [x] Interactive configuration setup
- [ ] Improve command execution safety measures
- [ ] Implement speech input support
- [ ] Add support for user-defined command aliases
- [ ] Expand model compatibility (e.g., fine-tuned small-scale models)

---

## 🤝 Contributing

We welcome contributions! Here’s how to help:

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-idea`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-idea`.
5. Open a pull request.

---

## 📜 License

This project is licensed under the Apache 2.0 License. See [LICENSE](./LICENSE) for details.

---

## 📧 Contact

- Built by **Kirti Rathi**
- **Email**: [kirtirathi282@gmail.com](mailto:kirtirathi282@gmail.com)

---

> **Note**:<br/>
> Always verify commands before execution.<br/>
> Use at your own risk with critical operations.<br/>
> This project is not affiliated with any API or model providers.<br/>
> Local models require adequate system resources.<br/>
> Internet is required for API mode.<br/>
