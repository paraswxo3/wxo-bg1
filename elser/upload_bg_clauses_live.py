import os
from elasticsearch import Elasticsearch,helpers
from fastapi import exceptions

# Connect to Elasticsearch
api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")

es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)
print(es.info())
# List of example clauses
documents = []

def upload_bg_clauses_live(content):
    print("uploading to ES")
    for index,row in enumerate(content,start=1):
        documents.append(
            {
                "_index": "bank_guarantee_clauses_live",
                "_source": {"clause": row["clause"],"classification":row["classification"],
                            "explanation": row["explanation"],"clause_category": row["clause_category"],
                            "category_meaning": row["category_meaning"],"category_example": row["category_example"]}
            }
        )
    helpers.bulk(es, documents)

def delete_index_content():
    try:
        # Delete all documents from the index using delete_by_query
        response = es.delete_by_query(
            index="bank_guarantee_clauses_live",
            body={
                "query": {
                    "match_all": {}
                }
            }
        )

        # Print the response
        print("Delete operation successful:")
        print(response)
    
    except exceptions.ConnectionError as e:
        print("Error: Could not connect to Elasticsearch. Please ensure it is running.")
        print(str(e))
    except exceptions.ElasticsearchException as e:
        print("Elasticsearch error occurred:")
        print(str(e))

# delete_index_content()
