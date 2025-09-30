

# agents.md

## Agent Overview

| Attribute        | Value                                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Agent Name**   | Codex Refactor Agent                                                                                                             |
| **Purpose**      | Transform a Markdown file (`book_iv.md`) into structured JSON with explicit hierarchy: **book → chapter → paragraph → sentence** |
| **Primary File** | `book_iv.md`                                                                                                                     |
| **Output File**  | `book_iv.json`                                                                                                                   |

---

## Capabilities

1. **Markdown Parsing**

   * Load the input file `book_iv.md`.
   * Normalize headings, paragraphs, and line breaks.

2. **Structural Segmentation**

   * Detect **book-level metadata** (title, author if present).
   * Split into **chapters** based on Markdown headers (`#`, `##`, etc.).
   * Further split into **paragraphs** on double line breaks.
   * Split paragraphs into **sentences** using punctuation rules.

3. **JSON Refactoring**

   * Nest output into the following schema:

     ```json
     {
       "book": {
         "title": "...",
         "chapters": [
           {
             "chapter_number": 1,
             "chapter_title": "...",
             "paragraphs": [
               {
                 "paragraph_number": 1,
                 "sentences": [
                   "First sentence.",
                   "Second sentence."
                 ]
               }
             ]
           }
         ]
       }
     }
     ```
   * Ensure sequential numbering of chapters and paragraphs.

4. **Validation**

   * Validate JSON output for correct nesting and formatting.
   * Guarantee no text is lost in transformation.

---

## Invocation

Run the agent with the following directive:

```bash
codex run refactor --input book_iv.md --output book_iv.json --mode structured-json
```

---

## Safety & Constraints

* Do not alter the **semantic content** of the text.
* Preserve all words, punctuation, and ordering.
* If Markdown contains footnotes or references, store them in a `notes` field under the corresponding sentence.
* Ensure JSON is valid and human-readable (pretty-print).

u want me to also **generate a Python script** alongside this `agents.md` that will actually do the Markdown → JSON refactor? That way Codex (or you) can run it directly.
