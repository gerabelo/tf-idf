import time, math
from pymongo import MongoClient, TEXT
from bs4 import BeautifulSoup

ts = time.time()

client = MongoClient("mongodb://localhost:27017")
db_dic = client['dicionario']
db_fb = client['facebook']
polaridade = db_dic['polaridade']
polaridades = polaridade.find({})

sources = ['ACriticaCom','UOLNoticias','bncplay','classificadosam','classificadosmanaus','compraevendamanaus','g1','radiocbn']

for source in sources:
    posts = db_fb[source]
    dicionario = db_dic[source]

    publicacoes = posts.find({})
    numero_de_docs = publicacoes.count()
    termos = dicionario.find({})
    
    for termo in termos:
        ocorrencias = posts.find({"publicacao": {'$regex': termo.get('term'), '$options': 'i'}})
        # print(termo.get('term'))
        numero_de_ocorrencias = ocorrencias.count()
        # print(numero_de_ocorrencias)
        if numero_de_ocorrencias > 0:
                dicionario.find_and_modify(query={"term":termo.get('term')},update={
                        "$set" :{
                                "idf":math.log((numero_de_docs/numero_de_ocorrencias))
                                }
                },upsert=False, full_response= True)