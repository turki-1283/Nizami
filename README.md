# Nizami | نظامي ⚖️

**Nizami** is an AI-powered Retrieval-Augmented Generation (RAG) assistant designed to answer questions about the **Saudi Labor Law** using retrieved legal provisions as its primary source of evidence.

The project combines lexical search, semantic retrieval, rank fusion, reranking, and large language models to retrieve relevant legal articles and generate concise, source-grounded answers.

> **Note:** Nizami is an educational and experimental AI project. It is not a substitute for professional legal advice.

---

## Overview

Legal documents can be difficult to search using traditional keyword matching alone, especially when users ask questions in natural Arabic that differ from the exact wording used in legislation.

Nizami addresses this by combining multiple retrieval techniques:

1. Arabic text normalization
2. Character n-gram BM25 retrieval
3. Semantic vector search
4. LLM-based query rewriting
5. Weighted Reciprocal Rank Fusion (RRF)
6. Cross-Encoder reranking
7. Retrieval protection and candidate fusion
8. Claude-based answer generation
9. Answer verification against retrieved legal context

The goal is to produce answers that remain grounded in the retrieved Saudi Labor Law material rather than relying on unsupported model knowledge.

---

## Architecture

```text
User Question
      │
      ▼
Arabic Normalization
      │
      ├───────────────┐
      │               │
      ▼               ▼
Original Query    Query Rewrite
      │               │
      ├───────┬───────┤
      │       │       │
      ▼       ▼       ▼
    BM25   Semantic Retrieval
      │       │
      └───┬───┘
          ▼
Weighted Reciprocal Rank Fusion
          │
          ▼
Candidate Pool
          │
          ▼
Cross-Encoder Reranking
          │
          ▼
Dual BM25 Protection
          │
          ▼
Retrieved Legal Context
          │
          ▼
Claude Answer Generation
          │
          ▼
Answer Verification
          │
          ▼
Final Grounded Answer
```

---

## Retrieval Pipeline

### 1. Arabic Text Normalization

Arabic text is normalized before lexical retrieval to reduce differences in spelling and character forms.

Character trigrams are then used for BM25 indexing and retrieval.

### 2. BM25 Retrieval

Nizami performs lexical retrieval using:

- Original user question
- LLM-rewritten question

This helps preserve exact legal terminology while also improving retrieval when the user's wording differs from the source material.

### 3. Semantic Retrieval

Semantic search is performed using:

```text
sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```

Legal chunks are stored in **ChromaDB** using cosine similarity.

### 4. Weighted Reciprocal Rank Fusion

Results from lexical and semantic retrieval are combined using weighted Reciprocal Rank Fusion.

Current experimental configuration:

```text
RRF weights: [0.5, 0.5, 1.0, 3.0]
RRF k: 60
```

This allows multiple retrieval signals to contribute to the final candidate ranking.

### 5. Cross-Encoder Reranking

Candidate documents are reranked using:

