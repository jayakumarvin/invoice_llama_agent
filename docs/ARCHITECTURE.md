# Architecture

The agent is a two-node [LangGraph](https://github.com/langchain-ai/langgraph) workflow defined in `local_agent.py`. Each input file is run through the graph once.

```mermaid
flowchart TD
    S([file path]) --> X[extractor node]
    X --> V[validator node]
    V --> E([final state])
```

## State

Both nodes read and update one shared state object, `AgentState`:

| Key | Type | Set by |
|---|---|---|
| `file_path` | `str` | The caller |
| `extracted_data` | `dict` or `None` | `extractor` |
| `validation_status` | `str` | `extractor` (on error) or `validator` |
| `remarks` | `str` | `extractor` (on error) or `validator` |

## Extractor node (`extract_node`)

1. `prepare_image_base64()` turns the file into a base64 image. A PDF's first page is rendered at 200 DPI with PyMuPDF; image files are read as they are.
2. The image and a fixed prompt are sent to the local `llava` model through `ChatOllama`. The model runs with `temperature=0` and `format="json"` so it returns a JSON object.
3. The response is parsed. Anything that is not a JSON object is rejected.
4. `mask_account_number()` replaces the account number with `****` plus its last 4 characters before the data is stored in the state.

Any exception sets the status to `FAILED` with the error in `remarks`.

## Validator node (`validate_node`)

Applies the approval rules in order and sets `validation_status` and `remarks`. The rules are listed in the [README](../README.md#approval-rules). The human-approval limit of 50,000 is set in this function.

## Main loop

When run as a script, `local_agent.py`:

1. Collects `.pdf`, `.png`, `.jpg` and `.jpeg` files from `input_documents/`.
2. Invokes the graph for each file.
3. Writes all results to `output_results/local_processed_payments.json`, creating the folder with `700` and the file with `600` permissions.

## Demo data

`create_sample_invoices.py` uses PyMuPDF to draw two fictional tax invoices into `input_documents/`. They contain no real vendor or bank data and are the only documents tracked in git.

## Changing the behaviour

| To change | Edit |
|---|---|
| The model | `ChatOllama(model="llava", ...)` |
| The extracted fields | The prompt in `extract_node` |
| The approval rules or limit | `validate_node` |
| Input and output folders | `input_folder` and `output_folder` in the main block |
