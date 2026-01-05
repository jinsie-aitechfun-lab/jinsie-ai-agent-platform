# Prompt Templates

This directory contains reusable prompt templates used by the application and demo scripts.

## Files

- `system_prompt.md`
  - Global assistant behavior and response style baseline.

- `summary_prompt.md`
  - Generic summarization template with placeholders such as `{{input_text}}`.

- `rag_prompt.md`
  - Retrieval-Augmented Generation template with placeholders such as `{{query}}` and `{{context}}`.

## Usage

Prompts are loaded via:

- `app/core/prompts.py` -> `load_prompt(name: str)`

Example:

- `load_prompt("system_prompt")` loads `app/prompts/system_prompt.md`.
