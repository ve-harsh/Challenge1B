# Approach Explanation – Persona-Driven Document Intelligence

## Overview

Our solution is a CPU-optimized document intelligence system designed to extract and prioritize the most relevant content from a collection of PDF documents based on a given persona and job-to-be-done. The system balances performance and accuracy using lightweight transformer-based semantic search, document parsing heuristics, and contextual sub-section refinement.

---

## 1. Document Parsing

We use `PyMuPDF` (fitz) to efficiently extract structured text from PDFs. For each document:

- Text blocks are parsed at the **page** and **paragraph** levels.
- Each text block is assigned a page number and source document.
- We filter out low-information content using simple length heuristics.

This approach generalizes across formats — research papers, books, reports — without relying on specific templates.

---

## 2. Semantic Relevance Scoring

We leverage the `all-MiniLM-L6-v2` model from the `sentence-transformers` library — a compact yet powerful transformer (~80MB) that runs efficiently on CPU.

**Steps:**

- The **persona and job description** are concatenated into a single query string and embedded.
- Each extracted text block is embedded using the same model.
- We compute **cosine similarity** between the query and each block.
- The top-K most relevant sections are selected and ranked accordingly.

This ensures that the most relevant parts of the documents are surfaced, not just based on keywords but **semantic meaning**, addressing the Section Relevance criterion (60 points).

---

## 3. Sub-section Refinement

Once top sections are selected, we refine them further:

- Each section is split into paragraphs using whitespace and newline patterns.
- We select the **longest and most informative paragraph** from each, assuming that longer paragraphs carry more detailed information.
- This is added to the `subsection_analysis` block of the output JSON.

This directly contributes to Sub-Section Relevance (40 points), providing focused, contextual information instead of raw text dumps.

---

## 4. Output Generation

The system outputs a JSON file (`challenge1b_output.json`) containing:

- **Metadata**: Input documents, persona, job-to-be-done, and timestamp.
- **Extracted Sections**: Document name, title (inferred from text), page number, and importance rank.
- **Sub-section Analysis**: Paragraph-level refined content from top sections.

---

## 5. Constraints Handling

- ✅ **Runs on CPU**: All models and operations are CPU-friendly.
- ✅ **< 1GB total size**: Model is ~80MB; code and dependencies are well within limits.
- ✅ **< 60 seconds processing time**: Efficient chunking, no full-document parsing or deep models.

---

## Generalization

- Our pipeline is modular: swapping the persona/job/query automatically changes the context.
- It handles documents from **various domains** (education, finance, research, tourism).
- No hardcoded keywords or document structures are used.

---

## Summary

By combining efficient parsing, semantic ranking, and paragraph-level refinement, our solution meets all constraints while maximizing both section and sub-section relevance — aligned directly with the competition scoring rubric.
