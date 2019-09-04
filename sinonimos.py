'''
Gera um dicionario de sininimos a partir dos termos constantes no dicionario
'''

import time, re
from pymongo import MongoClient, TEXT
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def getSinonimos(driver,term):
    try:
        resultado = []
        driver.get("https://www.sinonimos.com.br/"+term)

        
        # soup = BeautifulSoup(driver.find_element_by_id('content').get_attribute("innerHTML"), 'html.parser')
        # swrapper = soup.find("div",{"class":"s-wrapper"})
        sinonimos = driver.find_elements_by_xpath("//a[@class='sinonimo']")
        # sinonimos = soup.find_all('a', class_='sinonimo')
        # sinonimos = soup.findAll("a", {"class": "sinonimo"})
        for sinonimo in sinonimos:
            print("sinonimo.text: ",sinonimo.text)
            resultado.append(sinonimo.text)
        return resultado
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    ts = time.time()

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')    
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    client = MongoClient("mongodb://localhost:27017")

    db_src = client['dicionario']
    # db_dst = client['sinonimos']

    sources = ['ACriticaCom','UOLNoticias','bncplay','classificadosam','classificadosmanaus','compraevendamanaus','g1','radiocbn']

    collection_dst = db_src['sinonimos']
    collection_dst.create_index([('term',TEXT)],name='search_index', default_language='portuguese')
    
    sinonimos = [[],[]]

    for source in sources:
        collection_src = db_src[source]
        terms = collection_src.find({})
        # regx = re.compile("[À-ú]", re.IGNORECASE)
        # regx = re.compile("[’]|[‘]", re.IGNORECASE)
        # terms = collection_src.find({"term":regx}).limit(10)
    
        terms_counter = 0
        for term in terms:
            termo = term.get("term")
            # print(termo)
            termo = termo.replace("ç","c").replace("õ","o").replace("ó","o").replace("ô","o").replace("ã","a").replace("á","a").replace("â","a").replace("à","a").replace("é","e").replace("è","e").replace("ê","e").replace("í","i").replace("ú","u").replace("ü","u").replace("'","").replace("\"","").replace("#","").replace("?","").replace(";","").replace(":","").replace("(","").replace(")","").replace(",","").replace(".","").replace("*","").replace("%","").replace("‘","").replace("’","")
            print(termo)
            i = len(sinonimos[0]) #termos
            j = True
            while i > 0:
                i -= 1                
                if sinonimos[0][i] == termo:
                    j = False
                    break
            if j:
                sinonimos[0].append(termo)
                sinonimos[1].append(getSinonimos(driver,termo))
    driver.stop_client()
    driver.close()
    print("coletados em ",time.time()-ts," segundos")

    i = len(sinonimos[0]) #termos
    print("total de termos: ",i)
    while i > 0:
        i -= 1
        try:
            collection_dst.insert_one({"term":sinonimos[0][i],"sinonimos":sinonimos[1][i]})
        except Exception as e:
            print(e)
    print("finalizado em ",time.time()-ts," segundos")