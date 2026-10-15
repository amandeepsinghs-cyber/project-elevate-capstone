#!/usr/bin/env python3
"""Task 1 Automation Script: Grounding Data & Metadata (Subtasks 1, 2, 3, 4).

Executes:
- Subtask 1 (AT ID: 1): Creates BigQuery dataset `aeroglobal_aviation` in `US` multi-region
  and loads all 5 CSV tables from `gs://${PROJECT_ID}-static-assets-bucket/data/structured/`.
- Subtask 3 (AT ID: 3): Populates table descriptions and column descriptions for ALL columns
  across all 5 tables in `aeroglobal_aviation`.
- Subtask 2 (AT ID: 2): Creates `gs://aeroglobal-policies-${PROJECT_ID}` in `us-central1`,
  copies all 5 policy `.md` files, and creates Agent Search datastore `aeroglobal-policies-store` in `global`.
- Subtask 4 (AT ID: 4): Registers `description` in the datastore schema and imports/replaces
  the 5 policy documents with rich `structData.description` metadata (using `reconciliationMode: FULL`
  so documents are replaced cleanly without deleting the datastore).
"""

import hashlib
import json
import os
import sys
import time
from typing import Dict

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import bigquery
from google.cloud import storage

DATASET_ID = "aeroglobal_aviation"
BQ_LOCATION = "US"
TABLES = [
    "airports_hubs",
    "baggage_incidents",
    "bookings",
    "flights",
    "passengers",
]

TABLE_DESCRIPTIONS: Dict[str, str] = {
    "airports_hubs": (
        "AeroGlobal Airways global gateway airport hubs directory, including IATA airport codes, "
        "hub classifications, operational curfew windows (such as LHR 23:00-06:00 UTC), "
        "de-icing capacity, catering limits, and contracted hotel room inventory."
    ),
    "baggage_incidents": (
        "Passenger checked baggage irregularity and mishandling incident records, tracking delayed, "
        "damaged, or misrouted luggage, PIR reference numbers, last scanned locations, weight, "
        "and statutory liability claims under Montreal Convention Article 22 (1,288 SDRs) and US DOT Rule 5.1 ($3,800)."
    ),
    "bookings": (
        "Passenger flight reservations (PNRs) linking passengers (`passenger_id`) to flights (`flight_number`), "
        "origin/destination pairs, fare classes, booking statuses, ticket amounts in USD, and rebooking state."
    ),
    "flights": (
        "AeroGlobal real-time flight operations telemetry, capturing flight numbers (`AG-...`), origin and "
        "destination hubs, scheduled/actual departure and arrival timestamps, delay durations, root-cause delay "
        "codes (weather vs. crew duty-time expiration under FAA Part 117 or mechanical faults), aircraft tail numbers, "
        "and route distances in kilometers for EU261 statutory tier calculation."
    ),
    "passengers": (
        "AeroGlobal passenger master profile and loyalty directory, storing `passenger_id` (`PAX-...`), "
        "full name, 5-tier frequent flyer status (Executive Platinum, Platinum Pro, Platinum, Gold, General Member), "
        "lifetime mileage balance, and B2B corporate contract codes (`CORP-...`)."
    ),
}

