# Generate Notebook LM Report

This skill automates the creation of reports using Notebook LM integration.

## Description

Automatically generates reports by:
1. Collecting source documents from specified directories
2. Creating or updating a Notebook LM notebook via API
3. Generating insights and reports based on the sources
4. Exporting results to various formats (Markdown, JSON, etc.)

## Usage

```bash
/generate-notebooklm-report [options]
```

### Options

- `--source-dir <path>` - Directory containing source documents (default: ./sources)
- `--output-dir <path>` - Directory for generated reports (default: ./reports)
- `--format <type>` - Output format: markdown, json, html (default: markdown)
- `--notebook-name <name>` - Name for the Notebook LM notebook

## Environment Variables Required

- `NOTEBOOKLM_PROJECT_ID` - Google Cloud Project ID (for Enterprise API)
- `NOTEBOOKLM_LOCATION` - Location (e.g., us-central1)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key JSON
- `NOTEBOOKLM_API_KEY` - API key for third-party services (if using Apify)

## Instructions for Claude

When this skill is invoked:

1. **Parse the options** provided by the user
2. **Validate environment variables** are set
3. **Collect source files** from the specified directory
4. **Use the Bash tool** to execute the report generation script
5. **Monitor progress** and report status to the user
6. **Display summary** of generated reports with links to output files

The skill will execute the Python script located at `.claude/skills/scripts/notebooklm_reporter.py`

## Example

```bash
/generate-notebooklm-report --source-dir ./docs --format markdown --notebook-name "Project Documentation Report"
```

This will:
- Scan all documents in ./docs
- Create/update a Notebook LM notebook
- Generate a markdown report in ./reports
- Include citations and source references
