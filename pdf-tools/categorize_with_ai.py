import openai
import pandas as pd
import time
import random
from tqdm import tqdm
from openai import OpenAIError  # Importing OpenAI error handling

# Set your OpenAI API key
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

# File paths
INPUT_CSV = "./pdf-tools/bank_guarantee_paragraphs_classified.csv"  # Replace with your input file
OUTPUT_CSV = "./pdf-tools/bank_guarantee_paragraphs_categorized.csv"

# OpenAI Model
MODEL_NAME = "gpt-4-turbo"  # Use "gpt-3.5-turbo" if GPT-4 is unavailable
BATCH_SIZE = 10  # Adjust batch size based on rate limits
MAX_RETRIES = 3  # Retry failed requests up to 3 times

# Prompt Template for Clause Classification
PROMPT_TEMPLATE = """
Classify the following Bank Guarantee clause into one of the standard clause types such as Expiry, Demand, Claim Period, Governing Law, etc.
Provide:
1. The clause type
2. A brief meaning of the clause type
3. A standard example of that clause type

Clause:
"{CLAUSE_TEXT}"

Respond in this format:
Clause Type: [Type]
Clause Meaning: [Brief Explanation]
Clause Example: [Standard Example]
"""

def classify_clause(clause):
    """ Sends a clause to OpenAI API with error handling and retries. """
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert in bank guarantees and contract law."},
                    {"role": "user", "content": PROMPT_TEMPLATE.replace("{CLAUSE_TEXT}", clause)}
                ],
                max_tokens=150,
            )

            output_text = response["choices"][0]["message"]["content"]
            lines = output_text.split("\n")

            clause_type = lines[0].split(":")[-1].strip()
            clause_meaning = lines[1].split(":")[-1].strip()
            clause_example = lines[2].split(":")[-1].strip() if len(lines) > 2 else "No example provided."

            return clause_type, clause_meaning, clause_example

        except OpenAIError as e:
            print(f"API error on attempt {attempt + 1}: {e}")
            time.sleep(2 + random.uniform(0, 2))  # Wait before retrying

    return "Error", "API request failed after retries.", "No example available."

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
        clause_type, clause_meaning, clause_example = classify_clause(clause)
        results.append((clause, clause_type, clause_meaning, clause_example))
    
    time.sleep(1)  # Prevent rate limits

# Save results to CSV
output_df = pd.DataFrame(results, columns=["Paragraph", "Clause Type", "Clause Meaning", "Clause Example"])
output_df.to_csv(OUTPUT_CSV, index=False)

print(f"Classification completed! Results saved to {OUTPUT_CSV}")
