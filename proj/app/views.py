from django.shortcuts import render

# Create your views here.
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def distrito(request):
    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)


    query = """
    prefix ns0: <https://distrito/pred/>
    prefix ns1: <https://distrito/pref/>
    select ?distrito ?nomemunicipio
    where{
        ?distrito ns1:municipio ?nomemunicipio.
        ?distrito ns0:nome 'Aveiro'.
    }
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
    repo_name=repo_name)
    res = json.loads(res)
    for e in res['results']['bindings']:
        print(e['nomemunicipio']['value'])

    return render(request, 'distritos.html', {})