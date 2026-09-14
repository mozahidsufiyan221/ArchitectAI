# AI-Augmented AEC Consulting System — Windows Edition

A complete Microsoft Agent Framework Python starter based on the supplied
Saudi AEC architecture.

## Included

- Microsoft Agent Framework
- `MagenticBuilder` for manager-driven multidisciplinary orchestration
- `ConcurrentBuilder` for parallel discipline fan-out
- LM Studio OpenAI-compatible endpoint:
  `http://127.0.0.1:1234/v1`
- Qwen model:
  `qwen/qwen3.5-9b`
- Persistent project state in JSON
- Human approval gates
- Local SBC RAG using FAISS + sentence-transformers
- Real `MCPStreamableHTTPTool` connection to a local Revit MCP server
- Local/private Revit execution only after human approval
- Windows PowerShell setup and run instructions

Microsoft Agent Framework currently documents `MagenticBuilder` for Magentic
One-style manager orchestration and `ConcurrentBuilder` for fan-out/fan-in
parallel workflows. It also provides `MCPStreamableHTTPTool` for HTTP MCP
servers.

## Architecture

                         CLIENT BRIEF
                              |
                              v
                    MAGENTIC BUILDER
                    LLM-POWERED MANAGER
                              |
               +--------------+--------------+
               |              |              |
               v              v              v
           SURVEYOR       ARCHITECT      STRUCTURAL
               |              |              |
               +--------------+--------------+
                              |
                    CONCURRENT BUILDER
                              |
                +------+------+------+------+
                |      |      |      |      |
              HVAC  ELECTRICAL INTERIOR  ...
                |      |      |      |
                +------+------+------+------+
                              |
                              v
                       REVIEWER / QA
                         + SBC RAG
                              |
                              v
                    HUMAN ENGINEERING GATE
                              |
                         APPROVED?
                         /       \
                       NO         YES
                       |           |
                    STOP          v
                          REVIT EXECUTION AGENT
                                  |
                                  v
                       MCPStreamableHTTPTool
                                  |
                                  v
                         LOCAL REVIT MCP
                                  |
                                  v
                                REVIT

The model itself does not directly "know" the SBC. The Reviewer retrieves
evidence from the local `data\sbc` corpus.

## IMPORTANT

This is an engineering-AI orchestration starter. AI output is advisory.
It does not replace the SCE-registered professional, professional-of-record,
regulatory approval, or stamped engineering work.

Do not expose the Revit MCP endpoint to the public Internet.

Do not treat an empty SBC index as a compliance pass.

---

# 1. Windows prerequisites

Recommended:

- Windows 10/11
- Python 3.11 or 3.12
- Git (optional)
- LM Studio
- Revit + your local Revit MCP add-in/server

Check Python in PowerShell:

```powershell
py --version
python --version
```

If `py` is available, use it in the commands below.

---

# 2. Extract the project

Example:

```powershell
cd $HOME\Downloads
Expand-Archive .\aec_agent_system_windows_lmstudio.zip -DestinationPath .
cd .\aec_agent_system_windows_lmstudio
```

You should now have:

```text
aec_agent_system_windows_lmstudio\
```

---

# 3. Create the Python environment

PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

Install the project:

```powershell
pip install -r requirements.txt
```

---

# 4. LM Studio

Open LM Studio.

Load:

```text
qwen/qwen3.5-9b
```

Start the LM Studio local server at:

```text
http://127.0.0.1:1234
```

LM Studio provides an OpenAI-compatible API. This project uses:

```text
http://127.0.0.1:1234/v1
```

Copy the environment file:

```powershell
Copy-Item .env.example .env
```

The default values are:

```text
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=qwen/qwen3.5-9b
```

Verify the endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

IMPORTANT: LM Studio may expose the loaded model under an exact identifier
different from the display name. If `/v1/models` returns a different ID,
put that exact ID into `.env`.

Test the model:

```powershell
python .\scripts\test_lmstudio.py
```

---

# 5. SBC RAG

Put the official/current SBC documents you are authorized to use in:

```text
data\sbc\
```

Supported:

- PDF
- TXT
- Markdown
- DOCX

Example:

```text
data\sbc\
    SBC_Architectural.pdf
    SBC_Structural.pdf
    SBC_Mechanical.pdf
    SBC_Electrical.pdf
```

Then build the local index:

```powershell
python .\scripts\build_sbc_index.py
```

The index will be stored locally:

```text
data\sbc_index\
    index.faiss
    metadata.json
```

