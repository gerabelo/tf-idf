import requests     #
import time         # para o sleep()
import sys          # para exibir o erro

from pymongo import MongoClient, TEXT
from bs4 import BeautifulSoup

if __name__ == "__main__":
    ts = time.time()
    client = MongoClient("mongodb://localhost:27017")
    db_src = client['dicionario']
    collection_src = db_src['sinonimos']
    collection_dst = db_src['significados']

    collection_dst.create_index([('term',TEXT)],name='search_index', default_language='portuguese')

    URL = "https://www.significados.com.br/"

    HEADERS = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    termos = collection_src.find({})
    print("total de termos: ",termos.count())

    significados = [[],[]]

    for termo in termos:
        term = termo.get("term")
        try:
            r = requests.get(url = URL+term+"/", headers = HEADERS) 
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                conteudo = soup.findAll("div", {"id": "article"})
                print("conteudo: ",conteudo)
                i = len(significados[0])
                j = True
                while i > 0:
                    i -= 1
                    if significados[0] == term:
                        j = False
                        break
                if j:
                    try:
                        significados[0].append(term)
                        significados[1].append(conteudo)
                    except Exception as e:
                        print(e)
            elif r.status_code == 404:
                print("termo: ",term," ",r.status_code,": ",sys.exc_info()[0])
                try:
                    r = requests.get(url = URL+"/?s="+term, headers = HEADERS) 
                    soup = BeautifulSoup(r.text, 'html.parser')
                    conteudo = soup.find('div',{"class":"left-container"})
                    print("conteudo: ",conteudo)
                    i = len(significados[0])
                    j = True
                    while i > 0:
                        i -= 1
                        if significados[0] == term:
                            j = False
                            break
                    if j:
                        try:
                            significados[0].append(term)
                            significados[1].append(conteudo)
                            collection_dst.insert_one({"term":term,"significado":conteudo})
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
            else:
                print("termo: ",term," ",r.status_code,": ",sys.exc_info()[0])
        except Exception as e:
            print(e)
    i = len(significados[0])
    print("total de significados: ",i)
    print("coletados em ",time.time()-ts," segundos")
    # while i > 0:
    #     i -= 1
    #     try:
    #         collection_dst.insert_one({"term":significados[0][i],"significado":significados[1][i]})
    #     except Exception as e:
    #         print(e)

    print("finalizado em ",time.time()-ts," segundos")