import requests
import json

def upload_csv(file_path: str, api_url: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read the CSV file content
        csv_content = f.read()
        
    # Prepare the payload
    payload = {"csv_input": {"file_content": csv_content}}
    auth_token = "Auth01234"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": "Auth01234"
    }

    # Send the POST request to the FastAPI endpoint
    response = requests.post(api_url, headers=headers, json=payload,timeout=240)
    
    if response.status_code == 200:
        print("CSV file uploaded successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to upload. Status Code: {response.status_code}")
        print("Response:", response.json())

# Example usage
api_url = "http://localhost:8080/upload-csv-train/"  # Replace with your FastAPI URL
csv_file_path = "./pdf-tools/bank_guarantee_cleaned.csv"  # Replace with your CSV file path

upload_csv(csv_file_path, api_url)