```text
cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

The reranker provides a stronger query-document relevance signal before the final context is constructed.

### 6. Retrieval Protection

Nizami includes a retrieval protection mechanism designed to preserve strong lexical matches that could otherwise be lost during semantic fusion or reranking.

A separate experimental **Retrieval Rescue V3** pipeline was evaluated to measure whether additional candidates could recover missed relevant articles.

---

## Answer Generation

After retrieval, the selected legal context is provided to Claude.

The answer-generation prompt is designed to:

- Answer only from retrieved legal material
- Avoid unsupported legal conclusions
- Avoid inventing penalties, conditions, amounts, or legal effects
- Mention relevant article numbers
- Explicitly state when the retrieved material is insufficient
- Keep responses concise and directly related to the question

A second verification stage reviews the generated answer against the retrieved context and removes or corrects unsupported legal claims.

---

## Evaluation

Nizami was evaluated using a manually defined benchmark of Saudi Labor Law questions.

One original benchmark question was excluded after source inspection showed that its expected reference was not supported by the available corpus. The validated benchmark therefore contains **49 questions**.

### Retrieval Results

| Pipeline | Top-1 | Article-Level Retrieval Recall |
|---|---:|---:|
| Current Retrieval | 31/49 (63.3%) | 44/49 (89.8%) |
| Retrieval Rescue V3 | 31/49 (63.3%) | **49/49 (100.0%)** |

Retrieval Rescue V3 recovered five previously missed article-level cases without losing any previously successful retrievals.

### Answer Generation Results

Manual evaluation of generated answers using the V3 retrieval context produced:

```text
Core-answer correctness: 48/49 (98.0%)
```

The single failed case revealed an important limitation in the evaluation methodology: the correct **article** had been retrieved, but the specific **paragraph** containing the required rule was missing from the generated context.

This demonstrated that article-level recall alone does not guarantee evidence-level or paragraph-level recall.

Further diagnostic experiments successfully retrieved the missing paragraph, but these experimental rescue mechanisms were not promoted to the production retrieval pipeline because they also introduced additional irrelevant context.

### Important Evaluation Note

The reported results describe performance on this specific internal benchmark.

They should **not** be interpreted as 100% legal accuracy or as evidence that the system will correctly answer every Saudi Labor Law question.

---

## Technology Stack

- **Python**
- **Streamlit**
- **ChromaDB**
- **Sentence Transformers**
- **BM25 / rank-bm25**
- **Cross-Encoder reranking**
- **Anthropic Claude**
- **python-dotenv**

---

## Project Structure

```text
nizami/
│
├── app.py
├── nizami.py
├── build_database.py
├── chunk_articles.py
├── chunks.json
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── articles_clean.json
│
└── evaluation/
    ├── fixed_rewrites.json
    ├── retrieval_rescue_v3_experiment.py
    ├── answer_generation_v3_experiment.py
    └── answer_generation_v3_results.json
```

Local databases, API credentials, Python cache files, raw preprocessing files, and archived experiments are excluded from version control.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/turki-1283/Nizami.git
cd Nizami
```

### 2. Create a virtual environment

Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Never commit the real `.env` file or API keys to version control.

A safe `.env.example` is included in the repository.

---

## Building the Data

The cleaned legal articles are stored in:

```text
data/articles_clean.json
```

Generate the chunked dataset:

```bash
python chunk_articles.py
```

Then build the local ChromaDB vector database:

```bash
python build_database.py
```

---

## Running Nizami

Start the Streamlit application:

```bash
streamlit run app.py
```

On Windows with a specific Python installation, for example:

```bash
py -3.14 -m streamlit run app.py
```

The application will open in your browser and allow you to ask Saudi Labor Law questions in Arabic.

---

## Example Questions

Nizami can process questions such as:

```text
كم أقصى مدة لفترة التجربة؟

هل يقدر صاحب العمل ينقلني لمدينة ثانية بدون موافقتي؟

كيف تُحسب مكافأة نهاية الخدمة؟

كم ساعات العمل في رمضان للمسلمين؟

هل يحق للعامل أجر إضافي على العمل الإضافي؟
```

The system retrieves relevant legal provisions before generating the response.

---

## Limitations

Nizami is currently limited by several factors:

- Evaluation is based on a relatively small internal benchmark.
- Retrieval quality depends on the quality and completeness of the legal corpus.
- Article-level retrieval does not always guarantee retrieval of the exact relevant paragraph.
- LLM-generated answers may still require human verification.
- The system does not replace a lawyer or an official legal authority.
- Legal sources may change over time and require dataset updates.

---

## Future Work

Potential future improvements include:

- Paragraph-level retrieval evaluation
- Better context diversity and sibling-chunk selection
- Larger and more diverse evaluation datasets
- Automated source/version tracking
- Improved legal citation presentation
- Evaluation of answer faithfulness and evidence coverage
- Support for additional Saudi regulations and legal domains

---

## Author

**Turki Al-Shahrani**  
B.Sc. Computer Science

Developed as a practical AI/RAG project focused on Arabic legal information retrieval, semantic search, reranking, and grounded answer generation.

---

## Disclaimer

Nizami is an educational and experimental software project.

The information generated by the system should not be considered legal advice. Users should refer to official Saudi legal sources and qualified legal professionals when making legal decisions.
