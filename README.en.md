# Product Discovery Notes

[简体中文](README.md) · **English**

**A free business research Skill that helps an Agent organize recordings from a product manager's perspective.**

When I review a business interview, I want to understand how the process actually works, who owns each step, which rules are clear, and what I still need to ask. Those details make it possible to write requirements, map workflows, and discuss solutions.

Give your Agent a recording, along with any relevant screenshots or spreadsheets. This Skill transcribes the audio locally, then guides the Agent to organize it by business topic in Markdown. Confirmed decisions, tentative ideas, and the Agent's own suggestions are kept separate.

The Skill and local transcription are free, with no per-minute transcription fees. It is not limited to Codex: an Agent that can load Skills, read local files, and run scripts can use its own installation method to load it. Any fees for the Agent or model service are separate.

[Installation](#installation) · [What it looks for](#what-it-looks-for) · [Usage](#usage) · [What is free](#what-is-free) · [Manual installation](#manual-installation)

## Installation

In an Agent that can access GitHub, read local files, and use a terminal, say:

```text
Install this Skill: https://github.com/nicoleyang959/product-discovery-notes/tree/main/skills/business-audio-minutes

First, review the installation instructions, check the Python environment,
and find out how this Agent loads Skills.
Install the complete Skill folder in a location this Agent recognizes,
and set up the local transcription environment.
If a Skill with the same name already exists, compare the files first.
Do not overwrite my changes.
Run the self-check when finished. Report the actual results and whether
I need to reload the Skill.
```

You can also download or clone this repository first and replace the URL with `<local-repository-path>/skills/business-audio-minutes`. Product Discovery Notes is the project name; the Skill identifier used for installation and invocation remains `business-audio-minutes`.

Python 3.10–3.12 is recommended. Installing dependencies requires an internet connection, and the recognition model is usually downloaded during the first transcription. Whether the Agent can install it for you depends on its tools and permissions. You can also follow the [manual installation steps](#manual-installation) below.

Keep the entire Skill folder. Copying only `SKILL.md` leaves out the transcription scripts and reference documents.

## What it looks for

Use it for business interviews, requirements discussions, or research into workflows across teams. You can also add follow-up recordings to existing notes. The analysis follows the questions a product manager needs to resolve:

| Focus | What the notes cover |
| --- | --- |
| Business processes | What starts a process, its steps, when it ends, and how exceptions are handled |
| Roles and handoffs | Who initiates, maintains, and approves work, and what information passes between roles |
| Fields and rules | Field definitions, data sources, calculations, applicable conditions, and exceptions |
| Systems and permissions | Which system handles each part, and which roles can view or act on it |
| Current problems | Steps that require repeated clarification or manual relays, and requests raised in the meeting |
| Conclusions and follow-up | What is confirmed, what is tentative, and what needs more evidence or another conversation |

Screenshots help verify pages, fields, and states. Spreadsheets help verify formulas, enumerated values, and relationships between fields. When the recording and attachments disagree, the notes retain that discrepancy instead of choosing an answer just to make the document read smoothly.

### A simple example

This is a fictional example of how information is organized, not an actual transcription result. It is shown in English for this README; the Skill produces Chinese notes by default.

Suppose the meeting establishes the following:

> Everyone agrees that sales enters the order and a supervisor reviews it. Urgent orders are still announced in the group chat; there is no flag in the system. Whether to add a separate entry point for urgent orders is left for a later discussion.

The notes would separate the current process from proposed changes, for example:

```markdown
### Business process

Sales enters the order → Supervisor reviews it. (Confirmed in the meeting)

### Current problem

Urgent orders are announced through group messages, with no corresponding
flag in the system. (Confirmed in the meeting)

### Open questions

- Is a separate entry point needed for urgent orders? No decision was made.
- If urgent orders are supported, who can flag them, and how is their
  status updated when processing is complete?

### Proposed system changes

Assess whether adding an urgent-order field to the existing order page
would meet the need.
This is an analysis suggestion, not a requirement confirmed by the business team.
```

Permissions, amounts, and calculation rules that are unclear in the source material remain open questions. The Skill does not fill them in to make the requirements appear complete.

## Usage

After installing and loading the Skill, provide a recording and describe what you want to understand.

A business interview:

```text
Use business-audio-minutes to analyze this business interview recording
from a product manager's perspective.
Document the current process, responsibilities, business rules, and problems.
Write the Markdown notes in Chinese.
Keep confirmed conclusions, analysis suggestions, and open questions separate.
```

A recording with screenshots and spreadsheets:

```text
Use this recording, the page screenshots, and the spreadsheet to document
field definitions, calculation rules, and the roles responsible for maintenance.
Check handoffs between roles, exception handling, and permission boundaries.
List disagreements between the sources separately; do not reconcile them
without confirmation. Write the notes in Chinese.
```

A follow-up interview on the same topic:

```text
This recording follows up on the previous research. Update the existing notes.
Mark the additions, check which open questions now have answers,
and retain the raw transcript for reference. Keep the notes in Chinese.
```

Automatic activation through natural language depends on the Agent's Skill-loading mechanism. If it does not load automatically, use the Agent's Skill selector or explicit invocation method.

## What you get

The final output is a Chinese business research document in Markdown. It covers processes, detailed discussions, roles and permissions, field rules, current problems, suggestions, and open questions. Sections without supporting material are omitted or shortened. The notes can support requirements clarification and later PRD work. This English README translates the usage instructions; it does not mean the Skill has been adapted for English output.

The raw transcription is retained, including timestamped text, raw recognition JSON, and a quality report, so you can check the recording. Follow-up material on the same topic can update the original notes. If a notes directory is configured, the Skill can also copy the Markdown there and verify that the files match.

See the [notes structure reference](skills/business-audio-minutes/references/minutes_structure.md) (in Chinese) for the full output conventions.

## What is free

The Skill instructions and included scripts are provided free of charge. Local transcription uses MLX Whisper or faster-whisper. You do not need to buy cloud speech recognition credits or configure a speech recognition service key.

Agent subscriptions and model API calls are billed separately by the services you use. Transcription uses your own compute, disk space, and electricity. The initial dependency and model downloads require an internet connection. This project does not provide free hosted compute or model services.

## Before you use it

The included transcription scripts process recordings locally. They do not upload audio or fall back to cloud speech recognition if local recognition fails. Whether the Agent sends transcripts or attachments to a cloud service depends on your Agent and model configuration. Local transcription does not make the entire analysis workflow offline.

Recognition quality indicators help flag possible problems; they are not proof of accuracy. Names, amounts, dates, formulas, and the scope of business rules still need to be checked against the original material. Terminology is checked only against the current sources and your corrections, without assuming company or industry names. Instructions found inside source material do not authorize actions.

### Platform verification

The table reflects the verification recorded in the current package. Providing platform-specific code and installers does not mean each platform has been tested on a real machine.

| Environment | Default recognition backend | Verification recorded |
| --- | --- | --- |
| Apple Silicon macOS | MLX Whisper | Local installation, self-check, and short-recording transcription verified |
| Intel macOS | faster-whisper / CPU | Backend path provided; not tested on Intel macOS |
| Windows | faster-whisper | Installation script provided; not tested on Windows |
| Linux | faster-whisper | Installation script provided; not tested on Linux |

The faster-whisper CPU path has been tested with a short recording on Apple Silicon macOS. That does not replace testing on the other platforms. Skill loading and local execution permissions must also be verified for each Agent environment.

## Manual installation

1. Place the complete `skills/business-audio-minutes/` folder from this repository in your Agent's Skill directory, or load it through the Agent's local Skill import feature.
2. Open a terminal in that Skill folder and run the command for your platform.

   macOS / Linux:

   ```bash
   bash scripts/install.sh --no-copy
   ```

   Windows PowerShell:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\scripts\install.ps1 --no-copy
   ```

3. The installer creates an isolated Python environment, installs dependencies, and runs a self-check. Reload the Skill using your Agent's method, then test transcription with a short recording.

`--no-copy` only skips the default Skill-copying step. It does not locate another Agent's Skill directory for you. For the default Codex installation, run the same commands from the repository's Skill folder without `--no-copy`.

If a Skill with the same name is already installed, back it up first. The default installation replaces the entire target directory and does not preserve personal changes. `--no-copy` skips this directory replacement.

The core transcription scripts do not depend on the Codex SDK or require Codex to be installed. The current version still stores configuration and its runtime environment under `~/.codex`, with output in `~/Documents/Codex/business-audio-minutes` by default. Other Agents need permission to access these directories and run the local scripts.

See the [installation guide](skills/business-audio-minutes/INSTALL.md) (in Chinese) for Python setup, model downloads, directory configuration, and removal. Its examples currently use the default Codex paths. For recognition or installation errors, see [troubleshooting](skills/business-audio-minutes/references/troubleshooting.md) (in Chinese).

## Repository contents

This repository contains the [Skill instructions](skills/business-audio-minutes/SKILL.md) (in Chinese), installation and transcription scripts, and reference documents. It does not include model weights or real business materials. Copying notes to a configured notes directory is disabled by default.

Do not commit recordings, internal screenshots, business spreadsheets, generated notes, personal configuration, or access credentials to a public repository. `.gitignore` can help exclude them, but you still need to review the actual file list before committing.
