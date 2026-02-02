# Security Guidelines

## Protecting Client Data

This repository contains code for generating portfolio reports. To protect sensitive client information:

### What's Protected

The `.gitignore` file is configured to:
- ✅ Exclude all generated PDF reports (except examples)
- ✅ Exclude client CSV files in the `data/` directory
- ✅ Only allow sample/demo CSV files (sample_*.csv, client_portfolio.csv)

### Best Practices

1. **Never commit real client data**
   - Keep actual client CSV files in the `data/` directory - they won't be tracked
   - Only sample/demo files are committed to the repository

2. **Repository visibility**
   - Consider making this repository **private** if you'll be working with sensitive data
   - Code can be public, but keep client data separate

3. **Generated reports**
   - All PDF reports are automatically excluded from Git
   - Store reports locally or in a secure, separate location
   - Never push PDFs containing real client information

4. **Sharing code**
   - The code itself is safe to share
   - Always use sample/anonymized data for examples
   - Remove any hardcoded credentials or API keys

### Making the Repository Private

To make this repository private on GitHub:
1. Go to: https://github.com/kyrillasatur-cpu/report-builder/settings
2. Scroll to the "Danger Zone"
3. Click "Change visibility" → "Make private"

### Secure Workflow

```bash
# Safe: Add your real client CSV (won't be tracked)
cp ~/Downloads/real_client_data.csv data/my_client.csv

# Safe: Generate report (PDF won't be tracked)
python3 generate_report.py data/my_client.csv -o output/confidential_report.pdf

# Safe: Commit code changes (data and PDFs are excluded)
git add src/ README.md
git commit -m "Update report styling"
git push
```

### What Gets Committed

✅ **Safe to commit:**
- Python source code (`src/`, `*.py`)
- Configuration files (`requirements.txt`, `.gitignore`)
- Documentation (`README.md`, `SECURITY.md`)
- Sample data files (demo portfolios with fake names)
- Example PDF outputs (in `examples/` folder only)

❌ **Never committed (protected by .gitignore):**
- Real client CSV files in `data/` directory
- Generated PDF reports in `output/` or root directory
- Any files with real client names, account numbers, or holdings

## Questions?

If you're unsure whether something is safe to commit, check with `git status` first. The `.gitignore` file provides automatic protection for sensitive data.
