import json
import os
import re
from pathlib import Path

import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer


# ==================================================
# Configuration
# ==================================================

CHUNKS_FILE = Path("chunks.json")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "labor_law"

EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
LLM_MODEL = "claude-sonnet-4-5"

RRF_WEIGHTS = [0.5, 0.5, 1.0, 3.0]
RRF_K = 60

BM25_ORIGINAL_KEEP = 10
BM25_REWRITE_KEEP = 10
RRF_KEEP = 30

RERANKER_TOP_K = 5
FINAL_TOP_K = 5


# ==================================================
# Environment
# ==================================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY غير موجود. "
        "أضف المفتاح إلى ملف .env."
    )

client_llm = Anthropic(api_key=api_key)


# ==================================================
# Load data
# ==================================================

if not CHUNKS_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {CHUNKS_FILE}. "
        "Run chunk_articles.py first."
    )

with CHUNKS_FILE.open("r", encoding="utf-8") as file:
    articles = json.load(file)

if not articles:
    raise ValueError("chunks.json does not contain any chunks.")


# ==================================================
# Arabic normalization and tokenization
# ==================================================

def normalize_arabic(text):
    """Normalize Arabic text for BM25 retrieval."""

    text = re.sub(r"[\u064B-\u0652]", "", text)
    text = text.replace("ـ", "")

    text = (
        text.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
    )

    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")

    return text


def tokenize(text):
    """Convert Arabic text into character trigrams."""

    text = normalize_arabic(text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", "", text)

    n = 3

    return [
        text[i:i + n]
        for i in range(len(text) - n + 1)
    ]


# ==================================================
# BM25
# ==================================================

corpus_tokens = [
    tokenize(article["text"])
    for article in articles
]

bm25 = BM25Okapi(corpus_tokens)


# ==================================================
# Models
# ==================================================

model = SentenceTransformer(
    EMBEDDING_MODEL
)

reranker = CrossEncoder(
    RERANKER_MODEL
)


# ==================================================
# Chroma
# ==================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )
except Exception as exc:
    raise RuntimeError(
        "تعذر العثور على قاعدة بيانات Chroma. "
        "شغّل build_database.py أولًا."
    ) from exc


# ==================================================
# Chunk lookups
# ==================================================

id_to_title = {
    f"chunk_{i}": articles[i]["title"]
    for i in range(len(articles))
}

id_to_text = {
    f"chunk_{i}": articles[i]["text"]
    for i in range(len(articles))
}


# ==================================================
# Query rewriting
# ==================================================

QUERY_REWRITE_PROMPT = """
أنت مكوّن Query Rewriting داخل نظام RAG لنظام العمل السعودي.

حوّل السؤال إلى صياغة نظامية رسمية مناسبة للاسترجاع من مواد نظام العمل السعودي.

قواعد إلزامية:
- أخرج جملة بحث واحدة فقط.
- لا تجب عن السؤال.
- لا تشرح.
- لا تذكر رقم مادة.
- لا تضف مفاهيم غير موجودة في السؤال.
- حافظ على المعنى الأصلي.
- استخدم المصطلحات النظامية الرسمية الأقرب فقط.

السؤال:
{query}
""".strip()


def rewrite_query(query):
    """Rewrite a user question into formal legal retrieval language."""

    response = client_llm.messages.create(
        model=LLM_MODEL,
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": QUERY_REWRITE_PROMPT.format(
                    query=query
                ),
            }
        ],
    )

    return response.content[0].text.strip()


# ==================================================
# Answer generation prompt
# ==================================================

