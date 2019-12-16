from django.shortcuts import render

# Create your views here.
import json
from lxml import etree
import xmltodict
from BaseXClient import BaseXClient
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def main(request):
    return render(request, 'newmain.html')

def distritos(request):
    doc = etree.parse("portugal.xml")
    search = doc.xpath("//distrito")
    # create session
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    send = {}
    infoportugal = {}
    for s in search:
        send[s.find("nomedistrito").text] = s.find("iddistrito").text

    try:
        input = '''
            for $i in doc("portugal")
            let $dados := $i//municipio
            let $totalpop := sum($dados/populacao)
            let $totalarea := sum($dados/area)
            let $densidadeportugal := $totalpop div $totalarea
            return <portugal>{<totalpop>{xs:integer($totalpop)}</totalpop>, <totalarea>{$totalarea}</totalarea>, <densidadeportugal>{$densidadeportugal}</densidadeportugal>}</portugal>'''
        query = session.query(input)
        search = xmltodict.parse(query.execute())['portugal']
        query.close()
    finally:
        if session:
            infoportugal['totalpop'] = search['totalpop']
            infoportugal['totalarea'] = search['totalarea']
            infoportugal['densidadeportugal'] = search['densidadeportugal']
            session.close()
    return render(request, 'distritos.html', {"send": send, "infoportugal": infoportugal})

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