COLUMN_DESCRIPTIONS: Dict[str, str] = {
    # airports_hubs
    "airport_code": "Three-letter IATA airport hub code (e.g., JFK, LHR, ORD, DEN, CDG, FRA, HND, SIN, SYD).",
    "iata_code": "Three-letter IATA airport identifier code.",
    "airport_name": "Official name of the commercial airport hub.",
    "city": "Metropolitan city where the airport hub is located.",
    "country": "Country or sovereign jurisdiction of the airport hub.",
    "region": "Geographic operating region of the airport hub.",
    "timezone": "IANA local timezone identifier for airport operations.",
    "is_hub": "Boolean or category flag indicating whether the airport is an AeroGlobal primary or secondary hub.",
    "hub_type": "Classification of hub tier (Primary Gateway, Secondary Hub, Regional Spoke).",
    "curfew_start_utc": "Start time in UTC for mandatory night flight curfew restrictions (e.g., 23:00 at LHR).",
    "curfew_end_utc": "End time in UTC for mandatory night flight curfew restrictions (e.g., 06:00 at LHR).",
    "curfew_hours": "Operational night flight ban or curfew window in UTC.",
    "hotel_inventory_available": "Count of contracted partner hotel rooms available near the airport hub for disrupted passengers.",
    "contracted_hotel_rooms": "Number of contracted distressed-passenger hotel rooms available at the hub.",
    "catering_capacity": "Maximum meal voucher and catering kitchen capacity at the airport hub.",
    "deicing_bays": "Number of active aircraft de-icing pads/bays at the airport.",
    # passengers
    "passenger_id": "Unique AeroGlobal passenger identifier (e.g., PAX-70418, PAX-74972).",
    "first_name": "Passenger legal given/first name.",
    "last_name": "Passenger legal surname/family name.",
    "full_name": "Passenger full legal name as printed on travel documents.",
    "email": "Passenger contact email address for disruption notifications.",
    "phone": "Passenger mobile phone number for SMS disruption alerts.",
    "loyalty_tier": "AeroGlobal 5-tier frequent flyer status (Executive Platinum, Platinum Pro, Platinum, Gold, General Member).",
    "loyalty_status": "AeroGlobal frequent flyer tier governing rebooking priority, hotel cap, and meal stipends.",
    "lifetime_miles": "Cumulative lifetime frequent flyer mileage balance accrued by the passenger.",
    "lifetime_mileage_balance": "Total lifetime mileage balance accrued on AeroGlobal Airways.",
    "miles_balance": "Current redeemable and lifetime mileage balance for the passenger.",
    "corporate_contract_code": "Enterprise B2B corporate travel contract identifier (e.g., CORP-GOOGLE-901, CORP-AMAZON-606).",
    "corporate_code": "B2B corporate account contract code associated with the passenger profile.",
    "home_airport": "Passenger primary home gateway IATA airport code.",
    "special_assistance": "SSR/special service request code or mobility/dietary accommodation requirement.",
    # flights
    "flight_number": "AeroGlobal flight designator code (e.g., AG-814, AG-771).",
    "flight_id": "Unique operational flight leg identifier.",
    "origin": "Three-letter IATA code of the departure origin airport.",
    "destination": "Three-letter IATA code of the arrival destination airport.",
    "scheduled_departure": "Scheduled gate departure timestamp in UTC.",
    "actual_departure": "Actual or estimated gate departure timestamp in UTC.",
    "scheduled_arrival": "Scheduled gate arrival timestamp in UTC.",
    "actual_arrival": "Actual or estimated gate arrival timestamp in UTC.",
    "status": "Current operational flight status (Delayed, Cancelled, On_Time, Diverted, Ground_Stop).",
    "flight_status": "Current operational status of the flight leg.",
    "delay_minutes": "Total arrival or departure delay duration in minutes.",
    "delay_hours": "Total delay duration in hours used for EU261 and US DOT Part 260 threshold evaluation.",
    "delay_reason": "Primary operational cause of flight delay or cancellation (e.g., Weather / Winter Storm Orion, Crew Duty-Time Limit under FAA Part 117, Mechanical Fault).",
    "cancellation_reason": "Root cause classification for flight cancellation or extended disruption.",
    "distance_km": "Great-circle flight route distance in kilometers used to determine EU261 compensation tier (<=1500km, 1500-3500km, >3500km).",
    "route_distance_km": "Route distance in kilometers between origin and destination hubs.",
    "aircraft_tail": "Aircraft registration tail number assigned to the flight.",
    "aircraft_type": "Equipment model type (e.g., B777-300ER, B787-9, A350-900, B737-MAX8).",
    # bookings
    "pnr": "Six-to-nine character Passenger Name Record (PNR) booking reference code (e.g., PNR501792).",
    "booking_id": "Unique reservation booking identifier.",
    "fare_class": "Booked cabin fare class code (F, J, W, Y).",
    "fare_class_name": "Cabin service class name (First, Business, Premium Economy, Economy).",
    "booking_status": "Current reservation state (Confirmed, Disrupted, Cancelled, Voluntarily_Rebooked_Next_Flight).",
    "ticket_amount_usd": "Total paid ticket fare amount in USD eligible for refund calculation under US DOT 14 CFR Part 260.",
    "seat_number": "Assigned cabin seat number on the aircraft.",
    "checked_bags_count": "Number of checked luggage pieces associated with the PNR.",
    # baggage_incidents
    "incident_id": "Unique baggage irregularity incident identifier.",
    "bag_tag": "Ten-digit IATA license plate baggage tag number.",
    "pir_number": "Property Irregularity Report (PIR) reference code for delayed or damaged baggage.",
    "incident_type": "Type of baggage mishandling (Delayed, Damaged, Pilfered, Lost, Misrouted).",
    "baggage_status": "Current baggage tracing status and resolution workflow state.",
    "last_scanned_hub": "IATA airport code where the baggage tag was most recently scanned.",
    "last_scan_location": "Most recent physical scan point for the mishandled bag.",
    "claim_amount_usd": "Claimed or estimated reimbursement amount in USD for baggage delay/loss.",
    "itinerary_type": "Domestic vs. International itinerary classification governing Rule 5.1 ($3,800 USD) vs. Montreal Convention (1,288 SDRs).",
}