ANSWER_PROMPT = """
أنت مساعد قانوني متخصص في نظام العمل السعودي.

مهمتك الإجابة عن سؤال المستخدم اعتمادًا حصريًا على النص الصريح للمواد المرفقة.

قواعد إلزامية:
- استخدم فقط المعلومات الموجودة نصًا في المواد المرفقة.
- لا تستخدم معرفتك العامة أو معلومات قانونية من خارج السياق.
- لا تستنتج أثرًا قانونيًا غير منصوص عليه صراحةً.
- لا تحول كلمات مثل "يجب" أو "يلتزم" أو "لا يجوز" إلى حكم بالبطلان أو عدم الصحة أو عدم النظامية ما لم ينص السياق على ذلك صراحةً.
- لا تقل إن شيئًا ما "شرط صحة" أو "شرط بطلان" إلا إذا نص السياق على ذلك صراحةً.
- لا تخترع أحكامًا أو مبالغ أو مددًا أو عقوبات.
- إذا كان النص يقرر واجبًا فقط، فاذكر الواجب فقط.
- إذا سأل المستخدم عن أثر قانوني لا تحدده المواد صراحةً، فاذكر ما تقرره المواد ثم قل إن المواد المسترجعة لا تكفي للجزم بهذا الأثر.
- لا تقدم نصائح أو توصيات أو إجراءات من خارج المواد المرفقة.
- اذكر رقم المادة أو المواد التي استندت إليها.
- اجعل الإجابة مباشرة ومختصرة، ويفضل ألا تتجاوز 250 كلمة.

السؤال:
{question}

المواد المسترجعة:
{context}
""".strip()


# ==================================================
# Answer verification prompt
# ==================================================

VERIFY_PROMPT = """
أنت مدقق قانوني لنظام RAG متخصص في نظام العمل السعودي.

لديك سؤال المستخدم، والمواد المسترجعة، وإجابة أولية.

مهمتك إخراج إجابة نهائية مصححة بحيث يكون كل حكم قانوني فيها مدعومًا صراحةً بالمواد المرفقة.

قواعد إلزامية:
- استخدم فقط المواد المرفقة، ولا تستخدم معرفتك العامة.
- احذف أو صحح أي ادعاء غير مدعوم صراحةً بالنص.
- لا تستنتج أن التصرف باطل أو غير صحيح أو غير نظامي من مجرد وجود كلمة "يجب" أو "لا يجوز".
- لا تقل "باطل" أو "غير صحيح" أو "غير نظامي" إلا إذا كان هذا الأثر منصوصًا عليه صراحةً في المواد.
- إذا كان النص يقرر واجبًا فقط، فاذكر الواجب فقط.
- إذا سأل المستخدم عن أثر مخالفة واجب ولم تحدد المواد هذا الأثر، فقل إن المواد المسترجعة لا تكفي للجزم به.
- لا تضف نصائح أو توصيات أو إجراءات غير منصوص عليها في المواد.
- لا تخترع أحكامًا أو مبالغ أو مددًا أو عقوبات.
- أخرج الإجابة النهائية فقط، ولا تشرح عملية التدقيق.
- اجعل الإجابة واضحة ومختصرة.

السؤال:
{question}

المواد المسترجعة:
{context}

الإجابة الأولية:
{draft_answer}
""".strip()


# ==================================================
# Retrieval rankings
# ==================================================

def dense_ranking(query):
    """Rank all chunks using dense semantic retrieval."""

    embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=len(articles),
    )

    return results["ids"][0]


def bm25_ranking(query):
    """Rank all chunks using BM25 character trigrams."""

    scores = bm25.get_scores(
        tokenize(query)
    )

    order = sorted(
        range(len(articles)),
        key=lambda i: scores[i],
        reverse=True,
    )

    return [
        f"chunk_{i}"
        for i in order
    ]


# ==================================================
# Weighted Reciprocal Rank Fusion
# ==================================================

def weighted_rrf(rankings, weights, k=RRF_K):
    """Fuse multiple retrieval rankings using weighted RRF."""

    fused = {}

    for ranking, weight in zip(rankings, weights):
        for rank, doc_id in enumerate(ranking):
            score = weight / (k + rank)

            fused[doc_id] = (
                fused.get(doc_id, 0)
                + score
            )

    ranked = sorted(
        fused.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        doc_id
        for doc_id, _ in ranked
    ]


