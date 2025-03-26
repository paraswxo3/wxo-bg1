import os
from elasticsearch import Elasticsearch


def analyze_clauses_elastic(clause):
    api_key = os.getenv("ES_API_KEY")
    es_url = os.getenv("ES_URL")

    es =  Elasticsearch(
        es_url,
        api_key=api_key,
        verify_certs=False
    )

    response = es.search(
        index="bank_guarantee_clauses_live",
        size=1,
        query={
            "text_expansion": {
                "embedding": {
                    "model_id": ".elser_model_2_linux-x86_64",
                    "model_text": clause
                }
            }
        }
    )
    if len(response["hits"]["hits"]) > 0:
        dict = response["hits"]["hits"][0]
        return {"classification":dict["_source"]["classification"],"explanation":dict["_source"]["explanation"]}
    else:
        return None
    


# clause = "Guarantee No Date Guarantee Cover from Amount in Rupees Rs WHEREAS a Company incorporated under the companies Act 1956 and having its Registered Office at in pursuance of Purchase Order No dated for the supply of AND WHEREAS it has been stipulated by you in the said contract that the supplier shall furnish you with a bank guarantee by a scheduled commercial recognized by you for the sum specified therein as security for compliance with its obligations in according with the contract AND WHEREAS we have agreed to give the supplier such a bank guarantee NOW THEREFORE we hereby the supplier up to a total"    
# print(analyze_clauses_elastic(clause))