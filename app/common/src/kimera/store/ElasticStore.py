import requests
import json

from kimera.helpers.Helpers import Helpers


class ElasticStore:
    def __init__(self, uri=None, index=None, **kwargs):
        """
        Initialize the ElasticStore with the base URL and API key.

        :param base_url: The base URL of the Elasticsearch instance (e.g., http://localhost:9200)
        :param api_key: The API key for authentication
        """
        base_url = uri.split("::")[0]
        api_key = uri.split("::")[1]


        self.base_url = base_url
        self.index = index
        self.headers = {
            'Authorization': f'ApiKey {api_key.strip()}',
            'Content-Type': 'application/json'
        }

    def set_index(self,index):
        self.index = index
    
    def get_index(self):
        return self.index

    def add(self,doc_id, document):
        """
        Add a new document to the specified index.

        :param index: The Elasticsearch index to which the document will be added
        :param doc_id: The document ID
        :param document: The document to be added (as a dictionary)
        :return: The response from Elasticsearch
        """
        url = f"{self.base_url}/{self.index}/_doc/{doc_id}"
        response = requests.put(url, headers=self.headers, data=json.dumps(document))
        return response.json()

    def update(self, doc_id, document):
        """
        Update an existing document in the specified index.

        :param index: The Elasticsearch index where the document resides
        :param doc_id: The ID of the document to update
        :param document: The updated document (as a dictionary)
        :return: The response from Elasticsearch
        """
        url = f"{self.base_url}/{self.index}/_update/{doc_id}"
        body = {
            "doc": document
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(body))
        return response.json()

    def remove(self, doc_id):
        """
        Remove a document from the specified index.

        :param index: The Elasticsearch index from which to remove the document
        :param doc_id: The ID of the document to remove
        :return: The response from Elasticsearch
        """
        url = f"{self.base_url}/{self.index}/_doc/{doc_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()

    def find_one(self, index, doc_id):
        """
        Find a single document by its ID.

        :param index: The Elasticsearch index where the document resides
        :param doc_id: The ID of the document to find
        :return: The document data or None if not found
        """
        url = f"{self.base_url}/{self.index}/_doc/{doc_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def search(self, query):
        """
        Search for documents in the specified index based on the given query.

        :param index: The Elasticsearch index to search
        :param query: The Elasticsearch query (as a dictionary)
        :return: The search results from Elasticsearch
        """

        url = f"{self.base_url}/{self.index}/_search"
        Helpers.sysPrint("URL",url)
        response = requests.post(url, headers=self.headers, json=query)
        return response.json()