# ==================================================
# Candidate pool
# ==================================================

def build_candidates(
    bm25_orig,
    bm25_rw,
    weighted_ids,
    orig_keep=BM25_ORIGINAL_KEEP,
    rw_keep=BM25_REWRITE_KEEP,
    rrf_keep=RRF_KEEP,
):
    """Build a deduplicated candidate pool for reranking."""

    candidates = []
    seen = set()

    for doc_id in bm25_orig[:orig_keep]:
        if doc_id not in seen:
            seen.add(doc_id)
            candidates.append(doc_id)

    for doc_id in bm25_rw[:rw_keep]:
        if doc_id not in seen:
            seen.add(doc_id)
            candidates.append(doc_id)

    for doc_id in weighted_ids[:rrf_keep]:
        if doc_id not in seen:
            seen.add(doc_id)
            candidates.append(doc_id)

    return candidates


# ==================================================
# Cross-encoder reranking
# ==================================================

def rerank(query, ids, top_k=RERANKER_TOP_K):
    """Rerank candidate chunks using a cross-encoder."""

    pairs = [
        [query, id_to_text[doc_id]]
        for doc_id in ids
    ]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(ids, scores),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        doc_id
        for doc_id, _ in ranked[:top_k]
    ]


# ==================================================
# Dual BM25 protection
# ==================================================

def apply_dual_bm25_protection(
    reranker_top5,
    bm25_orig,
    bm25_rw,
    final_k=FINAL_TOP_K,
):
    """
    Combine evidence from the reranker, original-query BM25,
    and rewritten-query BM25.
    """

    candidate_ids = []
    seen = set()

    sources = [
        reranker_top5,
        bm25_orig[:10],
        bm25_rw[:10],
    ]

    for source in sources:
        for doc_id in source:
            if doc_id not in seen:
                seen.add(doc_id)
                candidate_ids.append(doc_id)

    reranker_rank = {
        doc_id: rank
        for rank, doc_id in enumerate(
            reranker_top5,
            start=1,
        )
    }

    bm25_orig_rank = {
        doc_id: rank
        for rank, doc_id in enumerate(
            bm25_orig,
            start=1,
        )
    }

    bm25_rw_rank = {
        doc_id: rank
        for rank, doc_id in enumerate(
            bm25_rw,
            start=1,
        )
    }

    scores = {}

    for doc_id in candidate_ids:
        score = 0.0

        # Reranker evidence
        if doc_id in reranker_rank:
            rank = reranker_rank[doc_id]

            if rank == 1:
                score += 6.0
            elif rank == 2:
                score += 5.0
            elif rank == 3:
                score += 4.0
            elif rank == 4:
                score += 3.0
            elif rank == 5:
                score += 2.0

        # Original-query BM25 evidence
        if doc_id in bm25_orig_rank:
            rank = bm25_orig_rank[doc_id]

            if rank == 1:
                score += 6.0
            elif rank == 2:
                score += 5.0
            elif rank == 3:
                score += 4.0
            elif rank <= 5:
                score += 3.0
            elif rank <= 10:
                score += 1.5

        # Rewritten-query BM25 evidence
        if doc_id in bm25_rw_rank:
            rank = bm25_rw_rank[doc_id]

            if rank == 1:
                score += 6.0
            elif rank == 2:
                score += 5.0
            elif rank == 3:
                score += 4.0
            elif rank <= 5:
                score += 3.0
            elif rank <= 10:
                score += 1.5

        scores[doc_id] = score

    ranked = sorted(
        candidate_ids,
        key=lambda doc_id: scores[doc_id],
        reverse=True,
    )

    return ranked[:final_k]


# ==================================================
# Context construction
# ==================================================

def build_context(final_ids):
    """Build the legal context passed to the LLM."""

    context_parts = []

    for doc_id in final_ids:
        title = id_to_title[doc_id]
        text = id_to_text[doc_id]

        context_parts.append(
            f"{title}\n{text}"
        )

    return "\n\n---\n\n".join(context_parts)


