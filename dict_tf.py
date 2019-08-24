'''
Gera um dicionario de termos a partir da colecao facebook
'''

import time
from pymongo import MongoClient, TEXT
from bs4 import BeautifulSoup

ts = time.time()

client = MongoClient("mongodb://localhost:27017")
db_src = client['facebook']
db_dst = client['dicionario']
# collection_src = db_src['engenharia.da.computacao.ufam']
# collection_dst = db_dst['engenharia.da.computacao.ufam']
# collection_dst.create_index([('term',TEXT)],name='search_index', default_language='portuguese')

sources = ['ACriticaCom','UOLNoticias','bncplay','classificadosam','classificadosmanaus','compraevendamanaus','g1','radiocbn']

for source in sources:
    collection_src = db_src[source]
    collection_dst = db_dst[source]
    collection_dst.create_index([('term',TEXT)],name='search_index', default_language='portuguese')
    
    artigos = collection_src.find({})
    terms_counter = 0
    for artigo in artigos:
        soup = BeautifulSoup(artigo.get("publicacao"), 'html.parser')
        post_message = soup.find("div",{"data-testid":"post_message"})
        if post_message:
            paragraphs = post_message.find_all("p")
            quote = ''
            if paragraphs:
                for paragraph in paragraphs:
                    quote += paragraph.get_text().lower()+' '

            terms = quote.split()
            for term in terms:
                if collection_dst.find({"term":term}).count() > 0:
                    collection_dst.update_one({"term":term},{"$inc":{"tf":1}})
                else:
                    terms_counter += 1
                    collection_dst.insert_one({"term":term, "tf":1})

print("total de termos: ",terms_counter)
print("finalizado em ",time.time()-ts," segundos")