def get_policy_description(filename: str, text_content: str) -> str:
    """Generates a comprehensive regulatory scope description for Subtask 4 (`structData.description`)."""
    lower_name = filename.lower()
    if "contract" in lower_name or "carriage" in lower_name or "baggage" in lower_name:
        return (
            f"AeroGlobal regulatory policy manual ({filename}): Covers Passenger Contract of Carriage rules, "
            "Rule 5.1 domestic checked baggage maximum liability limit ($3,800 USD), Montreal Convention of 1999 "
            "Article 22 international baggage delay and loss liability limits (1,288 SDRs, approx. $1,728 USD), "
            "21-day interim emergency purchase reimbursement, US DOT 14 CFR Part 260 mandatory 100% cash refunds, "
            "and EU261 statutory passenger rights."
        )
    if "eu261" in lower_name or "uk261" in lower_name or "comp" in lower_name or "reg" in lower_name:
        return (
            f"AeroGlobal statutory passenger protection policy ({filename}): Covers EU261 / UK261 statutory cash "
            "compensation tiers (€250 <=1,500km, €400 1,500-3,500km, €600 >3,500km), extraordinary weather exemptions "
            "vs. non-exempt mechanical defects (CJEU Case C-549/07 Wallentin-Hermann) and FAA Part 117 crew duty-time "
            "expirations, mandatory Duty of Care (hotel and meal vouchers), and US DOT 14 CFR Part 260 cash refunds."
        )
    if "loyalty" in lower_name or "tier" in lower_name or "vip" in lower_name or "allow" in lower_name:
        return (
            f"AeroGlobal 5-tier loyalty hierarchy and disruption allowance manual ({filename}): Defines rebooking "
            "priority, hotel voucher caps, lounge access, and daily meal stipends ($75/day) across Executive Platinum, "
            "Platinum Pro, Platinum, Gold ($200 hotel cap), and General Member tiers, alongside EU261 and US DOT rules."
        )
    if "weather" in lower_name or "waiver" in lower_name or "hub" in lower_name or "curfew" in lower_name:
        return (
            f"AeroGlobal operational disruption and weather waiver policy ({filename}): Covers Winter Storm Orion "
            "rebooking waivers, airport hub curfew boundaries (including LHR 23:00-06:00 UTC night flight ban), "
            "FAA 14 CFR Part 117 crew duty-time rules, EU261 statutory passenger rights, US DOT 14 CFR Part 260 "
            "cash refunds, and Montreal Convention baggage liability limits."
        )
    first_lines = " ".join(
        line.strip("#* ").strip()
        for line in text_content.splitlines()
        if line.strip()
    )[:220]
    return (
        f"AeroGlobal regulatory policy document ({filename}) covering EU261 statutory passenger rights, "
        f"US DOT 14 CFR Part 260 cash refunds, Montreal Convention and Rule 5.1 baggage liability limits, "
        f"loyalty tier allowances, and weather waivers. Scope: {first_lines}"
    )


