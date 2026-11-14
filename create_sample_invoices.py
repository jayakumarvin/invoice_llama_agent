import os
import pymupdf

def generate_invoice_pdf(filename, inv_no, date, vendor, items, subtotal, gst, total):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 60), "TAX INVOICE", fontsize=22, fontname="helv")
    page.insert_text((50, 95), f"Vendor Name : {vendor}", fontsize=12)
    page.insert_text((50, 115), f"Invoice No  : {inv_no}", fontsize=12)
    page.insert_text((50, 135), f"Date        : {date}", fontsize=12)
    page.draw_line((50, 155), (545, 155))
    y = 180
    page.insert_text((50, y), "Description", fontsize=12)
    page.insert_text((420, y), "Amount (INR)", fontsize=12)
    page.draw_line((50, y + 10), (545, y + 10))
    y += 35
    for desc, amt in items:
        page.insert_text((50, y), desc, fontsize=11)
        page.insert_text((420, y), f"{amt:,.2f}", fontsize=11)
        y += 25
    page.draw_line((50, y + 10), (545, y + 10))
    y += 35
    page.insert_text((300, y), f"Subtotal    : Rs. {subtotal:,.2f}", fontsize=12)
    page.insert_text((300, y + 25), f"GST (18%)   : Rs. {gst:,.2f}", fontsize=12)
    page.insert_text((300, y + 55), f"Total Amount: Rs. {total:,.2f}", fontsize=14)
    os.makedirs("input_documents", exist_ok=True)
    filepath = os.path.join("input_documents", filename)
    doc.save(filepath)
    doc.close()
    print(f"Created: {filepath}")

if __name__ == "__main__":
    generate_invoice_pdf("demo_invoice_1.pdf", "INV-2026-101", "2026-11-14", "Sri Murugan Office Supplies", [("A4 Paper Bundle", 4500.00), ("Toner Cartridge", 5500.00)], 10000.00, 1800.00, 11800.00)
    generate_invoice_pdf("demo_invoice_2.pdf", "INV-2026-102", "2026-11-14", "Kaveri Tech Solutions", [("Workstation Laptop", 65000.00), ("4K Monitor", 15000.00)], 80000.00, 14400.00, 94400.00)
