import os
import json
import fitz  # PyMuPDF
import re
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# === Configuration ===
INPUT_FOLDER = "input"
OUTPUT_FILE = "output/challenge1b_output.json"
PERSONA = "Travel Planner"
JOB_TO_BE_DONE = "Plan a trip of 4 days for a group of 10 college friends."
MODEL_NAME = "all-MiniLM-L6-v2"  # ~80MB and CPU-friendly
TOP_K_SECTIONS = 5
TOP_K_PARAGRAPHS_PER_SECTION = 1

# === Load model globally ===
model = SentenceTransformer(MODEL_NAME)

# === Utility: Get all PDFs ===
def get_pdf_files(folder):
    return list(Path(folder).glob("*.pdf"))

# === Utility: Extract visible text blocks with hierarchy cues ===
def extract_sections(doc_path):
    doc = fitz.open(doc_path)
    sections = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] == 0:  # text
                text = " ".join([line["spans"][0]["text"] for line in block["lines"] if line["spans"]])
                if len(text.strip()) < 40:
                    continue  # skip short titles or noisy text
                sections.append({
                    "document": os.path.basename(doc_path),
                    "text": text.strip(),
                    "page_number": page_index + 1
                })

    return sections

# === Utility: Compute semantic ranking ===
def rank_sections_by_relevance(query, chunks):
    query_embedding = model.encode(query, convert_to_tensor=True)
    texts = [chunk["text"] for chunk in chunks]
    chunk_embeddings = model.encode(texts, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]

    ranked = sorted(zip(chunks, cosine_scores), key=lambda x: x[1], reverse=True)
    return ranked

# === Utility: Paragraph-level filtering ===
def extract_top_paragraphs(text, k=1):
    paragraphs = re.split(r'\n{2,}|\r\n\r\n', text)
    paragraphs = sorted(paragraphs, key=lambda p: len(p), reverse=True)
    return paragraphs[:k] if paragraphs else [text[:300]]

# === Main driver ===
def generate_output(persona, job, docs):
    query = f"{persona}: {job}"
    all_sections = []

    for pdf in docs:
        all_sections += extract_sections(pdf)

    ranked = rank_sections_by_relevance(query, all_sections)

    extracted_sections = []
    sub_section_analysis = []

    for rank, (sec, score) in enumerate(ranked[:TOP_K_SECTIONS]):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["text"][:70].replace("\n", " ") + "...",
            "importance_rank": rank + 1,
            "page_number": sec["page_number"]
        })

        top_paragraphs = extract_top_paragraphs(sec["text"], TOP_K_PARAGRAPHS_PER_SECTION)
        for para in top_paragraphs:
            sub_section_analysis.append({
                "document": sec["document"],
                "refined_text": para.strip(),
                "page_number": sec["page_number"]
            })

    return {
        "metadata": {
            "input_documents": [os.path.basename(doc) for doc in docs],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": sub_section_analysis
    }

def main():
    Path("output").mkdir(exist_ok=True)
    pdfs = get_pdf_files(INPUT_FOLDER)
    if not pdfs:
        print("No PDF files found in the input folder.")
        return

    output_json = generate_output(PERSONA, JOB_TO_BE_DONE, pdfs)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    print(f"[✓] Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