def step1_and_3_bigquery(project_id: str) -> None:
    print(f"\n=== [Subtask 1 & 3] BigQuery Dataset `{DATASET_ID}` (US) + Table/Column Metadata ===")
    bq_client = bigquery.Client(project=project_id, location=BQ_LOCATION)
    dataset_ref = bigquery.Dataset(f"{project_id}.{DATASET_ID}")
    dataset_ref.location = BQ_LOCATION
    dataset_ref.description = (
        "AeroGlobal Airways operational telemetry dataset containing airport hubs, "
        "passengers, flights, bookings, and baggage incidents for autonomous disruption resolution."
    )
    bq_client.create_dataset(dataset_ref, exists_ok=True)
    print(f"[OK] Dataset `{project_id}.{DATASET_ID}` ready in location `{BQ_LOCATION}`.")

    src_bucket = f"gs://{project_id}-static-assets-bucket/data/structured"
    for table_name in TABLES:
        uri = f"{src_bucket}/{table_name}.csv"
        table_id = f"{project_id}.{DATASET_ID}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            allow_quoted_newlines=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        print(f"Loading {uri} -> {table_id} ...")
        load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()

        # Subtask 3: Populate table description and ALL column descriptions
        table_obj = bq_client.get_table(table_id)
        table_obj.description = TABLE_DESCRIPTIONS.get(
            table_name,
            f"AeroGlobal operational `{table_name}` table for flight disruption resolution.",
        )
        updated_schema = []
        for field in table_obj.schema:
            col_desc = COLUMN_DESCRIPTIONS.get(
                field.name.lower(),
                f"Operational `{field.name}` ({field.field_type}) attribute in AeroGlobal `{table_name}` table.",
            )
            updated_schema.append(
                bigquery.SchemaField(
                    name=field.name,
                    field_type=field.field_type,
                    mode=field.mode,
                    description=col_desc,
                    fields=field.fields,
                )
            )
        table_obj.schema = updated_schema
        bq_client.update_table(table_obj, ["description", "schema"])
        print(
            f"[OK] `{table_name}`: {table_obj.num_rows} rows loaded; "
            f"table description + {len(updated_schema)} column descriptions updated."
        )


