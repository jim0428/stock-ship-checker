from bs4 import BeautifulSoup
import requests
from flask import Flask,request,abort
import json
import re
import pandas as pd

temp = []
store = {}
import pandas as pd
df = pd.read_excel(r"stock.xlsx")
for i in range(len(df.columns.ravel())):
    #df[i] = df[i].replace("\xa0","")
    #print(df[df.columns.ravel()[i]].tolist())
    flag = 0
    tmp = []
    for k in range(len(df[df.columns.ravel()[i]].tolist())):
        cut = str(df[df.columns.ravel()[i]].tolist()[k]).replace(u'\xa0', u'')
        if(flag == 0 and re.match(r'^[0-9]+$',cut) and cut != 'nan'):
            tmp.append(cut)
            flag += 1
        elif(flag == 1):
            tmp.append(cut)
            store[tmp[0]] = tmp[1]
            tmp.clear()
            flag = 0

with open("No.json", "w", encoding='utf-8') as outfile: 
    json.dump(store, outfile, ensure_ascii=False,indent = 4)
print(store)