The starter does not upload the SBC corpus to a hosted vector database.

Test retrieval:

```powershell
python .\scripts\query_sbc.py "office building egress requirements"
```

If there are no SBC files, the Reviewer explicitly reports:

```text
SBC EVIDENCE NOT AVAILABLE
```

It must not infer that the project is compliant.

---

# 6. Run the AEC workflow

Example:

```powershell
python .\main.py --brief .\examples\commercial_office.txt
```

The workflow performs:

1. Project creation
2. Magentic multidisciplinary planning
3. Human plan approval
4. Concurrent discipline analysis
5. Local SBC retrieval
6. Reviewer / QA analysis
7. Human engineering approval
8. Optional local Revit MCP execution

At the first gate:

```text
Type APPROVE to continue
```

At the engineering gate:

```text
Type APPROVE to continue
```

Anything else stops the workflow.

For a complete design/QA run without Revit execution:

```powershell
python .\main.py --brief .\examples\commercial_office.txt --skip-execution
```

---

# 7. Local Revit MCP

The project uses the real Microsoft Agent Framework MCP client:

```python
MCPStreamableHTTPTool
```

Default:

```text
REVIT_MCP_URL=http://127.0.0.1:8765/mcp
```

Change `.env` if your Revit MCP server uses another endpoint.

Start Revit and your Revit MCP add-in/server separately.

Then run:

```powershell
python .\main.py --brief .\examples\commercial_office.txt
```

The Revit execution agent is NOT instantiated until after the human
engineering approval gate.

The Python application does not fake Revit or fake MCP. It connects to the
actual Streamable HTTP MCP endpoint and discovers the tools exposed by your
Revit bridge.

Your Revit bridge must implement the actual model operations.

## Security

Use:

```text
127.0.0.1
```

or a protected private LAN.

Do not port-forward the Revit MCP endpoint.

Do not expose it to the Internet.

---

# 8. Project state

Each project receives an ID, for example:

```text
20260912-a1b2c3d4
```

State:

```text
data\projects\20260912-a1b2c3d4\state.json
```

Artifacts:

```text
data\projects\20260912-a1b2c3d4\
    state.json
    supervisor\
    disciplines\
    qa\
    execution\
```

The state records:

- project brief
- supervisor plan
- discipline results
- SBC evidence
- QA report
- plan approval
- engineering approval
- execution result
- audit events
- final status

---

# 9. Useful commands

Check LM Studio:

```powershell
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

Test LM Studio:

```powershell
python .\scripts\test_lmstudio.py
```

Build SBC index:

```powershell
python .\scripts\build_sbc_index.py
```

Query SBC:

```powershell
python .\scripts\query_sbc.py "fire separation requirements"
```

Run full workflow:

```powershell
python .\main.py --brief .\examples\commercial_office.txt
```

Run without Revit:

```powershell
python .\main.py --brief .\examples\commercial_office.txt --skip-execution
```

Use a custom brief:

```powershell
python .\main.py --brief-text "Preliminary five-storey commercial office building in Saudi Arabia with BIM coordination."
```

---

# 10. Agent Framework design

The project intentionally uses Microsoft Agent Framework rather than AutoGen.

MagenticBuilder:

```python
workflow = (
    MagenticBuilder()
    .participants(...)
    .with_standard_manager(...)
    .build()
)
```

ConcurrentBuilder:

```python
workflow = (
    ConcurrentBuilder()
    .participants([...])
    .build()
)
```

Local Revit MCP:

```python
MCPStreamableHTTPTool(
    name="local-revit",
    url=REVIT_MCP_URL,
)
```

The exact Agent Framework API can evolve while it is under active development.
If a package release changes a method signature, check the installed package
and current Microsoft Agent Framework documentation before changing the
architecture.

---

# 11. Production next steps

This project is intentionally a strong runnable foundation, not a finished
commercial engineering platform.

Recommended next additions:

1. Replace the generic ConcurrentBuilder result with structured per-agent
   outputs using Pydantic models.
2. Add official SBC edition/version metadata to every retrieved chunk.
3. Add Balady-specific retrieval and submission checks.
4. Add project document ingestion.
5. Add BIM/Revit read-only inspection tools.
6. Add a Revit transaction allow-list.
7. Require approval for individual destructive MCP tools.
8. Add immutable audit logging.
9. Add user authentication and role-based authorization.
10. Add PDPL data classification and retention controls.
11. Add automated regression tests against a Revit test model.
12. Add a proper SCE professional review workflow.

