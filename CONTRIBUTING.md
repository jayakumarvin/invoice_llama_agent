# Contributing

Thanks for your interest in improving this project.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llava
```

## Making a change

1. Create a branch from `main`.
2. Make your change and keep it focused on one thing.
3. Run the agent against the demo invoices and check the output:

   ```bash
   python create_sample_invoices.py
   python local_agent.py
   ```

4. Open a pull request that explains what changed and why.

## Before you commit

- Run `git status` and confirm no real document, result file or secret is staged.
- Use only the generated demo invoices as test data.
- Read the contributor rules in [SECURITY.md](SECURITY.md).

## Reporting bugs

Open an issue with the steps to reproduce, what you expected and what happened. Redact any real financial data. For security problems, follow [SECURITY.md](SECURITY.md) instead of opening an issue.
