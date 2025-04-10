"""
cleaner.py

Text cleaning and blocklist filtering before summarization.
"""

import re
import string
import unicodedata

def clean_extracted_text(
    text: str,
    *,
    query: str = "",
    url: str = "",
    doc_id: str = "",
    return_matches: bool = False
):
    if not text or len(text) < 100:
        return ("", []) if return_matches else ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+\s?", " ", text)

    block_patterns = [
        r"(?i)instagram\\b.*", r"(?i)linkedin\\b.*", r"(?i)facebook\\b.*", r"(?i)twitter\\b.*",
        r"(?i)youtube\\b.*", r"(?i)follow us.*", r"(?i)stay connected.*",
        r"(?i)subscribe to email alerts.*", r"(?i)receive email alerts.*",
        r"(?i)email address.*", r"(?i)email subscriptions.*", r"(?i)unsubscribe.*",
        r"(?i)contact us.*", r"(?i)feedback.*", r"(?i)faqs.*", r"(?i)help center.*",
        r"(?i)customer support.*", r"(?i)support center.*", r"(?i)terms.*",
        r"(?i)privacy policy.*", r"(?i)all rights reserved.*", r"(?i)back to top.*",
        r"(?i)click here.*", r"(?i)login.*", r"(?i)sign up.*", r"(?i)download our app.*"
    ]

    removed_matches = []
    for pattern in block_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            removed_matches.append({"pattern": pattern, "matched": m})
        text = re.sub(pattern, "", text)

    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    lines = re.split(r"(?<=[.!?])\s+", text)
    clean_lines = [
        line.strip() for line in lines
        if line and len(line) >= 50 and len(line.split()) >= 6 and not all(c in string.punctuation for c in line)
    ]

    cleaned_text = " ".join(clean_lines)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()

    return (cleaned_text, removed_matches) if return_matches else cleaned_text