# ==================================================
# Answer generation
# ==================================================

def generate_answer(question, final_ids):
    """Generate a grounded draft answer."""

    context = build_context(final_ids)

    response = client_llm.messages.create(
        model=LLM_MODEL,
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": ANSWER_PROMPT.format(
                    question=question,
                    context=context,
                ),
            }
        ],
    )

    return response.content[0].text.strip()


# ==================================================
# Answer verification
# ==================================================

def verify_answer(question, final_ids, draft_answer):
    """Verify that the final answer is supported by retrieved law."""

    context = build_context(final_ids)

    response = client_llm.messages.create(
        model=LLM_MODEL,
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": VERIFY_PROMPT.format(
                    question=question,
                    context=context,
                    draft_answer=draft_answer,
                ),
            }
        ],
    )

    return response.content[0].text.strip()


# ==================================================
# Retrieval pipeline
# ==================================================

def retrieve(question):
    """
    Run the complete Nizami retrieval pipeline and return
    the final chunk IDs.
    """

    # Query rewrite
    rewritten = rewrite_query(question)

    # Original query retrieval
    dense_orig = dense_ranking(question)
    bm25_orig = bm25_ranking(question)

    # Rewritten query retrieval
    dense_rw = dense_ranking(rewritten)
    bm25_rw = bm25_ranking(rewritten)

    # Weighted 4-way RRF
    weighted_ids = weighted_rrf(
        rankings=[
            dense_orig,
            bm25_orig,
            dense_rw,
            bm25_rw,
        ],
        weights=RRF_WEIGHTS,
    )

    # Candidate pool
    candidates = build_candidates(
        bm25_orig=bm25_orig,
        bm25_rw=bm25_rw,
        weighted_ids=weighted_ids,
        orig_keep=BM25_ORIGINAL_KEEP,
        rw_keep=BM25_REWRITE_KEEP,
        rrf_keep=RRF_KEEP,
    )

    # Cross-encoder reranking
    reranker_top5 = rerank(
        rewritten,
        candidates,
        top_k=RERANKER_TOP_K,
    )

    # Dual BM25 protection
    final_ids = apply_dual_bm25_protection(
        reranker_top5=reranker_top5,
        bm25_orig=bm25_orig,
        bm25_rw=bm25_rw,
        final_k=FINAL_TOP_K,
    )

    return final_ids


# ==================================================
# Public Nizami functions
# ==================================================

def ask_nizami(question):
    """Answer a Saudi Labor Law question."""

    final_ids = retrieve(question)

    draft_answer = generate_answer(
        question,
        final_ids,
    )

    final_answer = verify_answer(
        question,
        final_ids,
        draft_answer,
    )

    return final_answer


def ask_nizami_with_sources(question):
    """Answer a question and return the retrieved legal sources."""

    final_ids = retrieve(question)

    draft_answer = generate_answer(
        question,
        final_ids,
    )

    final_answer = verify_answer(
        question,
        final_ids,
        draft_answer,
    )

    sources = [
        {
            "title": id_to_title[doc_id],
            "text": id_to_text[doc_id],
        }
        for doc_id in final_ids
    ]

    return final_answer, sources


# ==================================================
# Interactive CLI
# ==================================================

def main():
    print("\n" + "=" * 60)
    print("نظامي - مساعد نظام العمل السعودي")
    print("اكتب سؤالك، أو اكتب 'خروج' لإنهاء البرنامج.")
    print("=" * 60)

    while True:
        question = input("\nاسأل نظامي: ").strip()

        if question.lower() in [
            "exit",
            "quit",
            "خروج",
        ]:
            print("تم إنهاء نظامي.")
            break

        if not question:
            continue

        try:
            answer = ask_nizami(question)

            print("\nإجابة نظامي:")
            print(answer)

        except Exception as exc:
            print(f"\nحدث خطأ: {exc}")


if __name__ == "__main__":
    main()