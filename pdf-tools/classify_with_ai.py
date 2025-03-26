import openai
import pandas as pd
import time
import random
from tqdm import tqdm
from openai import OpenAIError

# Set your OpenAI API key
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

# File paths
INPUT_CSV = "./pdf-tools/bank_guarantee_paragraphs.csv"
OUTPUT_CSV = "./pdf-tools/bank_guarantee_paragraphs_classified.csv"

# OpenAI model settings
MODEL_NAME = "gpt-4-turbo"  
BATCH_SIZE = 10  # Adjust based on API rate limits
MAX_RETRIES = 3  # Retry failed requests up to 3 times

# Optimized Prompt Template
PROMPT_TEMPLATE = """
Classify the following Bank Guarantee clause as 'Onerous' or 'Neutral' and provide a concise explanation under 40 words.

Clause:
"{CLAUSE_TEXT}"

Respond in this format:
Classification: [Onerous/Neutral]
Explanation: [Concise justification]
"""

def classify_clause(clause):
    """ Sends a clause to OpenAI API with error handling and retries. """
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": "You are an expert in bank guarantees."},
                          {"role": "user", "content": PROMPT_TEMPLATE.replace("{CLAUSE_TEXT}", clause)}],
                max_tokens=50,
            )

            output_text = response["choices"][0]["message"]["content"]
            lines = output_text.split("\n")

            classification = lines[0].split(":")[-1].strip()
            explanation = lines[1].split(":")[-1].strip() if len(lines) > 1 else "No explanation provided."

            return classification, explanation

        except OpenAIError as e:
            print(f"API error on attempt {attempt + 1}: {e}")
            time.sleep(2 + random.uniform(0, 2))  # Wait before retrying

    return "Error", "API request failed after retries."

# Load CSV
df = pd.read_csv(INPUT_CSV)

# Ensure 'Paragraph' column exists
if "Paragraph" not in df.columns:
    raise ValueError("The input CSV must contain a column named 'Paragraph'.")

# Process clauses with OpenAI in batches
results = []
for i in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing Clauses"):
    batch = df.iloc[i:i + BATCH_SIZE]
    
    for _, row in batch.iterrows():
        clause = str(row["Paragraph"])
        classification, explanation = classify_clause(clause)
        results.append((clause, classification, explanation))
    
    time.sleep(1)  # Prevent rate limits

# Save results to CSV
output_df = pd.DataFrame(results, columns=["Paragraph", "Classification", "Explanation"])
output_df.to_csv(OUTPUT_CSV, index=False)

print(f"Classification completed! Results saved to {OUTPUT_CSV}")
