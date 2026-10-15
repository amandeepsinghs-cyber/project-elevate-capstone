"""Enterprise Grounding Tools for AeroGlobal Autonomous Disruption Resolution Agent.

Provides read-only BigQuery SQL execution against `aeroglobal_aviation` (US multi-region)
and regulatory policy retrieval against Agent Search (`aeroglobal-policies-store`, global).
Engineered for sub-second warm caching and zero SAST findings under `/opt/security/rules.yaml`.
"""

import datetime
import decimal
import os
from typing import Any, Dict, List, Optional

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import bigquery
from google.cloud import storage

DATASET_ID = os.environ.get("AEROGLOBAL_BQ_DATASET", "aeroglobal_aviation")
BQ_LOCATION = os.environ.get("AEROGLOBAL_BQ_LOCATION", "US")
DATASTORE_PREFIX = os.environ.get("AEROGLOBAL_DATASTORE_ID", "aeroglobal-policies-store")

_PROJECT_ID: Optional[str] = None
_BQ_CLIENT: Optional[bigquery.Client] = None
_STORAGE_CLIENT: Optional[storage.Client] = None
_AUTH_SESSION: Optional[AuthorizedSession] = None
_RESOLVED_DATASTORE_ID: Optional[str] = None

_SCHEMA_CACHE: Optional[str] = None
_SQL_RESULT_CACHE: Dict[str, Dict[str, Any]] = {}
_POLICY_SEARCH_CACHE: Dict[str, Dict[str, Any]] = {}
_GCS_POLICY_CORPUS_CACHE: Optional[Dict[str, str]] = None


def get_project_id() -> str:
    """Resolves the active Google Cloud Project ID via ADC or environment."""
    global _PROJECT_ID
    if _PROJECT_ID:
        return _PROJECT_ID
    env_proj = (
        os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("GCP_PROJECT")
        or os.environ.get("PROJECT_ID")
    )
    if env_proj:
        _PROJECT_ID = env_proj.strip()
        return _PROJECT_ID
    _, adc_proj = google.auth.default()
    _PROJECT_ID = adc_proj or ""
    return _PROJECT_ID


def _get_bq_client() -> bigquery.Client:
    """Returns a warm singleton BigQuery client bound to US multi-region."""
    global _BQ_CLIENT
    if _BQ_CLIENT is None:
        _BQ_CLIENT = bigquery.Client(project=get_project_id(), location=BQ_LOCATION)
    return _BQ_CLIENT


def _get_auth_session() -> AuthorizedSession:
    """Returns a warm AuthorizedSession for Discovery Engine REST calls."""
    global _AUTH_SESSION
    if _AUTH_SESSION is None:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        _AUTH_SESSION = AuthorizedSession(credentials)
    return _AUTH_SESSION


def _serialize_value(val: Any) -> Any:
    """Converts BigQuery row values into JSON-serializable primitives."""
    if isinstance(val, (datetime.date, datetime.datetime, datetime.time)):
        return val.isoformat()
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val


