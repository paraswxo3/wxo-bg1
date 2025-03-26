import os
from elasticsearch import Elasticsearch
import requests

# Connect to Elasticsearch
api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")

es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)
print(es.info())

# es.ingest.delete_pipeline(id="elser_ingest_bg_clauses_train")
# es.ingest.put_pipeline(
#     id="elser_ingest_bg_clauses_train",
#     description="Ingest pipeline for ELSER bank guarantee training",
#     processors=[
#         {
#             "inference": {
#                 "model_id": ".elser_model_2_linux-x86_64",
#                 "input_output": [
#                     {"input_field": "clause", "output_field": "embedding"}
#                 ],
#             }
#         }
#     ],
# )

# es.ingest.delete_pipeline(id="elser_ingest_bg_clauses_live")
# es.ingest.put_pipeline(
#     id="elser_ingest_bg_clauses_live",
#     description="Ingest pipeline for ELSER bank guarantee live",
#     processors=[
#         {
#             "inference": {
#                 "model_id": ".elser_model_2_linux-x86_64",
#                 "input_output": [
#                     {"input_field": "clause", "output_field": "embedding"}
#                 ],
#             }
#         }
#     ],
# )
es.indices.delete(index="bank_guarantee_clauses_train", ignore_unavailable=True)
es.indices.create(
    index="bank_guarantee_clauses_train",
    settings={"index": {"default_pipeline": "elser_ingest_bg_clauses_train"}},
    mappings={
        "properties": {
            "clause": {"type": "text"},
            "embedding": {"type": "sparse_vector"},
            "classification": {"type": "text"},
            "clause_category": {"type": "text"},
            "category_meaning": {"type": "text"},
            "category_example": {"type": "text"},
            "feedback": {"type": "text"},
            "status": {"type": "text"},
        }
    }
)


es.indices.delete(index="bank_guarantee_clauses_live", ignore_unavailable=True)
es.indices.create(
    index="bank_guarantee_clauses_live",
    settings={"index": {"default_pipeline": "elser_ingest_bg_clauses_live"}},
    mappings={
        "properties": {
            "clause": {"type": "text"},
            "embedding": {"type": "sparse_vector"},
            "classification": {"type": "text"},
            "clause_category": {"type": "text"},
            "category_meaning": {"type": "text"},
            "category_example": {"type": "text"},
            "feedback": {"type": "text"},
            "status": {"type": "text"},
        }
    }
)
