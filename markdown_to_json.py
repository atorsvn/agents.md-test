import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


HEADING_RE = re.compile(r"^(#+)\s+(.*)$")
SENTENCE_PATTERN = re.compile(r"[^.!?]+[.!?]?\s*")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
INLINE_FOOTNOTE_RE = re.compile(r"\[(footnote:[^\]]+)\]", re.IGNORECASE)
BY_LINE_RE = re.compile(r"^by\s+(.+)$", re.IGNORECASE)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(paragraph: str) -> List[str]:
    paragraph = paragraph.strip()
    if not paragraph:
        return []
    sentences = [normalize_whitespace(match) for match in SENTENCE_PATTERN.findall(paragraph)]
    return [s for s in sentences if s]


def extract_notes(sentence: str) -> Tuple[str, List[str]]:
    notes: List[str] = []

    def footnote_replacer(match: re.Match) -> str:
        notes.append(match.group(1).strip())
        return ""

    def inline_footnote_replacer(match: re.Match) -> str:
        notes.append(match.group(1).strip())
        return ""

    cleaned = FOOTNOTE_REF_RE.sub(footnote_replacer, sentence)
    cleaned = INLINE_FOOTNOTE_RE.sub(inline_footnote_replacer, cleaned)
    return normalize_whitespace(cleaned), notes


def ensure_chapter(current_chapter: Optional[Dict[str, Any]], chapters: List[Dict[str, Any]], fallback_title: str) -> Dict[str, Any]:
    if current_chapter is not None:
        return current_chapter
    chapter = {
        "chapter_number": len(chapters) + 1,
        "chapter_title": fallback_title,
        "paragraphs": [],
    }
    chapters.append(chapter)
    return chapter


def parse_markdown(markdown_text: str) -> Dict[str, Any]:
    lines = markdown_text.splitlines()

    book_title: Optional[str] = None
    book_metadata: Dict[str, Any] = {}
    chapters: List[Dict[str, Any]] = []
    current_chapter: Optional[Dict[str, Any]] = None
    paragraph_lines: List[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, current_chapter
        if current_chapter is None:
            paragraph_lines = []
            return
        paragraph_text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        paragraph_lines = []
        if not paragraph_text:
            return
        sentences_raw = split_sentences(paragraph_text)
        sentences: List[Dict[str, Any]] = []
        for number, sentence in enumerate(sentences_raw, start=1):
            cleaned_sentence, notes = extract_notes(sentence)
            sentence_entry: Dict[str, Any] = {
                "sentence_number": number,
                "text": cleaned_sentence,
            }
            if notes:
                sentence_entry["notes"] = notes
            sentences.append(sentence_entry)
        if not sentences:
            return
        paragraph_entry = {
            "paragraph_number": len(current_chapter["paragraphs"]) + 1,
            "sentences": sentences,
        }
        current_chapter["paragraphs"].append(paragraph_entry)

    for raw_line in lines:
        line = raw_line.rstrip()
        heading_match = HEADING_RE.match(line)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if book_title is None and level == 1:
                book_title = heading_text
                current_chapter = None
                continue
            by_match = BY_LINE_RE.match(heading_text)
            if by_match and "authors" not in book_metadata:
                book_metadata["authors"] = [normalize_whitespace(by_match.group(1))]
            current_chapter = {
                "chapter_number": len(chapters) + 1,
                "chapter_title": heading_text,
                "paragraphs": [],
            }
            chapters.append(current_chapter)
            continue

        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue

        by_match = BY_LINE_RE.match(stripped)
        if by_match and "authors" not in book_metadata:
            book_metadata["authors"] = [normalize_whitespace(by_match.group(1))]

        if stripped.startswith("- "):
            current_chapter = ensure_chapter(current_chapter, chapters, book_title or "Section 1")
            flush_paragraph()
            paragraph_lines = [stripped]
            flush_paragraph()
            continue

        current_chapter = ensure_chapter(current_chapter, chapters, book_title or "Section 1")
        paragraph_lines.append(line)

    flush_paragraph()

    if book_title is None:
        book_title = "Untitled"

    book_data: Dict[str, Any] = {
        "title": book_title,
        "chapters": chapters,
    }
    if book_metadata:
        book_data["metadata"] = book_metadata

    return {"book": book_data}


def run(input_path: Path, output_path: Path) -> None:
    markdown_text = input_path.read_text(encoding="utf-8")
    data = parse_markdown(markdown_text)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transform a Markdown book into structured JSON.")
    parser.add_argument("--input", dest="input_path", default="book_iv.md", help="Path to the Markdown input file.")
    parser.add_argument("--output", dest="output_path", default="book_iv.json", help="Path for the JSON output.")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if not input_path.exists():
        alt_path = Path("boot_iv.md")
        if alt_path.exists():
            input_path = alt_path
        else:
            raise FileNotFoundError(f"Input file '{args.input_path}' not found.")

    output_path = Path(args.output_path)
    run(input_path, output_path)


if __name__ == "__main__":
    main()
