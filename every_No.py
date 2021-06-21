#!/usr/bin/env python
#coding=utf-8
import json 
def get():
    with open('No.json','r',encoding = "utf-8") as jsonfile:
        data = json.load(jsonfile)
    return data