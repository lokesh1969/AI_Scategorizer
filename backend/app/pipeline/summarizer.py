import re

def generate_summary(text: str, max_sentences: int = 3) -> str:
    """
    Generates a concise extractive summary preserving Hindi and English language sentences.
    Ranks sentences based on term frequencies and sentence positions.
    """
    if not text or not text.strip():
        return "No text available to summarize."

    # Split text into sentences (supporting English .!? and Hindi | danda)
    sentences = [s.strip() for s in re.split(r'[\.\!\?\।\n]+', text) if len(s.strip()) > 10]

    if not sentences:
        return text[:200] + ("..." if len(text) > 200 else "")

    if len(sentences) <= max_sentences:
        return "\n".join([f"• {s}." for s in sentences])

    # Word frequency map
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        if len(w) > 2:
            freq[w] = freq.get(w, 0) + 1

    # Score sentences
    scores = []
    for idx, sentence in enumerate(sentences):
        score = 0
        s_words = re.findall(r'\w+', sentence.lower())
        for w in s_words:
            if w in freq:
                score += freq[w]
        
        # Position bonus for lead sentences
        if idx == 0:
            score *= 1.5
        elif idx == 1:
            score *= 1.25

        scores.append((score, idx, sentence))

    # Sort by score descending and take top N
    scores.sort(key=lambda x: x[0], reverse=True)
    selected = scores[:max_sentences]

    # Re-order by original position
    selected.sort(key=lambda x: x[1])

    summary_bullets = [f"• {x[2]}." for x in selected]
    return "\n".join(summary_bullets)
