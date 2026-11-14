# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report them privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Include the steps to reproduce and the impact you expect. Never attach a real invoice, cheque or account number to a report; use the demo invoices or redacted data.

## Supported versions

Only the latest commit on `main` is supported.

## How this project handles data

| Area | Control |
|---|---|
| Processing | Documents are read by a local Ollama model. No document or extracted field is sent to an external service. |
| Account numbers | Masked immediately after extraction. Only the last 4 characters are kept (`****9012`); the full number is never stored, printed or written to disk. |
| Output files | `output_results/` is created with `700` permissions and the results file with `600`, so only the owner can read them. |
| Source control | `.gitignore` excludes everything in `input_documents/` except the generated demo invoices, plus `output_results/`, `.env*` files and key or certificate files. |
| Secrets | The project needs no API keys or credentials. None may be committed. |
| Dependencies | Versions are pinned in `requirements.txt`. Dependabot alerts are enabled on the repository. |
| Repository | GitHub secret scanning and push protection are enabled. |

## Rules for contributors

- Never commit real invoices, cheques, bank details or personal data. The only documents allowed in git are the generated `demo_invoice_*.pdf` files.
- Never commit secrets. If one is committed by mistake, treat it as leaked: revoke it first, then remove it.
- Never log or print a full account number. Use `mask_account_number()` in `local_agent.py`.
- Treat model output as untrusted input: validate it before using it.
- Keep dependencies pinned, and update them deliberately.

## Known security-relevant limitations

- **Approval decisions rely on model output.** The vision model can misread an amount, which can place a document under the 50,000 human-approval limit incorrectly. The status produced by this tool must not be the only control before a payment is released.
- **Documents are untrusted input.** Text inside a document could try to influence the model (prompt injection). The model's output is limited to a fixed JSON structure and has no ability to take actions, but extracted values may still be wrong.
- **Masked values are not anonymous.** The last 4 digits, vendor names and amounts remain in the results file. Store and share it accordingly.
