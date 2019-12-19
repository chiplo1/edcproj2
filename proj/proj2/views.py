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
        area = area + float((e['area']['value']))
        pop = pop + float((e['pop']['value']))

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
    distrito = data['distrito']

    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    f = distrito.replace('_',' ')

    query = """
    prefix ns0: <https://distrito/pred/>
    prefix ns1: <https://municipio/pred/>
    select ?distrito ?nome ?idmunicipio ?img ?nomedist ?area ?pop
    where { 
        ?distrito ns0:nome '""" +f+ """'.
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
        nome2 = e['nome']['value'].replace(' ', '_')
        municipios[nome2] = e['nome']['value']
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
        select ?nome_int
        where {
           ?d d:nome '"""+distrito+"""'.
           ?d d:municipio ?s_nome.
           ?s_nome m:interesse ?s_int.
           ?s_int int:nome ?nome_int.
        }order by asc(?nome_int)
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)

    for e in res['results']['bindings']:
        nome2 = e['nome_int']['value'].replace(' ', '_')
        interesses[nome2] = e['nome_int']['value']

    codes = {
        "Aveiro": 'Q485581',
        "Beja": 'Q213251',
        "Braga": 'Q83247',
        "Braganca": 'Q768261',
        "Castelo_Branco": 'Q12899232',
        "Coimbra": 'Q45412',
        "Evora": 'Q179948',
        "Faro": 'Q159457',
        "Guarda": 'Q750594',
        "Leiria": 'Q206933',
        "Lisboa": 'Q597',
        "Portalegre": 'Q622819',
        "Porto": 'Q36433',
        "Santarem": 'Q273877',
        "Setubal": 'Q173699',
        "Viana_do_Castelo": 'Q208158',
        "Vila_Real": 'Q503856',
        "Viseu": 'Q117676',
    }
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    sparql.setQuery("""
              SELECT DISTINCT ?coordinates ?imagemLabel ?timezoneLabel ?borderLabel
              WHERE {
                ?distrito wdt:P17 wd:Q45 .
                ?distrito wdt:P31 wd:Q41806065 .
                ?distrito wdt:P36 wd:"""+ codes.get(distrito) +""" .
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
    coord = ""
    tz = ""
    img = ""
    for result in results['results']['bindings']:
        if 'coordinates' in result:
            coord = result['coordinates']['value']
        if 'imagemLabel' in result:
            if img == "":
                img = result['imagemLabel']['value']
        if 'timezoneLabel' in result:
            tz = result['timezoneLabel']['value']
        if 'borderLabel' in result:
            if result['borderLabel']['value'] not in borders:
                borders.append(result['borderLabel']['value'])
    data = {}
    data['coord'] = coord
    data['img'] = img
    data['tz'] = tz
    data['borders'] = borders
    return render(request, 'distritoDetail.html', {"municipios":municipios,"interesses":interesses,"data":data})

def interesseDetail(request):
    data = request.GET
    interesse = data['interesse']

    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    f = interesse.replace('_', ' ')
    query = """
        prefix int: <https://interesse/pred/>
        prefix m: <https://municipio/pred/>
        prefix d: <https://distrito/pred/>
        select ?tipo ?nomemunicipio ?nomedistrito
        where { 
           ?s_int int:nome '"""+ f +"""'.
           ?s_int int:tipo ?tipo.
           ?s_m m:interesse ?s_int.
           ?s_m m:nome ?nomemunicipio.
           ?distrito d:municipio ?s_m.
           ?distrito d:nome ?nomedistrito.
        }
        """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)

    send = {}

    send = {'nome':f,
            'tipo':res['results']['bindings'][0]['tipo']['value'],
            'nomeconcelho':res['results']['bindings'][0]['nomemunicipio']['value'],
            'nomedistrito':res['results']['bindings'][0]['nomedistrito']['value']}
    # -----------------------------------------------------------
    # ----------EDITAR INTERESSE---------
    intdelete = None
    newinteresse = None
    newtipo = None
    nomeconcelho = res['results']['bindings'][0]['nomemunicipio']['value'];
    if 'nomeinteresse' in request.POST and 'newtipo' in request.POST:
        intdelete = f
        newinteresse = request.POST.get('nomeinteresse')
        newtipo = request.POST.get('newtipo')
    if intdelete != None and newinteresse != None and newtipo != None:
        s_nomeinteresse = newinteresse.replace(' ', '_')
        updateedit = """prefix int: <https://interesse/pred/>
                    prefix p_int: <https://interesse/pred/>
                   prefix m: <https://municipio/pred/>
                   delete {?s ?p ?o}
                   where { 
                      ?s int:nome '""" + intdelete + """'.
                      ?s ?p ?o.
                   };
                  insert data {
                      int:""" + s_nomeinteresse + """ p_int:nome '""" + newinteresse + """';
                                     p_int:tipo '""" + newtipo + """'.
                  };
                   insert{
                       ?s m:interesse int:""" + s_nomeinteresse + """
                   }where{
                       ?s m:nome '""" + nomeconcelho + """'.
                   }"""
        playload_querydel = {"update": updateedit}
        resedit = accessor.sparql_update(body=playload_querydel, repo_name=repo_name)
        print(resedit)
        print(updateedit)
    # ------------------------------------------------------------

    return render(request, 'interesseDetail.html', {"send": send})

