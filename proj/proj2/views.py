from django.shortcuts import render
from SPARQLWrapper import SPARQLWrapper, JSON
# Create your views here.
import json
import xmltodict
from BaseXClient import BaseXClient
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def main(request):
    return render(request, 'newmain.html')

def distritos(request):
    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
    prefix ns0: <https://municipio/pred/>
    prefix ns1: <https://distrito/pred/>
    SELECT ?municipio ?idmun ?nome ?regiao ?area ?pop  ?denspop
    WHERE {        
                   ?municipio ns0:idmun ?idmun .
                    ?municipio ns0:nome ?nome .
                   ?municipio ns0:regiao ?regiao .
                   ?municipio ns0:area ?area .
                   ?municipio ns0:pop ?pop .
                   ?municipio ns0:denspop ?denspop .

               }
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)
    area = 0
    pop = 0
    for e in res['results']['bindings']:
        # print(e)
        area = area + float((e['area']['value']))
        pop = pop + float((e['pop']['value']))
        # print(e['nome']['value'])
        # print(e['area']['value'])
        # print(e['pop']['value'])
    denspop = round(pop / area, 2)
    pop = round(pop, 2)
    area = round(area, 2)
    infoportugal = {}
    infoportugal['totalpop'] = pop
    infoportugal['totalarea'] = area
    infoportugal['densidadeportugal'] = denspop
    return render(request, 'distritos.html', {"infoportugal": infoportugal})

def distritoDetail(request):
    data = request.GET
    id = data['id']
    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """
    prefix ns0: <https://distrito/pred/>
    prefix ns1: <https://municipio/pred/>
    select ?distrito ?nome ?idmunicipio ?img ?nomedist ?area ?pop
    where { 
        ?distrito ns0:iddistrito '""" +id+ """'.
        ?distrito ns0:municipio ?nomemunicipio.
        ?nomemunicipio ns1:nome ?nome.
        ?nomemunicipio ns1:idmun ?idmunicipio.
        ?distrito ns0:imagem ?img.
    	?distrito ns0:nome ?nomedist.
    	?nomemunicipio ns1:area ?area.
        ?nomemunicipio ns1:pop ?pop.
       
    }
    order by asc(?nome)
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
    repo_name=repo_name)
    res = json.loads(res)
    municipios = {}
    interesses = {}
    area = 0
    pop = 0

    for e in res['results']['bindings']:
        municipios[e['idmunicipio']['value']] = e['nome']['value']
        area = area + float((e['area']['value']))
        pop = pop + float((e['pop']['value']))

    denspop = round(pop / area, 2)
    pop = round(pop, 2)
    area = round(area, 2)

    municipios['imagemdistrito'] = res['results']['bindings'][0]['img']['value']
    municipios['nomedistrito'] = res['results']['bindings'][0]['nomedist']['value']
    municipios['numpopulacao'] = pop
    municipios['areatotal'] = area
    municipios['densidadedistrito'] = denspop

    query = """
        prefix int: <https://interesse/pred/>
        prefix m: <https://municipio/pred/>
        prefix d: <https://distrito/pred/>
        select ?nome_int ?idint
        where {
           ?d d:iddistrito '"""+id+"""'.
           ?d d:municipio ?s_nome.
           ?s_nome m:interesse ?s_int.
           ?s_int int:nome ?nome_int.
           ?s_int int:idint ?idint
        }order by asc(?nome_int)
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:

        interesses[e['idint']['value']] = e['nome_int']['value']

    codes = {
        "1": 'Q485581',
        "2": 'Q213251',
        "3": 'Q83247',
        "4": 'Q768261',
        "5": 'Q12899232',
        "6": 'Q45412',
        "7": 'Q179948',
        "8": 'Q159457',
        "9": 'Q750594',
        "10": 'Q206933',
        "11": 'Q597',
        "12": 'Q622819',
        "13": 'Q36433',
        "14": 'Q273877',
        "15": 'Q173699',
        "16": 'Q208158',
        "17": 'Q503856',
        "18": 'Q117676',
    }
    sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
    sparql.setQuery("""
              SELECT DISTINCT ?coordinates ?imagemLabel ?timezoneLabel ?borderLabel
              WHERE {
                ?distrito wdt:P17 wd:Q45 .
                ?distrito wdt:P31 wd:Q41806065 .
                ?distrito wdt:P36 wd:"""+ codes.get(id) +""" .
                ?distrito wdt:P625 ?coordinates .
                OPTIONAL { ?distrito wdt:P2046 ?areaDistrito .}
                OPTIONAL { ?distrito wdt:P242 ?imagem .}
                OPTIONAL { ?distrito wdt:P421 ?timezone .}
                OPTIONAL { ?distrito wdt:P47 ?border .}
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en, pt". }
              }
          """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    borders = []
    for result in results['results']['bindings']:
        coord = result['coordinates']['value']
        img = result['imagemLabel']['value']
        tz = result['timezoneLabel']['value']
        borders.append(result['borderLabel']['value'])
    data = {}
    data['coord'] = coord
    data['img'] = img
    data['tz'] = tz
    data['borders'] = borders

    return render(request, 'distritoDetail.html', {"municipios":municipios,"interesses":interesses,"data":data})
