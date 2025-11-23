# Smart Timeout System - Progress-Based Detection

## Overview

The timeout system now only triggers when translation is **stuck** (no progress), not just because it's taking a long time.

---

## How It Works

### ✅ No Fixed Time Limit
- Translation can run for **any duration** (hours if needed)
- No artificial 25-minute or 60-minute timeout
- Perfect for large documents (1000+ pages)

### 🔍 Stuck Detection
- Monitors batch progress every second
- If **no progress for 10 minutes** → triggers stuck timeout
- Resets timer every time a batch completes

### 📊 Progress Tracking
```
Batch 39/65 complete → Timer resets to 0
Batch 40/65 complete → Timer resets to 0
...waiting 10 minutes with no progress...
→ STUCK DETECTED → Timeout triggered
```

---

## Implementation Details

### Frontend (page.js)

**Polling Function:**
```javascript
const pollBatchProgress = (progressId, onError) => {
  let lastCompletedBatches = -1;
  let lastProgressTime = Date.now(); // Track last progress
  const STUCK_TIMEOUT = 10 * 60 * 1000; // 10 minutes

  setInterval(async () => {
    // Check if stuck
    const timeSinceProgress = Date.now() - lastProgressTime;
    if (timeSinceProgress > STUCK_TIMEOUT) {
      onError(`Translation stuck - no progress for ${timeSinceProgress}s`);
      return;
    }

    // Check progress
    const data = await fetch(`/api/translate/progress/${progressId}`);
    
    if (data.completedBatches !== lastCompletedBatches) {
      // Progress made! Reset timer
      lastProgressTime = Date.now();
      console.log(`✅ Progress: ${data.completedBatches}/${data.totalBatches}`);
    }
    
    lastCompletedBatches = data.completedBatches;
  }, 1000);
};
```

**Main Fetch Request:**
- No timeout on the fetch request
- Polling handles stuck detection
- Can run indefinitely as long as progress is being made

---

## Console Output

### Normal Operation (Making Progress):
```
🔵 [PROGRESS] 39/65 batches complete
🔵 [PROGRESS] 40/65 batches complete
🔵 [PROGRESS] 41/65 batches complete
... (continues as long as batches complete)
```

### Waiting (No Progress Yet):
```
🔵 [WAITING] 41/65 batches complete (waiting...)
🔵 [WAITING] 41/65 batches complete (waiting...)
... (shows every 10 seconds)
```

### Stuck Detection:
```
🔴 [STUCK] No progress for 600s (total: 1500s)
Last completed: 41 batches
Translation appears stuck
```

---

## Benefits

### ✅ For Large Documents
- 1000-page book can take 2-3 hours → No problem!
- As long as batches keep completing, translation continues
- No artificial time limits

### ✅ Detects Real Problems
- API hanging → Detected after 10 minutes
- Backend crashed → Detected after 10 minutes
- Network issues → Detected after 10 minutes

### ✅ User Experience
- Clear progress updates
- Know exactly when stuck vs. just slow
- No premature timeouts

---

## Configuration

### Adjustable Parameters

**Stuck Timeout:**
```javascript
const STUCK_TIMEOUT = 10 * 60 * 1000; // 10 minutes
```

**Recommendations:**
- **Fast API**: 5 minutes (300000)
- **Normal API**: 10 minutes (600000) ← Current
- **Slow API**: 15 minutes (900000)

**Poll Interval:**
```javascript
setInterval(async () => { ... }, 1000); // Check every second
```

---

## Backend Changes

### Reduced Batch Sizes (Faster Processing)

**Token Targets:**
- **Simple**: 5,000 tokens (~20-30 paragraphs) - Was: 10,000
- **Moderate**: 3,000 tokens (~12-18 paragraphs) - Was: 5,000
- **Complex**: 2,000 tokens (~8-12 paragraphs) - Was: 3,000

**Why:**
- Smaller batches = faster individual API calls
- Less likely to hit API rate limits
- More frequent progress updates
- Better stuck detection

**Trade-off:**
- More total batches (100-400 instead of 50-300)
- Still well under 500 batch limit
- More granular progress tracking

---

## Example Scenarios

### Scenario 1: Normal Translation (1000-page book)
```
Total batches: 150
Time per batch: ~30 seconds
Total time: 75 minutes

Progress:
0:00 - Batch 1/150 complete
0:30 - Batch 2/150 complete
1:00 - Batch 3/150 complete
...
75:00 - Batch 150/150 complete
✅ Translation complete!
```
**Result:** ✅ Success (no timeout, took 75 minutes)

### Scenario 2: Slow API
```
Total batches: 150
Time per batch: ~2 minutes
Total time: 5 hours

Progress:
0:00 - Batch 1/150 complete
2:00 - Batch 2/150 complete
4:00 - Batch 3/150 complete
...
300:00 - Batch 150/150 complete
✅ Translation complete!
```
**Result:** ✅ Success (no timeout, took 5 hours)

### Scenario 3: API Hangs
```
Total batches: 150
Progress:
0:00 - Batch 1/150 complete
0:30 - Batch 2/150 complete
1:00 - Batch 3/150 complete
1:30 - Batch 4/150 complete
... (API hangs on batch 5)
11:30 - 🔴 STUCK DETECTED
```
**Result:** ❌ Timeout (stuck for 10 minutes after batch 4)

---

## Summary

### Old System:
- ❌ Fixed 25-minute timeout
- ❌ Failed on large documents
- ❌ Couldn't distinguish slow vs. stuck

### New System:
- ✅ No time limit (can run for hours)
- ✅ Detects stuck (10 min no progress)
- ✅ Resets timer on every batch completion
- ✅ Perfect for large documents
- ✅ Clear progress tracking

**Translation can now take as long as needed, as long as it's making progress!** 🚀

