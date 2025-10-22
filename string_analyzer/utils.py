import hashlib
import re


def sha256_hash(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def is_palindrome(s: str) -> bool:
    cleaned = "".join(ch.lower() for ch in s if not ch.isspace())
    return cleaned == cleaned[::-1]

def char_freq_map(s: str):
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def analyze_string(value: str):
    if not isinstance(value, str):
        raise TypeError("Value must be string")
    return {
        "length": len(value),
        "is_palindrome": is_palindrome(value),
        "unique_characters": len(set(value)),
        "word_count": len(re.findall(r'\S+', value)),
        "sha256_hash": sha256_hash(value),
        "character_frequency_map": char_freq_map(value)
    }
    
def parse_natural_language(query: str):
    q = query.lower().strip()
    filters = {}
    
    
    if "palindromic" in q or "palindrome" in q:
        filters['is_palindrome'] = True
    
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1

    import re
    if match := re.search(r"longer than (\d+)", q):
        filters["min_length"] = int(match.group(1)) + 1
    if match := re.search(r"containing the letter (\w)", q):
        filters["contains_character"] = match.group(1)
    if "first vowel" in q:
        filters["contains_character"] = "a"

    if not filters:
        raise ValueError("Unable to parse natural language query")
    return filters