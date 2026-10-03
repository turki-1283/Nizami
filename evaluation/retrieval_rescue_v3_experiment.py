import json
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALUATION_DIR = Path(__file__).resolve().parent
FIXED_REWRITES_FILE = EVALUATION_DIR / "fixed_rewrites.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import nizami


# ============================================================
# Frozen 49-question benchmark
# ============================================================

TEST_CASES = [
    ("كم أقصى مدة لفترة التجربة؟", "المادة الثالثة والخمسون"),
    ("هل يجوز وضع العامل تحت التجربة أكثر من مرة؟", "المادة الرابعة والخمسون"),
    ("هل يقدر صاحب العمل ينقلني لمدينة ثانية بدون موافقتي؟", "المادة الثامنة والخمسون"),
    ("هل يحق لصاحب العمل يغير طبيعة عملي بشكل جوهري؟", "المادة الستون"),
    ("متى أستحق إجازة سنوية؟", "المادة التاسعة بعد المائة"),
    ("هل العقد غير المكتوب يعتبر صحيح؟", "المادة الحادية والخمسون"),
    ("وش البيانات الأساسية اللي لازم تكون في عقد العمل؟", "المادة الثانية والخمسون"),
    ("متى يتحول العقد المحدد إلى غير محدد؟", "المادة الخامسة والخمسون"),
    ("إذا حضرت للعمل وصاحب العمل منعني، هل أستحق أجر؟", "المادة الثانية والستون"),
    ("هل يحق للشركة تحتجز جزء من راتبي بدون سند؟", "المادة الحادية والستون"),

    ("وش حقوقي إذا انتهى عقد العمل؟", "المادة الرابعة والستون"),
    ("هل العامل ملزم يحافظ على أدوات وممتلكات المنشأة؟", "المادة الخامسة والستون"),
    ("هل أقدر أشتغل عند صاحب عمل ثاني وأنا غير سعودي؟", "المادة التاسعة والثلاثون"),
    ("مين يتحمل رسوم الإقامة ورخصة العمل؟", "المادة الأربعون"),
    ("هل يجوز نقل العامل من راتب شهري إلى أجر بالساعة بدون موافقته؟", "المادة التاسعة والخمسون"),
    ("وش شروط فترة التجربة في العقد؟", "المادة الثالثة والخمسون"),
    ("وش يصير إذا تغير مالك المنشأة؟", "المادة الثامنة عشرة"),
    ("هل العامل غير السعودي لازم يكون عقده محدد المدة؟", "المادة السابعة والثلاثون"),
    ("هل العربية هي اللغة المعتمدة في عقود العمل؟", "المادة التاسعة"),
    ("كيف تُحسب المدد والمواعيد في نظام العمل؟", "المادة العاشرة"),

    ("إذا العامل ما حضر الدوام بدون عذر، وش الإجراء النظامي؟", "المادة الثمانون"),
    ("هل يقدر صاحب العمل يفصلني بدون مكافأة أو إشعار؟", "المادة الثمانون"),
    ("متى ينتهي عقد العمل بشكل نظامي؟", "المادة الرابعة والسبعون"),
    ("إذا استقلت، هل لي مكافأة نهاية خدمة؟", "المادة الخامسة والثمانون"),
    ("كيف تنحسب مكافأة نهاية الخدمة؟", "المادة الرابعة والثمانون"),
    ("هل أقدر آخذ إجازة للزواج؟", "المادة الثالثة عشرة بعد المائة"),
    ("كم إجازة الوفاة للعامل؟", "المادة الثالثة عشرة بعد المائة"),
    ("هل يحق لي إجازة عشان الاختبارات؟", "المادة الخامسة عشرة بعد المائة"),
    ("كم عدد ساعات العمل اليومية؟", "المادة الثامنة والتسعون"),
    ("هل لازم يكون فيه فترة راحة أثناء الدوام؟", "المادة الأولى بعد المائة"),

    ("هل يجوز تشغيل العامل أكثر من خمس ساعات متواصلة؟", "المادة الأولى بعد المائة"),
    ("كم ساعات العمل في رمضان للمسلمين؟", "المادة الثامنة والتسعون"),
    ("هل الجمعة هي يوم الراحة الأسبوعية؟", "المادة الرابعة بعد المائة"),
    ("هل يحق للعامل أجر إضافي على العمل الإضافي؟", "المادة السابعة بعد المائة"),
    ("كيف يُحسب أجر الساعات الإضافية؟", "المادة السابعة بعد المائة"),
    ("هل يجوز تأخير راتب العامل؟", "المادة التسعون"),
    ("متى يجب دفع راتب العامل الشهري؟", "المادة التسعون"),
    ("هل يحق لصاحب العمل يخصم من راتبي بسبب تلف شيء؟", "المادة الحادية والتسعون"),
    ("كم الحد الأقصى للخصم من أجر العامل؟", "المادة الثالثة والتسعون"),
    ("إذا صاحب العمل تأخر في دفع الراتب وش يصير؟", "المادة الرابعة والتسعون"),

    ("هل يحق للعامل يرفض عمل يختلف كلياً عن عمله المتفق عليه؟", "المادة الستون"),
    ("هل يجوز نقل العامل لمكان يغير محل إقامته؟", "المادة الثامنة والخمسون"),
    ("إذا تغير صاحب المنشأة هل عقدي يستمر؟", "المادة الثامنة عشرة"),
    ("هل صاحب العمل الجديد يتحمل حقوق العمال السابقة؟", "المادة الثامنة عشرة"),
    ("هل عقد غير السعودي لازم يكون مكتوب؟", "المادة السابعة والثلاثون"),
    ("من يدفع رسوم تغيير المهنة؟", "المادة الأربعون"),
    ("من يتحمل تذكرة عودة العامل غير السعودي بعد انتهاء العلاقة؟", "المادة الأربعون"),
    ("هل يجوز لصاحب العمل توظيف عامل تابع لصاحب عمل آخر؟", "المادة التاسعة والثلاثون"),
    ("هل العامل يقدر يشتغل لحسابه الخاص؟", "المادة التاسعة والثلاثون"),
]

