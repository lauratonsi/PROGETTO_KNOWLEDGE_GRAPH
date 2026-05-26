#!/usr/bin/env python3
"""
Export RDF triples to JSONL format for LLM integration.
Single output: triples_for_llm.jsonl (one triple per line, compact format)
"""

import json
from rdflib import Graph

def shorten_uri(uri_str):
    """Convert URI to shortened form."""
    if not isinstance(uri_str, str):
        return str(uri_str)
    
    ns_map = {
        'cpv': 'https://w3id.org/italia/onto/CPV/',
        'clv': 'https://w3id.org/italia/onto/CLV/',
        'bologna': 'https://w3id.org/bologna/resource/',
    }
    
    for prefix, ns_uri in ns_map.items():
        if uri_str.startswith(ns_uri):
            return f"{prefix}:{uri_str[len(ns_uri):]}"
    
    return uri_str

def main():
    print("Loading TTL graph...")
    g = Graph()
    g.parse('bologna_KG_definitivo.ttl', format='turtle')
    
    print(f"Graph loaded: {len(g)} triples")
    print("Exporting to triples_for_llm.jsonl...")
    
    with open('triples_for_llm.jsonl', 'w', encoding='utf-8') as f:
        for subj, pred, obj in g:
            triple = {
                's': shorten_uri(str(subj)),
                'p': shorten_uri(str(pred)),
                'o': shorten_uri(str(obj)),
            }
            f.write(json.dumps(triple, ensure_ascii=False) + '\n')
    
    print(f"Done: triples_for_llm.jsonl created ({len(g)} lines)")

if __name__ == '__main__':
    main()
