#!/usr/bin/env python3
import os
import time
import logging
from functools import lru_cache

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───── Configuration ──────────────────────────────────────────────────────────

SPARQL_ENDPOINT = 'https://ubergraph.apps.renci.org/sparql'
HPO_ROOT        = 'HP:0030057'
OUTPUT_DIR      = ''
CSV_PARENT      = 'parent_table.csv'
CSV_SIMPLE      = 'new_aab.csv'

ROOT_CODE = HPO_ROOT.split(':', 1)[1]
SPARQL_QUERY = f"""
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX HP:  <http://purl.obolibrary.org/obo/HP_>
PREFIX IAO: <http://purl.obolibrary.org/obo/IAO_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>

SELECT ?hpo_id ?label ?definition ?synonym ?dbxref WHERE {{
  ?hpo_id rdfs:subClassOf HP:{ROOT_CODE} .
  ?hpo_id rdfs:isDefinedBy obo:hp.owl .
  ?hpo_id rdfs:label ?label .
  OPTIONAL {{ ?hpo_id IAO:0000115     ?definition . }}
  OPTIONAL {{ ?hpo_id oboInOwl:hasExactSynonym ?synonym . }}
  OPTIONAL {{ ?hpo_id oboInOwl:hasDbXref     ?dbxref . }}
}}
"""

# ───── Logging & session with retries ──────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def create_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=['HEAD','GET','OPTIONS']
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    return s

session = create_session()

# ───── Helpers ────────────────────────────────────────────────────────────────

def submit_sparql(q: str) -> dict | None:
    try:
        r = session.get(
            SPARQL_ENDPOINT,
            params={'query': q},
            headers={'Accept': 'application/sparql-results+json'},
            timeout=20
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error("SPARQL query failed: %s", e)
        return None

def parse_sparql(res: dict) -> pd.DataFrame:
    if not res or 'results' not in res:
        return pd.DataFrame()
    rows = []
    for b in res['results']['bindings']:
        hid = b['hpo_id']['value'].rsplit('/', 1)[-1].replace('_', ':')
        rows.append({
            'hpo_id':     hid,
            'name':       b['label']['value'],
            'definition': b.get('definition', {}).get('value', ''),
            'synonyms':   b.get('synonym',    {}).get('value', ''),
            'ref':        b.get('dbxref',     {}).get('value', '')
        })
    df = pd.DataFrame(rows)
    agg = {
        'name':       'first',
        'definition': lambda x: '|'.join(sorted(set(filter(None, x)))),
        'synonyms':   lambda x: '|'.join(sorted(set(filter(None, x)))),
        'ref':        lambda x: '|'.join(sorted(set(filter(None, x))))
    }
    return df.groupby('hpo_id', as_index=False).agg(agg)

@lru_cache(None)
def get_associations(hid: str) -> tuple[list, list]:
    url = f'https://ontology.jax.org/api/network/annotation/{hid}'
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
        js = r.json()
        return js.get('diseases', []), js.get('genes', [])
    except Exception as e:
        logging.error("Associations fetch failed for %s: %s", hid, e)
        return [], []

@lru_cache(None)
def get_parent(hid: str) -> str | None:
    url = f'https://ontology.jax.org/api/hp/terms/{hid}/parents'
    try:
        r = session.get(url, timeout=5)
        r.raise_for_status()
        parents = r.json()
        return parents[0]['id'] if parents else None
    except Exception as e:
        logging.error("Parent fetch failed for %s: %s", hid, e)
        return None

def build_rels(hpo_ids: list[str]):
    all_dis, all_gen, all_par = [], [], []
    for hid in hpo_ids:
        ds, gs = get_associations(hid)
        all_dis.append([d['id'] for d in ds if 'id' in d])
        all_gen.append([f"{g['id']}:{g['name']}" for g in gs if 'id' in g and 'name' in g])
        all_par.append(get_parent(hid))
        time.sleep(0.2)
    return all_dis, all_gen, all_par

# ───── Main ───────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.info("Fetching SPARQL query…")
    res = submit_sparql(SPARQL_QUERY)
    df = parse_sparql(res)
    if df.empty:
        logging.error("No SPARQL results; aborting.")
        return

    ids = df['hpo_id'].tolist()
    logging.info("Fetching associations & parents for %d terms…", len(ids))
    dis, gen, par = build_rels(ids)

    df['related_diseases'] = ['|'.join(x) for x in dis]
    df['related_genes']    = ['|'.join(x) for x in gen]
    df['hpo_parent']       = par

    parent_csv = os.path.join(OUTPUT_DIR, CSV_PARENT)
    simple_csv = os.path.join(OUTPUT_DIR, CSV_SIMPLE)
    df.to_csv(parent_csv, index=False)
    df.drop(columns=['hpo_parent']).to_csv(simple_csv, index=False)
    logging.info("CSVs written to %s", OUTPUT_DIR)

if __name__ == "__main__":
    main()