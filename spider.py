# -*- coding: utf-8 -*-

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

INDEX_DEATH_ROW_INFO_URL = 1
INDEX_LAST_STATEMENT_URL = 2

base_url = "https://www.tdcj.texas.gov/death_row/"
death_row_infos = []

headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language':'zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
     'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Cookie': "__utmc=67821652; __utmz=67821652.1550809495.1.1.utmcsr=ruanyifeng.com|utmccn=(referral)|utmcmd=referral|utmcct=/blog/2019/02/weekly-issue-44.html; menu_generic_headers=-1c; __utma=67821652.1534429385.1550809495.1550811580.1550815385.3; __utmt=1; __utmb=67821652.5.10.1550815385",
    'Host':'www.tdcj.texas.gov',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
} 
source_html = requests.get(base_url + "dr_executed_offenders.html", 
                           headers=headers).text
soup = BeautifulSoup(source_html, 'html.parser')
soup_table = soup.find("table", attrs={"class": "tdcj_table indent"})
soup_trs = soup_table.find_all("tr")

# parse attributes in first line
attribute_list = [soup_th.get_text().strip() for soup_th in soup_trs[0].find_all("th")]
# two attribute is fuzzy, change it
attribute_list[INDEX_DEATH_ROW_INFO_URL] = "Offender Information URL"
attribute_list[INDEX_LAST_STATEMENT_URL] = "Last Statement URL"
attribute_list = [attribute.lower().replace(" ", "_") for attribute in attribute_list]

# parse detail of death rows
for soup_death_row in soup_trs[1: ]:
    soup_tds = soup_death_row.find_all("td")
    value_list = [soup_td.get_text().strip() for soup_td in soup_tds]
    # get special attribute value
    death_row_info_url = base_url + soup_tds[INDEX_DEATH_ROW_INFO_URL].find("a").get('href')
    last_statement_url = base_url + soup_tds[INDEX_LAST_STATEMENT_URL].find("a").get('href')
    value_list[INDEX_DEATH_ROW_INFO_URL] = death_row_info_url
    value_list[INDEX_LAST_STATEMENT_URL] = last_statement_url
    death_row_infos.append(dict(zip(attribute_list, value_list)))

# get last statement
for death_row_info in death_row_infos:
    last_statement_url = death_row_info["last_statement_url"]
    print("number:", death_row_info["execution"])
    last_statement_html = requests.get(last_statement_url, 
                                       headers=headers).text
    soup = BeautifulSoup(last_statement_html, 'html.parser')
    last_statement_fixed_html = soup.prettify()
    split_results = soup.text.split('Last Statement:')
    last_statement = split_results[1].strip() if len(split_results) > 1 else "No last statement"
    split_results = last_statement.split('Employee Resource')
    last_statement = split_results[0].strip() if len(split_results) > 1 else "No last statement"
 
    print(last_statement)  
    death_row_info.update({"last_statement": last_statement})
    time.sleep(3)
    
pd_data = pd.DataFrame(death_row_infos)
pd_data.to_csv("Last-Statement-of-Death-Row.csv")