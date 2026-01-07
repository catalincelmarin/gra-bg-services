# Module `kimera.store.ElasticStore`

Thin REST client for Elasticsearch with API-key authentication.

## `ElasticStore(uri=None, index=None, **kwargs)`
Splits the `uri` string on `"::"` to extract `base_url` and `api_key`, prepares default headers (`Authorization: ApiKey ...`, JSON content type), and stores the active index name.

### Index management
- `set_index(self, index)` / `get_index(self)` to mutate/read the active target index.

### Document operations
- `add(doc_id, document)` → `PUT /{index}/_doc/{doc_id}`
- `update(doc_id, document)` → `POST /{index}/_update/{doc_id}` with `{"doc": ...}` payload
- `remove(doc_id)` → `DELETE /{index}/_doc/{doc_id}`
- `find_one(index, doc_id)` → `GET /{index}/_doc/{doc_id}` (note: method ignores the `index` argument and uses `self.index`)
- `search(query)` → `POST /{index}/_search` with the provided query JSON. Logs the URL via `Helpers.sysPrint` for traceability.

All methods return the parsed JSON response from Elasticsearch.
