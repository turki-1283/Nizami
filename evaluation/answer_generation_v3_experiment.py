import json
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALUATION_DIR = Path(__file__).resolve().parent

FIXED_REWRITES_FILE = EVALUATION_DIR / "fixed_rewrites.json"
RESULTS_FILE = EVALUATION_DIR / "answer_generation_v3_results.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import nizami


# ============================================================
# Validated 49-question benchmark
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
BATCH_SIZE = 10
# ============================================================
# Helpers
# ============================================================

def load_fixed_rewrites():
    with FIXED_REWRITES_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_results():
    if not RESULTS_FILE.exists():
        return {}

    try:
        with RESULTS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)
    except Exception:
        return {}


def save_results(results):
    with RESULTS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )


def article_key(doc_id):
    title = nizami.id_to_title[doc_id].strip()

    if ": فقرة" in title:
        title = title.split(": فقرة")[0]

    return title.rstrip(":").strip()


def add_diverse_candidates(
    rescue,
    seen_docs,
    ranking,
    top_k,
    max_add,
):
    added = 0

    represented_articles = {
        article_key(doc_id)
        for doc_id in rescue
    }

    # Pass 1: prefer new legal articles.
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

    # Pass 2: fill remaining slots if necessary.
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
# Frozen retrieval
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
        "rrf": weighted_ids,
    }


# ============================================================
# Rescue V3
# ============================================================

def build_rescue_v3(result):
    rescue = list(result["final"])
    seen_docs = set(rescue)

    add_diverse_candidates(
        rescue,
        seen_docs,
        result["bm25_orig"],
        top_k=2,
        max_add=2,
    )

    add_diverse_candidates(
        rescue,
        seen_docs,
        result["bm25_rw"],
        top_k=5,
        max_add=2,
    )

    add_diverse_candidates(
        rescue,
        seen_docs,
        result["rrf"],
        top_k=5,
        max_add=1,
    )

    return rescue


# ============================================================
# Expected article check
# ============================================================

def expected_article_mentioned(
    expected_article,
    final_answer,
):
    """
    Simple automatic signal only.

    This does NOT judge legal correctness.
    It only checks whether the expected article name/number
    appears in the final answer in a usable form.
    """

    expected_number = (
        expected_article
        .replace("المادة", "")
        .strip()
    )

    return (
        expected_article in final_answer
        or expected_number in final_answer
    )


# ============================================================
# Batch runner
# ============================================================

def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "py -3.14 "
            "evaluation/answer_generation_v3_experiment.py "
            "<batch_number>"
        )
        print("\nBatch numbers: 1 to 5")
        return

    try:
        batch_number = int(sys.argv[1])
    except ValueError:
        print("Batch number must be an integer from 1 to 5.")
        return

    total_batches = (
        TOTAL_QUESTIONS + BATCH_SIZE - 1
    ) // BATCH_SIZE

    if batch_number < 1 or batch_number > total_batches:
        print(
            f"Batch number must be between "
            f"1 and {total_batches}."
        )
        return

    start = (batch_number - 1) * BATCH_SIZE
    end = min(
        start + BATCH_SIZE,
        TOTAL_QUESTIONS,
    )

    batch_cases = TEST_CASES[start:end]

    if not batch_cases:
        print("No questions in this batch.")
        return

    rewrites = load_fixed_rewrites()
    saved_results = load_results()

    print("\n" + "=" * 90)
    print(
        f"NIZAMI ANSWER GENERATION V3 "
        f"- BATCH {batch_number}/{total_batches}"
    )
    print(
        f"QUESTIONS {start + 1}-{end} "
        f"OF {TOTAL_QUESTIONS}"
    )
    print("=" * 90)

    mentioned_count = 0
    errors = 0

    for local_index, (question, expected) in enumerate(
        batch_cases,
        start=1,
    ):
        question_number = start + local_index

        print("\n" + "=" * 90)
        print(
            f"QUESTION {question_number}/"
            f"{TOTAL_QUESTIONS}"
        )
        print("=" * 90)

        print(f"\nQuestion:\n{question}")
        print(f"\nExpected article:\n{expected}")

        rewritten = rewrites.get(question)

        if rewritten is None:
            print("\nERROR: Frozen rewrite not found.")
            errors += 1
            continue

        print(f"\nFrozen rewrite:\n{rewritten}")

        try:
            # ----------------------------------------
            # Retrieval
            # ----------------------------------------

            result = current_pipeline(
                question,
                rewritten,
            )

            rescue_ids = build_rescue_v3(result)

            context_titles = [
                nizami.id_to_title[doc_id]
                for doc_id in rescue_ids
            ]

            print(
                f"\nRescue V3 context "
                f"({len(rescue_ids)} chunks):"
            )

            for rank, title in enumerate(
                context_titles,
                start=1,
            ):
                print(f"  {rank}. {title}")

            # ----------------------------------------
            # Generate
            # ----------------------------------------

            print("\nGenerating draft answer...")

            draft_answer = nizami.generate_answer(
                question,
                rescue_ids,
            )

            # ----------------------------------------
            # Verify
            # ----------------------------------------

            print("Verifying answer...")

            final_answer = nizami.verify_answer(
                question,
                rescue_ids,
                draft_answer,
            )

            # ----------------------------------------
            # Automatic article signal
            # ----------------------------------------

            article_mentioned = (
                expected_article_mentioned(
                    expected,
                    final_answer,
                )
            )

            if article_mentioned:
                mentioned_count += 1

            status = (
                "YES"
                if article_mentioned
                else "NO"
            )

            print(
                "\nExpected article mentioned: "
                f"{status}"
            )

            print("\nFINAL VERIFIED ANSWER")
            print("-" * 90)
            print(final_answer)

            # ----------------------------------------
            # Save result
            # ----------------------------------------

            saved_results[str(question_number)] = {
                "question": question,
                "expected_article": expected,
                "frozen_rewrite": rewritten,
                "context_ids": rescue_ids,
                "context_titles": context_titles,
                "draft_answer": draft_answer,
                "final_answer": final_answer,
                "expected_article_mentioned": (
                    article_mentioned
                ),
            }

            save_results(saved_results)

        except Exception as exc:
            errors += 1

            print(
                "\nERROR while processing question "
                f"{question_number}:"
            )
            print(exc)

    # ========================================================
    # Batch summary
    # ========================================================

    batch_total = len(batch_cases)
    completed = batch_total - errors

    print("\n" + "=" * 90)
    print(
        f"BATCH {batch_number} FINISHED"
    )
    print("=" * 90)

    print(
        f"\nCompleted: "
        f"{completed}/{batch_total}"
    )

    print(
        f"Expected article mentioned: "
        f"{mentioned_count}/{batch_total}"
    )

    print(
        f"Errors: {errors}"
    )

    print(
        "\nResults saved to:\n"
        f"{RESULTS_FILE}"
    )

    print(
        "\nNOTE: Expected article mention is only "
        "an automatic signal."
    )
    print(
        "Legal correctness will be evaluated "
        "separately from the final answers."
    )


if __name__ == "__main__":
    main()