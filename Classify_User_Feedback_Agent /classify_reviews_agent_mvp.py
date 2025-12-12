# classify_reviews_agent.py
import os
import json
import pandas as pd
import time
from typing import Dict, Any
import cohere

# ----------------------------
# Configuration
# ----------------------------
API_KEY = os.environ.get("COHERE_API_KEY")
if not API_KEY:
    raise RuntimeError("Set COHERE_API_KEY environment variable before running.")

MODEL = "command-a-03-2025"  # Cohere model
INPUT_CSV = "reviews.csv"    # CSV must have column "review"
OUTPUT_CSV = "classified_reviews.csv"
SLEEP_BETWEEN_CALLS = 0.2

# ----------------------------
# Initialize Cohere client
# ----------------------------
co = cohere.ClientV2(api_key=API_KEY)

# ----------------------------
# Local tool: classify_feedback
# ----------------------------
def classify_feedback_tool(text: str) -> Dict[str, Any]:
    """
    Classify an App Store review into categories for PMs.
    Categories: Praise, Bug/Crash, Subscription/Price, Feature Request, Usability, Other
    """
    t = text.lower()
    if any(w in t for w in ["crash", "crashes", "crashed", "bug", "error", "freezing"]):
        category = "Bug/Crash"
    elif any(w in t for w in ["too expensive", "expensive", "price", "subscription", "billing", "charged"]):
        category = "Subscription/Price"
    elif any(w in t for w in ["wish", "would be great", "should", "could you", "add ", "feature", "please add"]):
        category = "Feature Request"
    elif any(w in t for w in ["love", "great", "amazing", "helped", "enjoy"]):
        category = "Praise"
    elif any(w in t for w in ["hard to", "difficult", "confusing", "navigate", "usability", "ux", "ui"]):
        category = "Usability"
    else:
        category = "Other"
    return {"text": text, "category": category}

# ----------------------------
# Main processing function
# ----------------------------
def classify_reviews_from_csv(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    if "review" not in df.columns:
        raise RuntimeError("Input CSV must have a 'review' column")

    results = []
    total = len(df)
    for idx, row in df.iterrows():
        review_text = str(row["review"]).strip()
        print(f"[{idx+1}/{total}] Classifying review: {review_text[:80]}{'...' if len(review_text) > 80 else ''}")

        # 1) Local classification
        tool_output = classify_feedback_tool(review_text)

        # 2) Summarize with the model (no TOOLS)
        messages = [
            {
                "role": "user",
                "content": f"Review: {tool_output['text']}\nCategory: {tool_output['category']}\nSummarize in 1-2 sentences for a Product Manager."
            }
        ]
        response = co.chat(
            model=MODEL,
            messages=messages,
            max_tokens=200
        )

        try:
            assistant_summary = response.message.content[0].text
        except Exception:
            assistant_summary = str(response)

        # 3) Collect results
        results.append({
            "review": review_text,
            "category": tool_output.get("category"),
            "tool_output": json.dumps(tool_output),
            "assistant_summary": assistant_summary
        })

        time.sleep(SLEEP_BETWEEN_CALLS)

    # Save to CSV
    out_df = pd.DataFrame(results)
    out_df.to_csv(output_csv, index=False)
    print(f"Done! Classified {len(results)} reviews -> {output_csv}")

# ----------------------------
# Run script
# ----------------------------
if __name__ == "__main__":
    classify_reviews_from_csv(INPUT_CSV, OUTPUT_CSV)
