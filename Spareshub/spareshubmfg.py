# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:06:19 2018

@author: prachi
"""

import requests
import time as t
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import html

endpoint = "https://spareshub.com/manufacturers.html"
response = requests.get(endpoint)
if response.status_code != 200:
        print('Failed to retrieve articles with error {}'.format(response.status_code))
        exit()


soup = BeautifulSoup(response.content, "html.parser")
mfg_store = soup.find('div', attrs={'class': 'col-left-first'})
mfg_urls = mfg_store.find_all('a')

mfgurllist = []
for u in mfg_urls:
    mfgurllist.append(u.get('href'))

mfgurllist = [x for x in mfgurllist if x.endswith('.html')]

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--start-maximized")
options.add_argument("--test-type")
options.add_argument("--headless")

mfg_to_product_dict={}
#v=mfgurllist[0]
for v in mfgurllist:
    driver = webdriver.Chrome(executable_path='C:/Users/prachi/Downloads/chromedriver_win32/chromedriver.exe',chrome_options=options)
    t.sleep(3)
    #driver = webdriver.Firefox(executable_path='C:/Users/imart/Downloads/geckodriver-v0.21.0-win64/geckodriver.exe')
    driver.get(v)
    
    # Selenium script to scroll to the bottom, wait 3 seconds for the next batch of data to load, then continue scrolling.  It will continue to do this until the page stops loading new data.
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
            lastCount = lenOfPage
            t.sleep(3)
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount==lenOfPage:
                match=True
    source_data = driver.page_source
    
    soup2 = BeautifulSoup(source_data, "html.parser")
    product_store = soup2.select("a")
    
    x=[]
    products=[]
    products2=[]
    for f in product_store:
        x.append(f.get('href'))
    
    products = [y for y in x if type(y)==str]
    s= v[:-5]+'/'
    mfg_products = [z for z in products if (z.startswith(s) and z.endswith('.html'))]
    mfg_products = list(set(mfg_products))
    
    mfg_to_product_dict[v] = mfg_products      
    print(v)
    
    driver.quit()

finaldf = pd.DataFrame(columns={'Manufacturer','Manufacturer URL','Product Name','Product URL','Product Image','Product Price','Product Specifications','Product Description'})
i=0
for key,value in mfg_to_product_dict.items():

    for eachproduct in value:
        url  = eachproduct
        
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        page = requests.get(url,headers = headers,verify=False)
        page_response = page.text
        parser = html.fromstring(page.content)
        
        productname = parser.xpath('//*[@id="product_addtocart_form"]/div[3]/div[1]/div[1]')
        name = productname[0].text_content().strip()
        
        soupvar = BeautifulSoup(page.content, "html.parser")
        imglink = soupvar.find('a', attrs={'id': 'zoom1'})
        img = imglink.get('href')
        if(img.find('placeholder/default/')!=-1):
            img = "Default"
        
        productprice = parser.xpath('//*[@id="product_addtocart_form"]/div[3]/div[1]/div[2]/div[1]/div')
        price = productprice[0].text_content().strip()
        
        
        productspecs = parser.xpath('//*[@id="product_addtocart_form"]/div[3]/div[3]')
            
        a = productspecs[0].text_content().strip().split('\n')
        
        
        a = [x.strip(' ') for x in a]
        a= list(filter(None,a))
        a=a[3:]
        data = dict(zip(a[::2], a[1::2]))
        
        productdesc = parser.xpath('//*[@id="collateral-tabs"]/dd[2]/div/div')
        productdesc = productdesc[0].text_content().strip()
        
        finaldf.set_value(i,'Manufacturer',key.split('/')[-1][:-5])
        finaldf.set_value(i,'Manufacturer URL',key)
        finaldf.set_value(i,'Product Name',name)
        finaldf.set_value(i,'Product URL',eachproduct)
        finaldf.set_value(i,'Product Image',img)
        finaldf.set_value(i,'Product Price',price)
        finaldf.set_value(i,'Product Specifications', data)
        finaldf.set_value(i,'Product Description',productdesc)
        i=i+1
        
finaldf.to_csv('Manufacturers1output.csv',index=False)
