"""
Fix for the final batch not being saved bug

The issue: The batching logic checks if we're at the last paragraph of ALL paragraphs,
not the last paragraph that needs translation. If the last paragraphs are filtered out,
the final batch is never saved.
"""

# The problematic code in main.py around line 833:
# if len(current_batch) >= current_max_size or i == len(paragraphs) - 1:

# SOLUTION: After the while loop ends, we need to check if there's a remaining batch
# that hasn't been saved yet.

# Here's the fix to add after line 839 (after the while loop ends):

"""
    # CRITICAL FIX: Save any remaining batch after loop ends
    if current_batch:
        paragraph_batches.append(current_batch)
        logs.append(f"[BATCH FIX] Added final batch with {len(current_batch)} paragraphs")
"""

# The complete fixed section should look like:

def fixed_batching_logic():
    """
    Fixed version of the batching logic
    """
    # ... existing code ...
    
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i]
        original = para.text
        
        # Skip empty or decorative text
        if not original.strip() or not is_meaningful_text(original) or is_decorative_only(original):
            i += 1
            continue
            
        # ... other filtering logic ...
        
        # Add to current batch
        current_batch.append((i, para, original))
        total_paragraphs_to_translate += 1
        
        # If batch is full, save it
        if len(current_batch) >= current_max_size:
            paragraph_batches.append(current_batch)
            current_batch = []
            current_max_size = 5  # Reset
        
        i += 1
    
    # CRITICAL FIX: Save any remaining batch after loop ends
    if current_batch:
        paragraph_batches.append(current_batch)
        logs.append(f"[BATCH FIX] Added final batch with {len(current_batch)} paragraphs")
    
    # Now paragraph_batches will contain ALL paragraphs, even if the last batch wasn't full
