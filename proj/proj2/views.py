from django.shortcuts import render

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
    print(infoportugal)
    return render(request, 'distritos.html', {"infoportugal": infoportugal})

def distritoDetail(request):
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

def distritoDetail(request):
    #create session
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    data = request.GET
    id = data['id']
    try:
        #create query instance
        input = "import module namespace funcs = 'com.funcs.my.index';funcs:distrito({})".format(id)
        query = session.query(input)

        response = query.execute()

        query.close()

        input = "import module namespace funcs = 'com.funcs.my.index';funcs:interesseDist({})".format(id)
        query = session.query(input)
        response2 = query.execute()
        query.close()
    finally:
        if session:
            municipios = {}
            interesses = {}
            search = xmltodict.parse(response)['distrito']
            if not response2 == "<interesse/>":
                search1 = xmltodict.parse(response2)['interesse']['interesse']
            else:
                search1 = ''
            municipios['imagemdistrito'] = search['imagemdistrito']
            municipios['nomedistrito'] = search['nomedistrito']
            municipios['numpopulacao'] = search['numpopulacao']
            municipios['areatotal'] = round(float(search['areatotal']), 2)
            municipios['densidadedistrito'] = round(float(search['densidadedistrito']), 2)

            for s in search['municipios']['municipio']:
                municipios[s['idmunicipio']] = s['nomeconcelho']
            for m in search1:
                interesses[m['idinteresse']] = m['nome']
            session.close()

    return render(request, 'distritoDetail.html', {"municipios":municipios,"interesses":interesses})