TOTAL_QUESTIONS = len(TEST_CASES)


# ============================================================
# Helpers
# ============================================================

def load_fixed_rewrites():
    with open(FIXED_REWRITES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def article_key(doc_id):
    """
    Group chunks belonging to the same legal article.

    Example:
        المادة الحادية والثمانون: فقرة 1
        المادة الحادية والثمانون: فقرة 6

    Both become:
        المادة الحادية والثمانون
    """

    title = nizami.id_to_title[doc_id].strip()

    if ": فقرة" in title:
        title = title.split(": فقرة")[0]

    return title.rstrip(":").strip()


def contains_expected(ids, expected_title):
    for rank, doc_id in enumerate(ids, start=1):
        title = nizami.id_to_title[doc_id]

        if expected_title in title:
            return rank

    return None


def add_diverse_candidates(
    rescue,
    seen_docs,
    ranking,
    top_k,
    max_add,
):
    """
    Add missing candidates while preferring new legal articles.

    Pass 1:
        Prefer documents from articles not already represented.

    Pass 2:
        If rescue slots remain, allow another chunk from an
        already represented article.

    Document IDs are always deduplicated.
    """

    added = 0

    represented_articles = {
        article_key(doc_id)
        for doc_id in rescue
    }

    # Pass 1: prefer new articles
    for doc_id in ranking[:top_k]:
        if added >= max_add:
            break

        if doc_id in seen_docs:
            continue

        key = article_key(doc_id)

        if key in represented_articles:
            continue

        rescue.append(doc_id)
        seen_docs.add(doc_id)
        represented_articles.add(key)

        added += 1

    # Pass 2: fill remaining slots if necessary
    if added < max_add:
        for doc_id in ranking[:top_k]:
            if added >= max_add:
                break

            if doc_id in seen_docs:
                continue

            rescue.append(doc_id)
            seen_docs.add(doc_id)

            added += 1

    return added


# ============================================================
# Current pipeline using frozen rewrite
# ============================================================

def current_pipeline(question, rewritten):
    dense_orig = nizami.dense_ranking(question)
    bm25_orig = nizami.bm25_ranking(question)

    dense_rw = nizami.dense_ranking(rewritten)
    bm25_rw = nizami.bm25_ranking(rewritten)

    weighted_ids = nizami.weighted_rrf(
        rankings=[
            dense_orig,
            bm25_orig,
            dense_rw,
            bm25_rw,
        ],
        weights=nizami.RRF_WEIGHTS,
    )

    candidates = nizami.build_candidates(
        bm25_orig=bm25_orig,
        bm25_rw=bm25_rw,
        weighted_ids=weighted_ids,
        orig_keep=nizami.BM25_ORIGINAL_KEEP,
        rw_keep=nizami.BM25_REWRITE_KEEP,
        rrf_keep=nizami.RRF_KEEP,
    )

    reranker_top5 = nizami.rerank(
        rewritten,
        candidates,
        top_k=nizami.RERANKER_TOP_K,
    )

    final_ids = nizami.apply_dual_bm25_protection(
        reranker_top5=reranker_top5,
        bm25_orig=bm25_orig,
        bm25_rw=bm25_rw,
        final_k=nizami.FINAL_TOP_K,
    )

    return {
        "final": final_ids,
        "bm25_orig": bm25_orig,
        "bm25_rw": bm25_rw,
        "dense_orig": dense_orig,
        "dense_rw": dense_rw,
        "rrf": weighted_ids,
    }


# ============================================================
# Rescue V3
# ============================================================

def build_rescue_v3(result):
    """
    Rescue V3:

    1. Preserve Current Top-5 exactly.
    2. Add up to 2 documents from BM25 Original Top-2.
    3. Add up to 2 documents from BM25 Rewrite Top-5.
    4. Add up to 1 document from RRF Top-5.
    5. Prefer article diversity.
    6. Deduplicate document IDs.

    Maximum theoretical context size = 10 documents.
    """

    rescue = list(result["final"])
    seen_docs = set(rescue)

    # --------------------------------------------------------
    # V1 strength:
    # BM25 Original Top-2
    # --------------------------------------------------------

    add_diverse_candidates(
        rescue=rescue,
        seen_docs=seen_docs,
        ranking=result["bm25_orig"],
        top_k=2,
        max_add=2,
    )

    # --------------------------------------------------------
    # Wider rewritten lexical evidence:
    # BM25 Rewrite Top-5
    # --------------------------------------------------------

    add_diverse_candidates(
        rescue=rescue,
        seen_docs=seen_docs,
        ranking=result["bm25_rw"],
        top_k=5,
        max_add=2,
    )

    # --------------------------------------------------------
    # Strong fused evidence:
    # RRF Top-5
    # --------------------------------------------------------

    add_diverse_candidates(
        rescue=rescue,
        seen_docs=seen_docs,
        ranking=result["rrf"],
        top_k=5,
        max_add=1,
    )

    return rescue


# ============================================================
# Batch runner
# ============================================================

def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "py -3.14 evaluation/retrieval_rescue_v3_experiment.py <batch>\n\n"
            "Batch must be 1 to 5."
        )
        return

    try:
        batch_number = int(sys.argv[1])

    except ValueError:
        print("Batch must be a number from 1 to 5.")
        return

    if batch_number < 1 or batch_number > 5:
        print("Batch must be from 1 to 5.")
        return

    rewrites = load_fixed_rewrites()

    batch_size = 10

    start = (batch_number - 1) * batch_size
    end = min(start + batch_size, TOTAL_QUESTIONS)

    selected_cases = TEST_CASES[start:end]

    if not selected_cases:
        print(
            f"No questions found for batch {batch_number}."
        )
        return

    print("\n" + "=" * 90)

    print(
        f"NIZAMI RETRIEVAL RESCUE V3 - "
        f"BATCH {batch_number}/5"
    )

    print(
        f"QUESTIONS {start + 1}-{end} "
        f"OF {TOTAL_QUESTIONS}"
    )

    print("=" * 90)

    current_top1 = 0
    current_retrieved = 0

    rescue_top1 = 0
    rescue_retrieved = 0

    fixed_cases = []
    lost_cases = []
    still_failed = []

    for local_index, (question, expected) in enumerate(
        selected_cases,
        start=start + 1,
    ):
        print(
            f"\nRunning question "
            f"{local_index}/{TOTAL_QUESTIONS}..."
        )

        rewritten = rewrites.get(question)

        if rewritten is None:
            print(
                f"Missing frozen rewrite: "
                f"{question}"
            )
            continue

        result = current_pipeline(
            question,
            rewritten,
        )

        current_ids = result["final"]
        rescue_ids = build_rescue_v3(result)

        current_rank = contains_expected(
            current_ids,
            expected,
        )

        rescue_rank = contains_expected(
            rescue_ids,
            expected,
        )

        # ----------------------------------------------------
        # Current metrics
        # ----------------------------------------------------

        if current_rank == 1:
            current_top1 += 1

        if current_rank is not None:
            current_retrieved += 1

        # ----------------------------------------------------
        # Rescue V3 metrics
        # ----------------------------------------------------

        if rescue_rank == 1:
            rescue_top1 += 1

        if rescue_rank is not None:
            rescue_retrieved += 1

        # ----------------------------------------------------
        # Fixed / lost
        # ----------------------------------------------------

        if (
            current_rank is None
            and rescue_rank is not None
        ):
            fixed_cases.append(
                {
                    "question": question,
                    "expected": expected,
                    "rank": rescue_rank,
                }
            )

        if (
            current_rank is not None
            and rescue_rank is None
        ):
            lost_cases.append(
                {
                    "question": question,
                    "expected": expected,
                }
            )

        if rescue_rank is None:
            still_failed.append(
                {
                    "question": question,
                    "expected": expected,
                    "current": current_ids,
                    "rescue": rescue_ids,
                    "bm25_orig": result["bm25_orig"],
                    "bm25_rw": result["bm25_rw"],
                    "rrf": result["rrf"],
                }
            )

        current_display = (
            current_rank
            if current_rank is not None
            else "OUT"
        )

        rescue_display = (
            rescue_rank
            if rescue_rank is not None
            else "OUT"
        )

        print(
            f"[{local_index:02d}/{TOTAL_QUESTIONS}] "
            f"CURRENT={current_display} | "
            f"RESCUE_V3={rescue_display} | "
            f"{expected}"
        )

    total = len(selected_cases)

    # ========================================================
    # Results
    # ========================================================

    print("\n" + "=" * 90)
    print(f"BATCH {batch_number} RESULTS")
    print("=" * 90)

    print("\nCURRENT")

    print(
        f"Top-1: {current_top1}/{total} "
        f"= {current_top1 / total * 100:.1f}%"
    )

    print(
        f"Retrieved: {current_retrieved}/{total} "
        f"= {current_retrieved / total * 100:.1f}%"
    )

    print("\nRESCUE V3")

    print(
        f"Top-1: {rescue_top1}/{total} "
        f"= {rescue_top1 / total * 100:.1f}%"
    )

    print(
        f"Retrieved: {rescue_retrieved}/{total} "
        f"= {rescue_retrieved / total * 100:.1f}%"
    )

    print(
        f"\nFixed failures: "
        f"{len(fixed_cases)}"
    )

    print(
        f"Lost previous hits: "
        f"{len(lost_cases)}"
    )

    # ========================================================
    # Fixed cases
    # ========================================================

    print("\n" + "=" * 90)
    print("FIXED CASES")
    print("=" * 90)

    if not fixed_cases:
        print("None")

    else:
        for case in fixed_cases:
            print(
                f"\nQuestion: {case['question']}\n"
                f"Expected: {case['expected']}\n"
                f"Rescue V3 rank: {case['rank']}"
            )

    # ========================================================
    # Lost cases
    # ========================================================

    print("\n" + "=" * 90)
    print("LOST CASES")
    print("=" * 90)

    if not lost_cases:
        print("None")

    else:
        for case in lost_cases:
            print(
                f"\nQuestion: {case['question']}\n"
                f"Expected: {case['expected']}"
            )

    # ========================================================
    # Still failed
    # ========================================================

    print("\n" + "=" * 90)
    print("STILL FAILED AFTER RESCUE V3")
    print("=" * 90)

    if not still_failed:
        print("None")

    else:
        for case in still_failed:
            print("\n" + "-" * 90)

            print(
                f"Question: "
                f"{case['question']}"
            )

            print(
                f"Expected: "
                f"{case['expected']}"
            )

            print("\nCurrent Top-5:")

            for rank, doc_id in enumerate(
                case["current"],
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"{nizami.id_to_title[doc_id]}"
                )

            print("\nRescue V3 Context:")

            for rank, doc_id in enumerate(
                case["rescue"],
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"{nizami.id_to_title[doc_id]}"
                )

            print("\nBM25 Original Top-10:")

            for rank, doc_id in enumerate(
                case["bm25_orig"][:10],
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"{nizami.id_to_title[doc_id]}"
                )

            print("\nBM25 Rewrite Top-10:")

            for rank, doc_id in enumerate(
                case["bm25_rw"][:10],
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"{nizami.id_to_title[doc_id]}"
                )

            print("\nRRF Top-10:")

            for rank, doc_id in enumerate(
                case["rrf"][:10],
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"{nizami.id_to_title[doc_id]}"
                )

    print("\n" + "=" * 90)

    print(
        f"RESCUE V3 BATCH {batch_number} "
        f"FINISHED SUCCESSFULLY"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()