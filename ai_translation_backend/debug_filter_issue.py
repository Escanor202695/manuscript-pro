"""
Debug script to understand why paragraphs are being filtered out
"""

import re

def is_meaningful_text(text):
    """Check if text contains meaningful content"""
    cleaned = re.sub(r'[\W_]+', '', text)
    return bool(cleaned.strip())

def is_decorative_only(text):
    """Check if text is decorative only (symbols, single letters, etc.)"""
    stripped = text.strip()
    return not stripped or re.fullmatch(r"[^\w\s]+", stripped) or re.fullmatch(r"[A-Z]", stripped)

# Test various text patterns
test_texts = [
    "Hello world",  # Normal text
    "¿Cómo estás?",  # Spanish with special chars
    "1. First item",  # Numbered list
    "• Bullet point",  # Bullet point
    "★ Star item",  # Symbol with text
    "___",  # Decorative line
    "A",  # Single letter
    "Chapter 1",  # Normal chapter
    "§1.2 Section",  # Section with symbol
    "@author",  # Special char start
    "#hashtag",  # Hash start
    "100%",  # Number with symbol
    "",  # Empty
    "   ",  # Whitespace only
]

print("Testing text filtering logic:\n")
print(f"{'Text':<30} {'Meaningful?':<15} {'Decorative?':<15} {'Will Skip?'}")
print("-" * 80)

for text in test_texts:
    is_meaningful = is_meaningful_text(text)
    is_decorative = is_decorative_only(text)
    will_skip = not is_meaningful or is_decorative
    
    display_text = repr(text) if not text.strip() else text
    print(f"{display_text:<30} {str(is_meaningful):<15} {str(is_decorative):<15} {'YES' if will_skip else 'NO'}")

print("\n\nPossible issues:")
print("1. Text with only special characters (like '¿Cómo estás?') might be considered not meaningful")
print("2. Numbered lists might be filtered out")
print("3. Bullet points might be skipped")
print("4. Text starting with symbols might be rejected")