def step2_and_4_agent_search(project_id: str) -> None:
    print("\n=== [Subtask 2 & 4] Policy GCS Bucket + Agent Search Datastore + Metadata ===")
    storage_client = storage.Client(project=project_id)
    src_bucket_name = f"{project_id}-static-assets-bucket"
    dest_bucket_name = f"aeroglobal-policies-{project_id}"

    dest_bucket = storage_client.bucket(dest_bucket_name)
    if not dest_bucket.exists():
        dest_bucket = storage_client.create_bucket(dest_bucket_name, location="us-central1")
        print(f"[OK] Created bucket gs://{dest_bucket_name} in us-central1.")
    else:
        print(f"[OK] Bucket gs://{dest_bucket_name} already exists.")

    src_bucket = storage_client.bucket(src_bucket_name)
    policy_blobs = [
        b for b in storage_client.list_blobs(src_bucket, prefix="data/policies/")
        if b.name.endswith(".md")
    ]
    if not policy_blobs:
        raise RuntimeError(f"No .md policy files found in gs://{src_bucket_name}/data/policies/")

    policy_texts: Dict[str, str] = {}
    for blob in policy_blobs:
        fname = blob.name.split("/")[-1]
        src_bucket.copy_blob(blob, dest_bucket, new_name=fname)
        policy_texts[fname] = blob.download_as_text()
        print(f"[OK] Copied {fname} -> gs://{dest_bucket_name}/{fname}")

    # Create or locate `aeroglobal-policies-store` datastore in global default_collection
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)
    headers = {
        "X-Goog-User-Project": project_id,
        "Content-Type": "application/json",
    }
    base_url = (
        f"https://discoveryengine.googleapis.com/v1/projects/{project_id}"
        "/locations/global/collections/default_collection"
    )

    datastore_id = "aeroglobal-policies-store"
    list_resp = session.get(f"{base_url}/dataStores", headers=headers)
    existing_ds = None
    if list_resp.status_code == 200:
        for ds in list_resp.json().get("dataStores", []):
            ds_name_last = ds.get("name", "").split("/")[-1]
            if ds_name_last.startswith("aeroglobal-policies-store"):
                existing_ds = ds
                datastore_id = ds_name_last
                break

    if existing_ds:
        print(f"[OK] Found existing datastore: {datastore_id}")
    else:
        create_url = f"{base_url}/dataStores?dataStoreId={datastore_id}"
        payload = {
            "displayName": "aeroglobal-policies-store",
            "industryVertical": "GENERIC",
            "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
            "contentConfig": "CONTENT_REQUIRED",
        }
        c_resp = session.post(create_url, headers=headers, json=payload)
        if c_resp.status_code not in (200, 201, 409):
            raise RuntimeError(f"Failed to create datastore: {c_resp.status_code} {c_resp.text}")
        print(f"[OK] Created datastore `{datastore_id}` in global.")
        time.sleep(5)

    # Subtask 4: Register `description` in the datastore schema (`default_schema`)
    schema_url = f"{base_url}/dataStores/{datastore_id}/schemas/default_schema"
    schema_payload = {
        "structSchema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "indexable": True,
                    "dynamicFacetable": True,
                    "searchable": True,
                    "retrievable": True,
                },
                "title": {
                    "type": "string",
                    "searchable": True,
                    "retrievable": True,
                },
            },
        }
    }
    s_resp = session.patch(schema_url, headers=headers, json=schema_payload)
    print(f"[OK] Datastore schema update status: {s_resp.status_code}")

    # Inspect any existing documents so we reuse their IDs if already imported
    docs_url = f"{base_url}/dataStores/{datastore_id}/branches/default_branch/documents"
    existing_docs_resp = session.get(docs_url, headers=headers)
    uri_to_doc_id: Dict[str, str] = {}
    if existing_docs_resp.status_code == 200:
        for d in existing_docs_resp.json().get("documents", []):
            doc_uri = d.get("content", {}).get("uri", "")
            if doc_uri:
                uri_to_doc_id[doc_uri] = d.get("id", "")

    # Build JSONL manifest with `structData.description` and `content.uri`
    jsonl_lines = []
    for fname, content_text in sorted(policy_texts.items()):
        doc_uri = f"gs://{dest_bucket_name}/{fname}"
        # Discovery Engine default ID for GCS content imports is either sha256[:32] or stem
        stem_id = fname.replace(".md", "").replace(".", "_")
        doc_id = uri_to_doc_id.get(doc_uri) or hashlib.sha256(doc_uri.encode()).hexdigest()[:32] or stem_id
        desc = get_policy_description(fname, content_text)
        record = {
            "id": doc_id,
            "structData": {
                "description": desc,
                "title": fname,
            },
            "content": {
                "mimeType": "text/plain",
                "uri": doc_uri,
            },
        }
        jsonl_lines.append(json.dumps(record))

    # Upload JSONL manifest to static-assets-bucket so `gs://aeroglobal-policies-${PROJECT_ID}`
    # stays clean with only the 5 .md files, and trigger FULL reconciliation import!
    manifest_blob = src_bucket.blob("data/policies_metadata/metadata.jsonl")
    manifest_blob.upload_from_string("\n".join(jsonl_lines), content_type="application/json")
    manifest_uri = f"gs://{src_bucket_name}/data/policies_metadata/metadata.jsonl"
    print(f"[OK] Uploaded metadata JSONL manifest to {manifest_uri}")

    import_url = f"{docs_url}:import"
    import_payload = {
        "gcsSource": {
            "inputUris": [manifest_uri],
            "dataSchema": "document",
        },
        "reconciliationMode": "FULL",
    }
    imp_resp = session.post(import_url, headers=headers, json=import_payload)
    if imp_resp.status_code != 200:
        raise RuntimeError(f"Document import failed: {imp_resp.status_code} {imp_resp.text}")
    op_name = imp_resp.json().get("name", "")
    print(f"[OK] Triggered Discovery Engine FULL metadata+document import operation: {op_name}")

    # Poll operation for up to 90 seconds so documents are visible immediately for Subtask 4 sanity check
    if op_name:
        op_url = f"https://discoveryengine.googleapis.com/v1/{op_name}"
        for i in range(18):
            time.sleep(5)
            op_r = session.get(op_url, headers=headers)
            if op_r.status_code == 200 and op_r.json().get("done"):
                print("[OK] Document import operation completed!")
                break
            print(f"  Waiting for document import registration ({ (i + 1) * 5 }s)...")

    # Verify documents and descriptions
    verify_resp = session.get(docs_url, headers=headers)
    if verify_resp.status_code == 200:
        docs = verify_resp.json().get("documents", [])
        print(f"[OK] Verified {len(docs)} documents in `{datastore_id}`:")
        for d in docs:
            print(f"  - id={d.get('id')} | description={d.get('structData', {}).get('description', '')[:80]}...")


def main() -> None:
    _, project_id = google.auth.default()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or project_id
    if not project_id:
        print("ERROR: Could not determine PROJECT_ID. Run `export PROJECT_ID=$(gcloud config get-value project)`")
        sys.exit(1)
    print(f"Running Task 1 Grounding & Metadata Automation for project: {project_id}")
    step1_and_3_bigquery(project_id)
    step2_and_4_agent_search(project_id)
    print("\n==================================================================")
    print("SUCCESS! Subtasks 1, 2, 3, and 4 are complete.")
    print("Go to the Qwiklabs page and click 'Check my progress' for Subtasks 1, 2, 3, and 4!")
    print("==================================================================")


if __name__ == "__main__":
    main()