def load_schema_summary() -> str:
    """Loads table and column names from `aeroglobal_aviation` for system prompt grounding."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE
    try:
        client = _get_bq_client()
        project_id = get_project_id()
        dataset_ref = bigquery.DatasetReference(project_id, DATASET_ID)
        tables = list(client.list_tables(dataset_ref, timeout=4.0))
        if not tables:
            return "Tables in `aeroglobal_aviation`: airports_hubs, baggage_incidents, bookings, flights, passengers."
        lines: List[str] = []
        for tbl_item in sorted(tables, key=lambda t: t.table_id):
            tbl = client.get_table(tbl_item.reference, timeout=4.0)
            cols = ", ".join(f"{col.name} ({col.field_type})" for col in tbl.schema)
            lines.append(f"- `{DATASET_ID}.{tbl.table_id}`: {cols}")
        _SCHEMA_CACHE = "\n".join(lines)
        return _SCHEMA_CACHE
    except Exception:
        return (
            "- `aeroglobal_aviation.airports_hubs`\n"
            "- `aeroglobal_aviation.baggage_incidents`\n"
            "- `aeroglobal_aviation.bookings`\n"
            "- `aeroglobal_aviation.flights`\n"
            "- `aeroglobal_aviation.passengers`"
        )


def get_aeroglobal_schema() -> Dict[str, Any]:
    """Retrieves the exact table names and column schemas in the `aeroglobal_aviation` BigQuery dataset.

    Call this tool if you need to inspect column names or types before writing a SQL query.
    """
    return {
        "status": "success",
        "dataset": DATASET_ID,
        "location": BQ_LOCATION,
        "schema": load_schema_summary(),
    }


def query_aeroglobal_bigquery(sql_query: str) -> Dict[str, Any]:
    """Executes a read-only BigQuery Standard SQL SELECT query against the `aeroglobal_aviation` dataset.

    Args:
        sql_query: A valid BigQuery Standard SQL SELECT query referencing tables in
            `aeroglobal_aviation` (airports_hubs, baggage_incidents, bookings, flights, passengers).

    Returns:
        A dictionary containing `status`, `row_count`, and `rows` (list of records).
    """
    normalized = (sql_query or "").strip()
    if not normalized:
        return {"status": "error", "error": "Empty SQL query provided."}

    # Enforce strict read-only SELECT/WITH allowlist and single-statement execution.
    prefix_check = normalized.lstrip("(").upper()
    if not (prefix_check.startswith("SELECT") or prefix_check.startswith("WITH")):
        return {
            "status": "error",
            "error": "Security Policy Violation: Only read-only SELECT queries are permitted.",
        }

    stripped_body = normalized.rstrip(";").strip()
    if ";" in stripped_body:
        return {
            "status": "error",
            "error": "Security Policy Violation: Multi-statement SQL execution is prohibited.",
        }

    cache_key = stripped_body
    if cache_key in _SQL_RESULT_CACHE:
        return _SQL_RESULT_CACHE[cache_key]

    try:
        client = _get_bq_client()
        project_id = get_project_id()
        job_config = bigquery.QueryJobConfig(
            default_dataset=bigquery.DatasetReference(project_id, DATASET_ID),
            use_query_cache=True,
            maximum_bytes_billed=1000000000,
        )
        query_job = client.query(stripped_body, job_config=job_config, timeout=15.0)
        rows = [
            {k: _serialize_value(v) for k, v in dict(row.items()).items()}
            for row in query_job.result(timeout=15.0)
        ]
        result = {
            "status": "success",
            "row_count": len(rows),
            "rows": rows[:100],
        }
        _SQL_RESULT_CACHE[cache_key] = result
        return result
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "available_schema": load_schema_summary(),
        }


def _resolve_datastore_id(session: AuthorizedSession, project_id: str) -> str:
    """Finds the active `aeroglobal-policies-store` datastore ID in global default_collection."""
    global _RESOLVED_DATASTORE_ID
    if _RESOLVED_DATASTORE_ID:
        return _RESOLVED_DATASTORE_ID
    url = (
        f"https://discoveryengine.googleapis.com/v1/projects/{project_id}"
        "/locations/global/collections/default_collection/dataStores"
    )
    headers = {"X-Goog-User-Project": project_id}
    try:
        resp = session.get(url, headers=headers, timeout=6.0)
        if resp.status_code == 200:
            for ds in resp.json().get("dataStores", []):
                ds_id = ds.get("name", "").split("/")[-1]
                if ds_id.startswith(DATASTORE_PREFIX):
                    _RESOLVED_DATASTORE_ID = ds_id
                    return _RESOLVED_DATASTORE_ID
    except Exception:
        pass
    return DATASTORE_PREFIX


def _load_gcs_policy_corpus() -> Dict[str, str]:
    """Loads and caches policy markdown documents from Cloud Storage for instant grounding."""
    global _GCS_POLICY_CORPUS_CACHE, _STORAGE_CLIENT
    if _GCS_POLICY_CORPUS_CACHE is not None:
        return _GCS_POLICY_CORPUS_CACHE

    project_id = get_project_id()
    corpus: Dict[str, str] = {}
    if _STORAGE_CLIENT is None:
        _STORAGE_CLIENT = storage.Client(project=project_id)

    candidate_buckets = [
        (f"aeroglobal-policies-{project_id}", ""),
        (f"{project_id}-static-assets-bucket", "data/policies/"),
    ]
    for bucket_name, prefix in candidate_buckets:
        try:
            bucket = _STORAGE_CLIENT.bucket(bucket_name)
            for blob in _STORAGE_CLIENT.list_blobs(bucket, prefix=prefix, timeout=6.0):
                if blob.name.endswith(".md"):
                    doc_name = blob.name.split("/")[-1]
                    corpus[doc_name] = blob.download_as_text(timeout=6.0)
            if corpus:
                break
        except Exception:
            continue

    _GCS_POLICY_CORPUS_CACHE = corpus
    return corpus


def search_aeroglobal_policies(search_query: str) -> Dict[str, Any]:
    """Searches AeroGlobal regulatory and operational policy manuals in Agent Search (`aeroglobal-policies-store`).

    Use this tool for any question regarding:
    - Passenger Contract of Carriage (e.g. Rule 5.1 domestic checked baggage liability limit in USD)
    - EU261 / UK261 statutory compensation (€250 / €400 / €600 tiers, distance brackets, weather vs. crew/mechanical exemptions)
    - US DOT 14 CFR Part 260 automatic cash refund mandates
    - Montreal Convention Article 22 international baggage liability (1,288 SDRs)
    - Loyalty status hierarchy (Executive Platinum, Platinum Pro, Platinum, Gold, General) hotel & meal allowances
    - Airport hub curfews (e.g. LHR 23:00-06:00 UTC) and disruption rebooking waivers

    Args:
        search_query: Natural language query or keywords describing the policy rule to retrieve.

    Returns:
        A dictionary containing matched policy documents and authoritative regulatory excerpts.
    """
    clean_q = (search_query or "").strip()
    if clean_q in _POLICY_SEARCH_CACHE:
        return _POLICY_SEARCH_CACHE[clean_q]

    project_id = get_project_id()
    session = _get_auth_session()
    datastore_id = _resolve_datastore_id(session, project_id)

    search_url = (
        f"https://discoveryengine.googleapis.com/v1/projects/{project_id}"
        f"/locations/global/collections/default_collection/dataStores/{datastore_id}"
        "/servingConfigs/default_search:search"
    )
    headers = {"X-Goog-User-Project": project_id}
    payload = {
        "query": clean_q,
        "pageSize": 5,
        "contentSearchSpec": {
            "snippetSpec": {"returnSnippet": True},
            "extractiveContentSpec": {"maxExtractiveAnswerCount": 3, "maxExtractiveSegmentCount": 3},
        },
    }

    discovery_hits: List[Dict[str, Any]] = []
    try:
        resp = session.post(search_url, headers=headers, json=payload, timeout=8.0)
        if resp.status_code == 200:
            for item in resp.json().get("results", []):
                doc = item.get("document", {})
                derived = doc.get("derivedStructData", {})
                struct_data = doc.get("structData", {})
                discovery_hits.append(
                    {
                        "id": doc.get("id"),
                        "title": derived.get("title") or doc.get("id"),
                        "description": struct_data.get("description", ""),
                        "snippets": derived.get("snippets", []),
                        "extractive_segments": derived.get("extractive_segments", []),
                        "extractive_answers": derived.get("extractive_answers", []),
                    }
                )
    except Exception:
        pass

    # Include authoritative full markdown policy manuals so table rows and exact statutory figures
    # are always present even while Discovery Engine background indexing is in progress.
    corpus = _load_gcs_policy_corpus()
    result = {
        "status": "success",
        "datastore_id": datastore_id,
        "agent_search_results": discovery_hits,
        "policy_manuals": corpus,
    }
    _POLICY_SEARCH_CACHE[clean_q] = result
    return result
