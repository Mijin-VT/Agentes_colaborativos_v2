# 🤖 Collaborative Agents System v2.1

## Complete Documentation (English)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#33-supported-operating-systems)
[![Tests](https://img.shields.io/badge/Tests-24%20unitaries-brightgreen)](test_agentes.py)

---

## 1. What is this?

A system that allows **3 AI models** installed on your computer to work together as a team. Each AI has a specialized role and can **read files, write code, execute commands, and collaborate with each other** to solve complex tasks.

**Everything runs 100% locally on your machine.** Nothing is sent to the internet. No account or subscription needed.

### Key features

- 🤝 **Real collaboration**: All 3 agents work together, not in isolation
- 📂 **File management**: Read, create, modify and list workspace files
- ⚡ **Command execution**: Run system commands with your confirmation
- 🛡️ **Integrated security**: Banned commands, blocked paths, automatic backups
- 🎛️ **External configuration**: Change models, URLs and limits without touching code
- 🔄 **Error recovery**: If an agent fails, another automatically takes its place
- 📊 **Context management**: Token counting and automatic truncation
- 🎨 **Visual interface**: Decorative panels, progress bars, per-agent colors

### What's new in v2.1

- **External config** (`config.json`): Change models, URLs, workspace and limits without touching code
- **Error recovery**: If an agent fails, another automatically takes its place
- **Context management**: Token counting and automatic truncation to prevent overflows
- **Linux/macOS support**: `instalar.sh` and `ejecutar_agentes.sh` scripts
- **Unit tests**: 24 tests covering security, command analysis and context management
- **Improved UI**: Decorative panels, progress bars, loading indicators, per-agent colors
- **Windows compatibility**: UTF-8 forced + colorama for proper color and character rendering
- **.gitignore**: Excludes logs, backups and automatically generated files

---

## 2. Detailed description of each file

### 2.1 `INSTALAR.bat`

**Type:** Windows executable file (Batch)
**Function:** Entry point for the installer. Sets UTF-8 (`chcp 65001`) and launches `instalar.ps1`.

**What it does exactly:**
- Configures console to UTF-8 for proper character display
- Checks for administrator privileges
- Runs `instalar.ps1` with `Bypass` execution policy

---

### 2.2 `instalar.ps1`

**Type:** PowerShell Script
**Function:** The actual Windows installer. Configures UTF-8 and installs everything step by step.

**What it does exactly (in order):**

1. **Configures UTF-8:** `[Console]::OutputEncoding = UTF8` for proper character display.
2. **Checks/installs Python:** Looks for `python`. If missing, installs via `winget`.
3. **Checks/installs Windows Terminal:** Looks for `Microsoft.WindowsTerminal`. If missing, installs it.
4. **Checks/installs LM Studio:** Searches for executable. If missing, installs via `winget` or provides link.
5. **Installs Python dependencies:** Runs `pip install openai colorama`. **colorama** is essential for colors on Windows.
6. **Downloads the 3 models:** If `lms` is available, automatic download. Otherwise, shows names.
7. **Configures the server:** Attempts to load models and start server via CLI.
8. **Copies files and creates shortcut:** Copies `agentes_colaborativos_v2.py` and `config.json` to project folder.

**Everything is logged to:** `C:\Users\YourName\AgentesColaborativos\instalacion.log`

---

### 2.3 `instalar.sh` (NEW in v2.1)

**Type:** Bash Script (Linux/macOS)
**Function:** Installer for Unix systems. Automatically detects the OS and uses the appropriate package manager.

**What it does exactly (in order):**

1. **Detects the OS:** Linux (apt, dnf, pacman) or macOS (Homebrew).
2. **Checks/installs Python:** Uses the OS package manager.
3. **Checks LM Studio:** Looks for existing installation or provides download instructions.
4. **Installs dependencies:** `python3 -m pip install openai colorama`.
5. **Lists required models:** Shows all 3 models with their Hugging Face repos.
6. **Copies files:** Main script and `config.json` to the project directory.
7. **Creates executable script:** Generates `ejecutar_agentes.sh`.

**Run:** `chmod +x instalar.sh && ./instalar.sh` (or `sudo` to install system software).

---

### 2.4 `EJECUTAR_AGENTES.bat`

**Type:** Windows executable file (Batch)
**Function:** Launches the agent system with pre-flight checks. Configures UTF-8.

**What it does exactly (in order):**

1. **Configures UTF-8:** `chcp 65001` for proper character display.
2. **Verifies Python:** `python --version`.
3. **Verifies dependencies:** `import openai, colorama`. If missing, installs them.
4. **Verifies LM Studio:** Connects to `http://localhost:1234`. If it fails, shows checklist.
5. **Finds and runs the script:** Launches `python agentes_colaborativos_v2.py`.

---

### 2.5 `ejecutar_agentes.sh` (NEW in v2.1)

**Type:** Bash Script (Linux/macOS)
**Function:** Launcher for Unix systems with pre-flight checks.

**What it does exactly (in order):**

1. **Verifies Python3:** Checks that `python3` is available.
2. **Verifies dependencies:** `import openai, colorama`. If missing, installs them.
3. **Verifies LM Studio:** Connects to `http://localhost:1234`.
4. **Runs the script:** `python3 agentes_colaborativos_v2.py`.

**Run:** `chmod +x ejecutar_agentes.sh && ./ejecutar_agentes.sh`

---

### 2.6 `agentes_colaborativos_v2.py`

**Type:** Python script (the heart of the system)
**Function:** Contains all the collaborative agent system logic.

**Internal file structure:**

**ENVIRONMENT COMPATIBILITY section (~lines 30-75):**
- `_init_entorno()`: Forces UTF-8 on stdout/stderr (`sys.stdout.reconfigure`)
- Attempts `colorama.init()` for Windows colors
- Fallback: activates `ENABLE_VIRTUAL_TERMINAL_PROCESSING` via ctypes on Windows 10+

**CONFIG LOADING section (~lines 78-130):**
- `_cargar_config()`: Finds and loads `config.json` from script directory or current directory
- `LM_STUDIO_URL`, `WORKSPACE`, `MAX_TOKENS`, `MAX_CONTEXT_TOKENS` (from config or defaults)
- `RUTAS_PROHIBIDAS`, `COMANDOS_PROHIBIDOS`, `MODELOS` (from config or defaults)

**COLORS AND UI section (~lines 135-175):**
- `Color` class with ANSI codes (added: `GRIS`, `SUBRAYADO`, `INVERTIDO`)
- `color()`: Applies colors to text
- `caja()`: Creates a decorative box around text
- `separador()`: Separator line with Unicode characters (`─`, `═`)
- `spinner()`: Loading indicator ("⏳ Pensando como...")
- `spinner_ok()`: Success indicator ("✅ Respondió en X.Xs")
- `barra_progreso()`: Visual progress bar (`[████████░░░░░░░░░░░░░░░░░░░░] 33%`)

**LOGGING SYSTEM section (~lines 180-195):**
- Creates a log file per session with timestamps
- `log()` records every action

**CONTEXT MANAGEMENT section (~lines 200-245):**
- `estimar_tokens()`: Estimates tokens (~1 token ≈ 3.5 characters)
- `truncar_contexto()`: Truncates history if it exceeds the limit, preserves system prompt

**SECURITY SYSTEM section (~lines 250-285):**
- `ruta_es_segura()`: Verifies path is inside workspace (uses `os.path.normpath`)
- `comando_es_seguro()`: Checks command isn't banned (Windows/Unix-specific blocks)
- `hacer_backup()`: Creates backup copy before modifying a file

**COMMAND ANALYSIS section (~lines 290-395):**
- `analizar_comando()`: Classifies command, assigns risk, generates pros/cons
- `mostrar_analisis_y_confirmar()`: Displays info and waits for decision (yes/no/edit)

**ACTION EXECUTOR section (~lines 400-515):**
- `EjecutorAcciones` class:
  - `leer_archivo()`: Reads workspace files
  - `escribir_archivo()`: Creates/modifies files (preview, confirmation, backup)
  - `ejecutar_comando()`: Runs system commands (2-min timeout, bash on Unix)
  - `listar_workspace()`: Shows workspace file tree

**SYSTEM PROMPTS section (~lines 520-590):**
- Defines each agent's "personality" with detailed instructions
- Includes available action capabilities
- Each agent receives a different prompt based on its role

**AGENT ENGINE section (~lines 595-680):**
- `extraer_acciones()`: Regex to find `[ACCION:TIPO]...[/ACCION]`
- `procesar_acciones()`: Executes each found action
- `llamar_agente()`: Sends message to model, receives response, processes actions. **v2.1**: automatic retries (up to 2), context management, context-length error detection, loading spinner, response in decorative box, per-agent colors

**WORKFLOWS section (~lines 685-870):**
- `flujo_completo()`: 3 phases with progress bars. Recovery: if agent fails, another takes its place
- `flujo_codigo()`: 3 steps with progress. Recovery: analyst → coordinator, developer → analyst
- `flujo_debate()`: 3 opinions with progress. Per-agent recovery
- `flujo_libre()`: Direct chat with agent, visual selector with icons

**MAIN MENU section (~lines 875-970):**
- Header with decorative box
- Agent panel with individual colors
- Capabilities panel
- Menu panel with numbered options
- Bottom info in gray (workspace, OS, log)
- Styled input with colored prompt

**EXECUTION section (~lines 975-1010):**
- Header with version
- LM Studio connection spinner
- List of available models
- Launches main menu

---

### 2.7 `config.json` (NEW in v2.1)

**Type:** JSON configuration file
**Function:** Centralizes all configurable system parameters without touching Python code.

| Key | What it controls | Default value |
|-----|-----------------|---------------|
| `lm_studio_url` | LM Studio server URL | `http://localhost:1234/v1` |
| `workspace` | Agent working folder | `~/agentes_workspace` |
| `max_tokens` | Maximum tokens per response | `4096` |
| `max_context_tokens` | Maximum context tokens | `3500` |
| `temperature` | Default temperature | `0.7` |
| `modelos.coordinador.nombre` | Coordinator model name | `p-e-w_qwen3-4b-instruct-2507-heretic` |
| `modelos.coordinador.temperatura` | Coordinator temperature | `0.3` |
| `modelos.analista.nombre` | Analyst model name | `p-e-w_gpt-oss-20b-heretic` |
| `modelos.analista.temperatura` | Analyst temperature | `0.7` |
| `modelos.desarrollador.nombre` | Developer model name | `huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1` |
| `modelos.desarrollador.temperatura` | Developer temperature | `0.5` |
| `rutas_prohibidas` | Blocked paths | List of system paths |
| `comandos_prohibidos` | Blocked commands | List of dangerous commands |

**How to edit:** Open `config.json` with any text editor. Changes apply on restart. If the file doesn't exist, defaults are used.

---

### 2.8 `test_agentes.py` (NEW in v2.1)

**Type:** Unit tests (Python)
**Function:** 24 tests verifying security, command analysis, context management and executor.

| Class | Tests | What it verifies |
|-------|-------|-----------------|
| `TestRutaSegura` | 3 | Safe paths inside workspace, external ones blocked |
| `TestComandoSeguro` | 3 | Dangerous commands blocked, safe ones pass |
| `TestAnalizarComando` | 7 | Risk classification correct for each command type |
| `TestEstimarTokens` | 3 | Token estimation is reasonable |
| `TestTruncarContexto` | 4 | Context truncated correctly, system prompt preserved |
| `TestConfiguracion` | 2 | Default values work without config.json |
| `TestEjecutorAcciones` | 2 | Can create files and list workspace |

**Run:** `python test_agentes.py`

---

### 2.9 `.gitignore` (NEW in v2.1)

**Type:** Git ignore file
**Function:** Excludes automatically generated files from version control.

**Excludes:**
- Logs (`agentes_workspace/.logs/`, `*.log`)
- Backups (`agentes_workspace/.backups/`, `*.bak`)
- Project files created by agents
- Python caches (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `.venv/`)
- IDE files (`.vscode/`, `.idea/`)
- OS artifacts (`.DS_Store`, `Thumbs.db`)

---

### 2.10 Automatically generated files

| File | Location | Function |
|------|----------|----------|
| `instalacion.log` | `AgentesColaborativos/` | Installer log |
| `sesion_YYYYMMDD_HHMMSS.log` | `agentes_workspace/.logs/` | Session log |
| `*.bak` | `agentes_workspace/.backups/` | Automatic backup copies |

---

## 3. System components

### 3.1 The 3 agents

| Agent | Model | LM Studio ID | Size | Role | UI Color |
|-------|-------|--------------|------|------|----------|
| Coordinator | P-E-W Qwen3 4B Instruct 2507 Heretic | `p-e-w_qwen3-4b-instruct-2507-heretic` | 8.05 GB | Organizes, integrates | Cyan |
| Analyst | P-E-W GPT Oss 20B Heretic | `p-e-w_gpt-oss-20b-heretic` | 22.19 GB | Deep reasoning, planning | Magenta |
| Developer | Huihui Qwen3 Coder 30B A3B | `huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1` | 14.71 GB | Code writing | Blue |

### 3.2 Required software

- **Python 3.10+** → Runs the main script
- **LM Studio 0.4.8+** → Hosts and serves the AI models
- **colorama** (Python) → Colors in Windows terminal
- **Windows Terminal** (recommended on Windows) → Color and emoji support

### 3.3 Supported operating systems

| OS | Installer | Launcher |
|----|-----------|----------|
| Windows 10/11 | `INSTALAR.bat` + `instalar.ps1` | `EJECUTAR_AGENTES.bat` |
| Linux (Ubuntu, Fedora, Arch) | `instalar.sh` | `ejecutar_agentes.sh` |
| macOS | `instalar.sh` | `ejecutar_agentes.sh` |

### 3.4 Recommended hardware

- **GPU**: NVIDIA RTX 4080 Super (16 GB VRAM) or better
- **RAM**: 48 GB (minimum 32 GB)
- **Disk**: ~50 GB free for models
- **OS**: Windows 10/11, Linux or macOS

---

## 4. Step-by-step installation

### 4.1 Automatic installation (Windows)

1. Download all project files into a single folder
2. **Right-click** `INSTALAR.bat` → **Run as administrator**
3. Follow the on-screen instructions

### 4.2 Automatic installation (Linux/macOS)

1. Download all project files into a single folder
2. Run: `chmod +x instalar.sh && ./instalar.sh`
3. If you need to install system software: `sudo ./instalar.sh`

### 4.3 Manual installation

#### Step 1: Python

**Windows:** https://www.python.org/downloads/ → check ✅ "Add Python to PATH"

**Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y python3 python3-pip`

**Linux (Fedora):** `sudo dnf install -y python3 python3-pip`

**macOS:** `brew install python3`

#### Step 2: LM Studio

1. Go to https://lmstudio.ai
2. Download and install for your OS
3. Open LM Studio

#### Step 3: Download models

In LM Studio, search and download:

```
bartowski/P-E-W-Qwen3-4B-Instruct-2507-Heretic-GGUF
bartowski/P-E-W-Gpt-Oss-20B-Heretic-GGUF
mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Quantization recommendations: **Q4_K_M** (balance), **Q6_K_L** (quality), **BF16** (maximum).

#### Step 4: Load models and start server

1. In LM Studio → "Your Models" → load each model
2. Go to **Developer** → **Start Server**
3. Verify all 3 say **READY** in green
4. Server should show: `Reachable at http://localhost:1234`

#### Step 5: Install dependencies

```
pip install openai colorama
```

#### Step 6: Configure models (optional)

If names in LM Studio differ, edit `config.json` → `"modelos"` section → `"nombre"` field.

---

## 5. How to run

### Windows

**Option A:** Double-click `EJECUTAR_AGENTES.bat`

**Option B:** Desktop shortcut (if you used the installer)

**Option C:** `cd C:\path\to\file && python agentes_colaborativos_v2.py`

### Linux/macOS

**Option A:** `./ejecutar_agentes.sh`

**Option B:** `cd /path/to/file && python3 agentes_colaborativos_v2.py`

---

## 6. Workflows

### 6.1 Full task (option 1)

All 3 agents collaborate **sequentially** (1 at a time, not in parallel):

```
YOU → Coordinator (plans) → Analyst and/or Developer (execute) → Coordinator (integrates) → YOU
```

**Example:** "Create a REST API in Python to manage a to-do list"

**Phases with progress:**
- **PHASE 1/3: PLANNING** `[██████████████████████████████] 33%` — Coordinator
- **PHASE 2/3: EXECUTION** `[██████████████████████████████] 66%` — Analyst + Developer
- **PHASE 3/3: INTEGRATION** `[██████████████████████████████] 100%` — Coordinator

**Error recovery:** If an agent fails, another automatically takes its place.

**Why sequential and not parallel?**
- Each agent reads the previous agent's result (accumulated context)
- You confirm each action before it executes
- LM Studio processes 1 request at a time (synchronous API)
- **Saves VRAM**: only 1 model active at a time (~16 GB max vs ~32 GB in parallel)

### 6.2 Code development (option 2)

```
Analyst (specifications) → Developer (implementation) → Coordinator (review)
```

**Example:** "A snake game in Python with pygame"

**Recovery:** Analyst → Coordinator. Developer → Analyst.

### 6.3 Debate/evaluation (option 3)

```
Analyst (analysis) → Developer (technical perspective) → Coordinator (synthesis)
```

**Example:** "Is it better to use React or Vue for a dashboard project?"

**Recovery:** Each agent has individual coordinator fallback.

### 6.4 Free chat (option 4)

Talk directly with an agent. Type "cambiar" to switch agents. Visual selector with icons and colors.

---

## 7. Action system (files and commands)

### 7.1 Available actions

| Action | What it does |
|--------|-------------|
| READ | Reads a file from the workspace |
| WRITE | Creates or modifies a file |
| EXECUTE | Runs a system command |
| LIST | Shows workspace contents |

### 7.2 Confirmation system

Each action displays: type, risk level, advantages, disadvantages, reversibility.

Options: **[s]í** (yes) executes, **[n]o** cancels, **[e]ditar** (edit) modifies the command.

### 7.3 Risk levels

| Level | Color | Examples |
|-------|-------|----------|
| LOW | 🟢 Green | Read files, list directories, git status |
| MEDIUM | 🟡 Yellow | Create files, install packages, copy/move |
| HIGH | 🔴 Red | Delete files, run scripts, unknown commands |

---

## 8. Security system

### 8.1 Safe folder (workspace)

Everything is created in: `C:\Users\YourName\agentes_workspace\` (Windows) or `~/agentes_workspace/` (Linux/macOS).
Agents **cannot** access anything outside this folder.

**What does this mean in practice?**

| Situation | Result |
|-----------|--------|
| Read `file.txt` inside the workspace | ✅ Agent reads the file normally |
| Read `C:\Users\Name\Documents\project.py` | ❌ **Error:** external path blocked |
| Use `cd ..` to leave the workspace | ❌ **Blocked** by security |
| Access `C:\Windows`, `/usr/bin`, etc. | ❌ **Blocked** (prohibited paths) |

**Need the agent to use an external file?**
Copy it to the workspace first:

```
# Windows
copy "C:\path\my_file.py" "%USERPROFILE%\agentes_workspace\"

# Linux/macOS
cp /path/my_file.py ~/agentes_workspace/
```

### 8.2 Banned commands (always blocked)

```
format, del /s, rm -rf /, rmdir /s, shutdown, reboot,
reg delete, taskkill /f /im explorer, net user, net localgroup,
powershell -enc, dd if=, mkfs
```

**Additionally on Windows:** `reg add`, `sc config`, `schtasks`

**Additionally on Linux/macOS:** `sudo`, `su -`, `visudo`, `passwd`

### 8.3 Automatic backups

Before modifying any file: `agentes_workspace/.backups/`

### 8.4 Session logs

Every action recorded in: `agentes_workspace/.logs/`

### 8.5 AI-generated content cleaning

The system includes a `limpiar_respuesta()` function that:
- **Extracts code from markdown blocks**: If the agent generates code inside ```` ```python ```` or similar, it extracts ONLY the code
- **Removes unwanted texts**: Removes markers like `[CONTENIDO DEL ARCHIVO]`, `[ARCHIVO]`, etc.
- **Formats correctly**: Removes multiple blank lines and formats the result

---

## 9. Context management (NEW in v2.1)

### 9.1 Token estimation

The system automatically estimates tokens: ~1 token ≈ 3.5 characters. Shown on each agent call.

### 9.2 Automatic truncation

If the context exceeds `max_context_tokens` (default 3500):
- The **system prompt** is always preserved
- The **oldest** messages are removed first
- The **most recent** messages are kept
- Each truncation is logged

### 9.3 Context error recovery

If the API returns "context_length_exceeded":
1. Halves the limit automatically
2. Truncates with the new limit
3. Retries the call

### 9.4 How to adjust limits

Edit `config.json`:
```json
{
    "max_tokens": 4096,
    "max_context_tokens": 3500
}
```

- **Increase** if your model supports longer contexts
- **Decrease** if you have limited VRAM/RAM

---

## 10. Performance and optimization

### With RTX 4080 Super (16 GB VRAM) + 48 GB RAM

| Configuration | Performance | VRAM used |
|---------------|-------------|-----------|
| 3 models loaded | Functional but slow (3-10 tokens/s) | ~16 GB max |
| 2 models (4B + one large) | Faster | ~12-14 GB |
| Reduced context (2048 vs 4096) | Improves memory usage | ~2-3 GB less |

### VRAM per agent (sequential execution)

| Agent | Model | Approximate VRAM |
|-------|-------|-----------------|
| Coordinator (4B) | Qwen3 4B Instruct | ~4 GB |
| Analyst (20B) | GPT-OSS 20B | ~12 GB |
| Developer (30B) | Qwen3 Coder 30B A3B | ~16 GB |

**Important note:** Since agents run **sequentially** (1 at a time), only the active model consumes VRAM. There's no overhead from multiple models in memory.

### Recommended optimizations

1. **Selective loading:** If you don't need all 3 agents, load only 2 in LM Studio
2. **Adjust `max_context_tokens`:** Reducing to 2048 improves performance on limited hardware
3. **Individual temperatures:** Each agent has its own temperature in `config.json`
   - Coordinator: 0.3 (precise and concise)
   - Analyst: 0.7 (creative in analysis)
   - Developer: 0.5 (balanced)
4. **Close other applications:** Free up VRAM and RAM for the models
5. **Recommended quantization:** Q4_K_M (balance), Q6_K_L (quality), BF16 (maximum)

---

## 11. File structure

```
📁 Collaborative Agents Project/
│
├── 📄 agentes_colaborativos_v2.py    → Main script (the brain of the system)
├── 📄 config.json                    → External config (models, URLs, limits)
├── 📄 INSTALAR.bat                   → Windows installer (run as admin)
├── 📄 instalar.ps1                   → Windows installer logic (PowerShell)
├── 📄 instalar.sh                    → Linux/macOS installer (Bash)
├── 📄 EJECUTAR_AGENTES.bat           → Windows launcher (double-click to use)
├── 📄 ejecutar_agentes.sh            → Linux/macOS launcher (Bash)
├── 📄 test_agentes.py                → Unit tests (24 tests)
├── 📄 test_limpieza.py               → Content cleaning specific tests
├── 📄 test_progress_bar.py           → Animated progress bar tests
├── 📄 .gitignore                     → Git ignore
├── 📄 DOCUMENTACION.md               → Full documentation in Spanish
├── 📄 DOCUMENTATION_EN.md            → Full documentation in English (this file)
└── 📄 README.md                      → Bilingual quick start guide
│
📁 agentes_workspace/                  (created automatically when using the system)
├── 📁 .backups/                       → Automatic backups before modifying files
├── 📁 .logs/                          → Detailed session logs
│   └── sesion_YYYYMMDD_HHMMSS.log     → Individual log with timestamp
└── 📁 (agent-created projects)        → Files generated during work
```

### Automatically generated files

| File/Folder | Location | Function |
|-------------|----------|----------|
| `instalacion.log` | `AgentesColaborativos/` (Windows) | Complete installation process log |
| `sesion_*.log` | `agentes_workspace/.logs/` | Detailed log of each work session |
| `*.bak` | `agentes_workspace/.backups/` | Automatic backup copies before overwriting |
| `__pycache__/` | Project directory | Python compilation cache (excluded by .gitignore) |

---

## 12. Troubleshooting

### "Cannot connect to LM Studio"
1. Open LM Studio → Developer → verify "Status: Running"
2. At least 1 model must say READY
3. Server at `http://localhost:1234`

### "Model not found"
1. In Developer, copy the exact model name
2. Edit `config.json` → `"modelos"` → `"nombre"` of the corresponding agent

### "Agent doesn't execute actions"
- Be explicit: "Create a file named main.py with the code"
- The 30B model is most accurate at following formats

### "It's very slow"
1. Load only 2 models
2. Reduce `max_context_tokens` to 2048 in `config.json`
3. Close other applications

### "pip install openai colorama fails"
```
python -m pip install --upgrade pip
python -m pip install openai colorama
```

### "Python is not recognized as a command"
Reinstall Python checking ✅ "Add Python to PATH"

### "Strange characters appear (←[93m, ΓòÉ)"
- The system already configures UTF-8 automatically (`chcp 65001` on Windows)
- **colorama** is installed to translate ANSI codes to Windows colors
- If it persists, use **Windows Terminal** instead of classic CMD

### "Tests fail"
```
python test_agentes.py
```
Verify that `config.json` has the correct format and the workspace is accessible.

---

## 13. Advanced customization

### From config.json (recommended)
- **Change models:** Edit `"modelos"` → `"nombre"` of each agent
- **Change temperatures:** Edit `"temperatura"` (0.0 = precise, 1.0 = creative)
- **Change workspace:** Edit `"workspace"`
- **Different server:** Change `"lm_studio_url"` (e.g., `http://192.168.100.57:1234/v1`)
- **Adjust tokens:** Change `"max_tokens"` and `"max_context_tokens"`
- **Banned commands:** Edit `"comandos_prohibidos"`
- **Banned paths:** Edit `"rutas_prohibidas"`

### From the Python code (advanced)
- **Change roles:** Edit `SYSTEM_PROMPTS` in the script
- **Add agents:** Add to `MODELOS` in `config.json` and create their prompt in `SYSTEM_PROMPTS`
- **Change retries:** Modify `max_reintentos` in `llamar_agente()` (default 2)

---

## 14. Glossary

| Term | Meaning |
|------|---------|
| GGUF | Quantized model format, optimized for CPU/GPU |
| VRAM | Graphics card memory (16 GB on the 4080 Super) |
| RAM | System memory (48 GB) |
| Token | Minimum text unit (~0.75 words in English, ~3.5 characters in Spanish) |
| MoE | Mixture of Experts: activates only parts of the model, more efficient |
| Quantization | Precision reduction for lower memory usage |
| API | Interface that allows scripts to communicate with LM Studio |
| Workspace | Safe folder where agents can create and modify files |
| Offloading | When part of the model loads in RAM instead of VRAM |
| Batch (.bat) | Windows executable file containing commands |
| PowerShell | Advanced Windows terminal with scripting capabilities |
| Bash | Linux/macOS terminal with scripting capabilities |
| Context | Message history sent to the model |
| Truncation | Removal of old messages to keep context within the limit |
| Retry | Automatic attempt after an error (up to 2 by default) |
| colorama | Python library that translates ANSI codes to native Windows colors |
| UTF-8 | Character encoding that supports emojis and Unicode symbols |
| Sequential execution | Agents run 1 at a time, not in parallel (saves VRAM) |
| Q4_K_M quantization | Balance between quality and size (recommended) |
| Q6_K_L quantization | Higher quality, higher memory consumption |
| BF16 quantization | Maximum quality (Brain Float 16-bit) |
| Animated progress bar | Visual indicator showing estimated progress during generation |
| Content cleaning | Function that extracts code from markdown blocks and removes unwanted markers |
| Confirmation system | Mechanism that requires user approval before each action |

---

*Collaborative Agents System v2.1 — April 2026*
