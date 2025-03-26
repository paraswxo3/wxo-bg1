import base64
from fastapi import Body, Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import pandas as pd
from io import StringIO
from elser import upload_bg_clauses_train
from elser import upload_bg_clauses_live

app = FastAPI()

# Define the expected columns
EXPECTED_COLUMNS = {"Paragraph", "Clause Classification", "Explanation","Clause Type","Clause Meaning","Clause Example"}

# Define the request model
class CSVInput(BaseModel):
    file_content: str  # Expecting the CSV file content as plain text
class ResponseModel(BaseModel):
    response: str

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "Auth01234":
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key

@app.post("/upload-csv-train/", response_model=ResponseModel, dependencies=[Depends(verify_api_key)])
def upload_csv_train(csv_input: CSVInput = Body(..., embed=True)):
    try:
        # Read the CSV content from the text input
        csv_data = pd.read_csv(StringIO(csv_input.file_content))

        # Validate columns
        uploaded_columns = set(csv_data.columns)
        if not EXPECTED_COLUMNS.issubset(uploaded_columns):
            missing_columns = EXPECTED_COLUMNS - uploaded_columns
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Process the CSV data (Loop through the records)
        processed_data = []
        for index, row in csv_data.iterrows():
            # Extract relevant data
            record = {
                "clause": row["Paragraph"],
                "classification": row["Clause Classification"],
                "explanation": row["Explanation"],
                "clause_category": row["Clause Type"],
                "category_meaning": row["Clause Meaning"],
                "category_example": row["Clause Example"]
            }
            processed_data.append(record)
        print(len(processed_data))
        upload_bg_clauses_train(processed_data)
        upload_bg_clauses_live(processed_data)

        return {"response": "File processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    print("starting.....")
    uvicorn.run(app, host='0.0.0.0', port=8080)