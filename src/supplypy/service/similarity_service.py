from supplypy.service.modeling import get_top_matches, find_competitive_alternatives, get_cluster_for_query

def get_top_matches_service(query):
    return get_top_matches(query, top_n=5)

def get_competitors_service(query):
    return find_competitive_alternatives(query, top_n=5)

def get_cluster_id_service(query):
    return get_cluster_for_query(query)