def municipioDetail(request):
    nomeinteresse = None
    tipo = None
    data = request.GET
    municipio = data['municipio']

    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    f = municipio.replace('_', ' ')

    # -----INSERIR INTERESSE----------
    if 'nomeinteresse' in request.POST and 'tipo' in request.POST:
        nomeinteresse = request.POST.get('nomeinteresse')
        tipo = request.POST.get('tipo')

    if nomeinteresse != None and tipo != None:
        s_nomeinteresse = nomeinteresse.replace(' ', '_')
        update = """
           prefix int: <https://interesse/>
           prefix p_int: <https://interesse/pred/>
           insert data {
               int:""" + s_nomeinteresse + """ p_int:nome '""" + nomeinteresse + """';
                              p_int:tipo '""" + tipo + """'.
           }"""
        playload_query2 = {"update": update}
        res = accessor.sparql_update(body=playload_query2, repo_name=repo_name)

        update2 = """
           prefix m: <https://municipio/pred/>
           prefix int: <https://interesse/>
           insert{
               ?s m:interesse int:""" + s_nomeinteresse + """
           }where{
               ?s m:nome '""" + f + """'.
           }"""
        #print(update)
        #print(update2)
        playload_query3 = {"update": update2}
        res = accessor.sparql_update(body=playload_query3, repo_name=repo_name)
    # ------------------------------------------------------------------------------
    # -----DELETE INTERESSE---------
    intdelete = None
    if 'nomeinteressedel' in request.POST != None:
        intdelete = request.POST.get('nomeinteressedel')
    if intdelete != None:
        updatedel = """prefix int: <https://interesse/pred/>
           delete {?s ?p ?o}
           where { 
              ?s int:nome '""" + intdelete + """'.
              ?s ?p ?o.
           }"""
        playload_querydel = {"update": updatedel}
        resdel = accessor.sparql_update(body=playload_querydel, repo_name=repo_name)
# -----------------------------------------------------------------------------------------
    #imprime toda a informaçao associado a um determinado municipio
    query = """
        prefix m: <https://municipio/pred/>
        prefix int: <https://interesse/pred/>
        select ?regiao ?area ?pop ?denspop 
        where{
            ?municipio m:nome '"""+ f +"""'.
            ?municipio m:regiao ?regiao.
            ?municipio m:area ?area.
            ?municipio m:pop ?pop.
            ?municipio m:denspop ?denspop.
        }
        """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)

    send = {}
    listanomes = {}
    send["nomeconcelho"] = f
    send["regiao"] = res['results']['bindings'][0]['regiao']['value']
    send["area"] = res['results']['bindings'][0]['area']['value']
    send["populacao"] = res['results']['bindings'][0]['pop']['value']
    send["densidadepopulacional"] = res['results']['bindings'][0]['denspop']['value']
#-----------------------------------------------------------------------------------------
    #resultado toda a informacao de interesses que um municipio tem
    query2 = """
            prefix m: <https://municipio/pred/>
            prefix int: <https://interesse/pred/>
            select ?nomeint ?tipo
            where{
                ?municipio m:nome '""" + f + """'.
                ?municipio m:interesse ?s_int.
                ?s_int int:nome ?nomeint.
                ?s_int int:tipo ?tipo
            }
            """
    payload_queryint = {"query": query2}
    res = accessor.sparql_select(body=payload_queryint,
                                 repo_name=repo_name)
    res = json.loads(res)
    tmp = res['results']['bindings']
    if tmp != []:
        if len(tmp)>1:
           for ints in tmp:
                listanomes[ints['nomeint']['value'].replace(' ', '_')] = {
                "nome": ints['nomeint']['value'],
                "tipo": ints['tipo']['value']}
        else:
            listanomes[res['results']['bindings'][0]['nomeint']['value'].replace(' ', '_')] = {
                "nome": res['results']['bindings'][0]['nomeint']['value'],
                "tipo": res['results']['bindings'][0]['tipo']['value']}

    #print(listanomes)
    return render(request, 'municipioDetail.html', {"send": send, "interesses": listanomes})

def interesses(request):

    endpoint = "http://localhost:7200"
    repo_name = "edcproj2"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """
        prefix int: <https://interesse/pred/>
        prefix m: <https://municipio/pred/>
        select ?nome ?tipo ?regiao
        where {
            ?s_int int:nome ?nome.
            ?s_int int:tipo ?tipo.
            ?s_m m:interesse ?s_int.
            ?s_m m:regiao ?regiao.
        }
        """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=repo_name)
    res = json.loads(res)

    send = {}
    cultura = {}
    lazer = {}
    gastronomia = {}
    patrimonio = {}

    for i in res['results']['bindings']:
        nomeint = i['nome']['value']
        tipoint = i['tipo']['value']
        regiaoint = i['regiao']['value']
        if tipoint=='Lazer':
            lazer[nomeint.replace(' ', '_')] = [nomeint, regiaoint]
        if tipoint=='Cultura':
            cultura[nomeint.replace(' ', '_')] = [nomeint, regiaoint]
        if tipoint=='Gastronomia e Vinho':
            gastronomia[nomeint.replace(' ', '_')] = [nomeint, regiaoint]
        if tipoint=='Patrimonio':
            patrimonio[nomeint.replace(' ', '_')] = [nomeint, regiaoint]

    send['cultura'] = cultura
    send['lazer'] = lazer
    send['gastronomia'] = gastronomia
    send['patrimonio'] = patrimonio
    return render(request, 'interesses.html', {"send": send})

def sobre(request):
    return render(request, 'sobre.html')