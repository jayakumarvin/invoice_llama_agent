import os
import json
import glob
import base64
import pymupdf
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    file_path: str
    extracted_data: Optional[dict]
    validation_status: str
    remarks: str

# JSON format-controling ollama system
llm = ChatOllama(model="llava", temperature=0, format="json")

def prepare_image_base64(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        doc = pymupdf.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        return base64.b64encode(pix.tobytes("png")).decode("utf-8")
    else:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

def mask_account_number(value) -> Optional[str]:
    """Mask an account number so only the last 4 characters stay visible."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("null", "none"):
        return None
    visible = text[-4:] if len(text) > 4 else ""
    return "****" + visible

def extract_node(state: AgentState):
    file_path = state["file_path"]
    print(f"📄 Reading: {os.path.basename(file_path)}...")
    try:
        img_base64 = prepare_image_base64(file_path)
        prompt = """
        Analyze this document image (Invoice or Cheque) and return ONLY a valid JSON object with these exact keys:
        {
            "document_type": "Invoice" or "Cheque",
            "document_number": "string or null",
            "date": "YYYY-MM-DD or null",
            "vendor_or_payee_name": "string or null",
            "total_amount": number (float, without currency symbols or commas),
            "gst_or_tax_amount": number (float, 0.0 if not found),
            "account_number": "string or null",
            "is_signature_present": true or false
        }
        """
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
            ]
        )
        response = llm.invoke([message])
        parsed_data = json.loads(response.content)
        if not isinstance(parsed_data, dict):
            raise ValueError("Model did not return a JSON object")
        # Never keep the full bank account number in memory, logs or output files
        parsed_data["account_number"] = mask_account_number(parsed_data.get("account_number"))
        return {"extracted_data": parsed_data}
    except Exception as e:
        return {"extracted_data": None, "validation_status": "FAILED", "remarks": f"Error: {str(e)}"}

def validate_node(state: AgentState):
    if state.get("validation_status") == "FAILED":
        return {}
        
    data = state.get("extracted_data")
    if not data:
        return {"validation_status": "REJECTED", "remarks": "Failed to extract data."}
    
    doc_type = data.get("document_type")
    amount = data.get("total_amount")
    
    if not amount or float(amount) <= 0:
        return {"validation_status": "NEEDS_REVIEW", "remarks": "Amount not detected properly."}
    
    if doc_type == "Cheque" and not data.get("is_signature_present"):
        return {"validation_status": "REJECTED", "remarks": "Signature missing on Cheque!"}
    
    if float(amount) > 50000:
        return {"validation_status": "HUMAN_APPROVAL_REQUIRED", "remarks": f"Amount {amount} exceeds 50,000 limit."}
    
    return {"validation_status": "APPROVED_FOR_PAYMENT", "remarks": "All details verified."}

workflow = StateGraph(AgentState)
workflow.add_node("extractor", extract_node)
workflow.add_node("validator", validate_node)
workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "validator")
workflow.add_edge("validator", END)
agent_app = workflow.compile()

if __name__ == "__main__":
    input_folder = "input_documents"
    output_folder = "output_results"
    files = []
    for ext in ("*.pdf", "*.png", "*.jpg", "*.jpeg"):
        files.extend(glob.glob(os.path.join(input_folder, ext)))
        
    if not files:
        print(f"⚠️ Put your Invoice/Cheque files inside '{input_folder}' folder and run again.")
    else:
        all_results = []
        for file_path in files:
            initial_state = {"file_path": file_path, "extracted_data": None, "validation_status": "", "remarks": ""}
            final_state = agent_app.invoke(initial_state)
            all_results.append({
                "file_name": os.path.basename(file_path),
                "status": final_state["validation_status"],
                "remarks": final_state["remarks"],
                "data": final_state["extracted_data"]
            })
            print(f"✅ Done: {os.path.basename(file_path)} -> {final_state['validation_status']} ({final_state['remarks']})\n")
            
        output_file_path = os.path.join(output_folder, "local_processed_payments.json")
        os.makedirs(output_folder, mode=0o700, exist_ok=True)
        os.chmod(output_folder, 0o700)
        # Owner-only permissions: results contain financial details
        fd = os.open(output_file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.chmod(output_file_path, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        print(f"🎉 Saved all results to '{output_file_path}'!")
