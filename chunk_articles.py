import json
import re
from pathlib import Path


INPUT_FILE = Path("data/articles_clean.json")
OUTPUT_FILE = Path("chunks.json")

MIN_ARTICLE_LENGTH = 15
SHORT_ARTICLE_THRESHOLD = 400


def load_articles():
    """Load cleaned Saudi Labor Law articles."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE}."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    # Remove repealed articles and very short entries.
    return [
        article
        for article in articles
        if "ملغاة" not in article["text"]
        and len(article["text"]) > MIN_ARTICLE_LENGTH
    ]


def split_into_chunks(article):
    """Split a labor law article into smaller numbered sections when possible."""

    title = article["title"]
    text = article["text"]

    # Keep short articles as a single chunk.
    if len(text) < SHORT_ARTICLE_THRESHOLD:
        return [
            {
                "title": title,
                "text": text,
            }
        ]

    # Detect numbered sections such as "1." and "2."
    pattern = r"(?:^|\s)(\d+)\.\s"
    parts = re.split(pattern, text)

    # Keep the entire article if no numbered sections are found.
    if len(parts) <= 1:
        return [
            {
                "title": title,
                "text": text,
            }
        ]

    chunks = []
    intro = parts[0].strip()

    if len(intro) > 20:
        chunks.append(
            {
                "title": title,
                "text": intro,
            }
        )

    for i in range(1, len(parts) - 1, 2):
        number = parts[i]
        content = parts[i + 1].strip()

        chunk_text = (
            f"{intro} ({number}) {content}"
            if intro
            else f"({number}) {content}"
        )

        chunks.append(
            {
                "title": f"{title} فقرة {number}",
                "text": chunk_text,
            }
        )

    return chunks


def build_chunks(articles):
    """Generate chunks for all articles."""

    chunks = []

    for article in articles:
        chunks.extend(split_into_chunks(article))

    return chunks


def save_chunks(chunks):
    """Save generated chunks to JSON."""

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main():
    articles = load_articles()
    chunks = build_chunks(articles)

    print(f"Original articles: {len(articles)}")
    print(f"Generated chunks: {len(chunks)}")

    save_chunks(chunks)

    print(f"Chunks saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()