#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 17:28:37 2021

@author: oem
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta, date
import numpy as np
import pickle
import pandas as pd
import calendar
import pprint
import os

def BeautifulSoupCreator (int_weekNum) :
    
    #Instanciation of soup object for the chosen week
    
    fichier = open('ScrapEDTest/PEP_{}.html'.format(int_weekNum), 'r')
    
    html = fichier.read()
       
    soup_week = BeautifulSoup(html,'html.parser')
    
    return soup_week


def weekNumberFinder (soup_week) :
    
    #returns the scraped week number
    
    int_weekNum = int(soup_week.find_all("span", class_="header2")[0].string.split()[1])
    
    return int_weekNum


def scrapWorkers (soup_week):
    
    #return a list containing the id of every workers
    
    div_workers = soup_week.findAll('div', class_='resourceNameCol')
    
    list_workers = list()
    
    for div in div_workers :   
        identity = div.contents[0].string.split(', ')
        name = identity[-1]
        surname = identity[0]
        id_worker = surname + ' ' + name
        list_workers.append(id_worker)
        
    del(list_workers[0:2])
    
    return list_workers


def scrapCommentsBars (soup_week) :
    
    div_commentsbar = soup_week.find_all('div', class_ = ['fc-event fc-event-skin fc-event-hori fc-corner-left fc-corner-right commentsbar fizCmt','fc-event fc-event-skin fc-event-hori fc-corner-left fc-corner-right commentsbar'])    

    list_commentsbar = list()
    
    for div_comment_bar in div_commentsbar:
        
        list_style_commentsbar = div_comment_bar['style'].split(';')
        
        for ind, style in enumerate(list_style_commentsbar) :
            if style.find('left') != -1:
                left = re.findall(r"[-+]?\d*\.\d+|\d+", style)
            if style.find('top') != -1:
                top = re.findall(r"[-+]?\d*\.\d+|\d+", style)
            if style.find('width') != -1:
                width = re.findall(r"[-+]?\d*\.\d+|\d+", style)
        
        list_commentsbar.append({'top':float(top[0]), 'left':float(left[0]), 'width':float(width[0])})
        
    if len(list_commentsbar) !=7 :
        print('Error, a day is missing !')
    
    return list_commentsbar           
            
    

def scrapReferencesTable (soup_week):
    
    # This function is for scrapping the differents opening period of the week
    # Take care in case of public holiday
    
    div_opehrbars = soup_week.findAll('div', class_ = 'fc-event fc-event-skin fc-event-hori fc-corner-left fc-corner-right opehrsbar')
    list_opehrbars = list()
    
    for div_opehrbar in div_opehrbars :
    
        list_style_opehrbars = div_opehrbar['style'].split(';')
        
        for ind, style in enumerate(list_style_opehrbars) :
            if style.find('left') != -1:
                left = re.findall(r"[-+]?\d*\.\d+|\d+", style)
            if style.find('top') != -1:
                top = re.findall(r"[-+]?\d*\.\d+|\d+", style)
            if style.find('width') != -1:
                width = re.findall(r"[-+]?\d*\.\d+|\d+", style)
        
        list_opehrbars.append({'top':float(top[0]), 'left':float(left[0]), 'width':float(width[0])})
        
    return list_opehrbars


def scrapTimePeriods (soup_week):
    
    #Here we scrap every activity bar period of the week (for every workers)
    
    div_actbars = soup_week.find('div', class_='fc-view fc-view-resourceWeek fc-grid')
    list_actbars_data = list()
    
    for div_actbar in div_actbars.contents[0].children :
        
        list_style_actbar = div_actbar['style'].split(';')
        for ind, style in enumerate(list_style_actbar):
            if style.find('left') != -1 :
                left = re.findall(r"[-+]?\d*\.\d+|\d+", style)        
            if style.find('top') != -1:
                top = re.findall(r"[-+]?\d*\.\d+|\d+", style)
        
        type_actbar = div_actbar['class'][-1]
        
        if type_actbar == 'actbar':
            for sibling in div_actbar :
            #this loop enable to scrap the begining and the end time of each work period. 
            #It puts it in the variable called period.
                period = sibling.string.split('-')
                h1 = int(period[0].split(':')[0])
                m1 = int(period[0].split(':')[1])
                h2 = int(period[1].split(':')[0])
                m2 = int(period[1].split(':')[1])                      
                period = [(h1,m1),(h2,m2)]
                list_actbars_data.append({'type':type_actbar,'top':float(top[0]),'left':float(left[0]), 'period':period})
        
        list_actbars_data = sorted(list_actbars_data, key=lambda list_actbars_data: list_actbars_data['top'])                
        list_actbars_data = [actbar_data for actbar_data in list_actbars_data if actbar_data['type'] != 'commentsbar' and actbar_data['type'] != 'opehrsbar']
        
    return list_actbars_data


def matchTopsWithWorkers (list_actbars_data, list_opehrbars, list_workers):
    
    # Return a dict containing id workers as value and top as keys
    
    # This part is for listing every top of the differents actbars
    list_top = list()
    list_top_diff = list()
    
    for actbar_data in list_actbars_data :
        list_top.append(actbar_data['top'])

    list_top = set(list_top)    
    list_top = sorted(list_top)
    

    # This part is for listing every top references in opehrbars, hopefully there is only one
    set_top_opehrbars = set()
    
    for opehrsbar in list_opehrbars :
        set_top_opehrbars.add(opehrsbar['top'])
    
    int_refTop = list(set_top_opehrbars)[0] if len(list(set_top_opehrbars)) == 1 else print('Error Multi Top Reference')
    
    
    # Substraction between top of actbars and the reference
    for top in list_top :
        list_top_diff.append(top - int_refTop)
    
    
    # Cheking the modulo of 47 of each value, that enables to know which worker is present at a moment durind the week
    arr_top_diff_modulo = np.array(list_top_diff)%47
    
    list_top_diff_modulo = arr_top_diff_modulo.tolist()
    
    dict_association_TopWorker = dict()
    
    for ind, value in enumerate(list_top_diff_modulo) :
        if value == 39 :
            dict_association_TopWorker[list_workers[ind]] = list_top[ind]
        elif value == 36 :
            dict_association_TopWorker[list_workers[ind+1]] = list_top[ind]
        elif value == 33 :
            dict_association_TopWorker[list_workers[ind+2]] = list_top[ind]
        elif value == 30 :
            dict_association_TopWorker[list_workers[ind+3]] = list_top[ind]
        elif value == 27 :
            dict_association_TopWorker[list_workers[ind+4]] = list_top[ind]
        elif value == 24 :
            dict_association_TopWorker[list_workers[ind+5]] = list_top[ind]
        elif value == 21 :
            dict_association_TopWorker[list_workers[ind+6]] = list_top[ind]
        elif value == 18 :
            dict_association_TopWorker[list_workers[ind+7]] = list_top[ind]            
        elif value == 15 :
            dict_association_TopWorker[list_workers[ind+8]] = list_top[ind]            
    

    
    dct = {v:k for k, v in dict_association_TopWorker.items()}    
    dict_association_TopWorker = dct

    return dict_association_TopWorker

def matchLeftWithDays (list_commentsbar, year, int_weekNum):
    
    list_WeekDate = list()
    list_association_LeftDate = list()
    
    list_commentsbar = sorted(list_commentsbar, key=lambda list_commentsbar: list_commentsbar['left']) 
    
    for n in range(7):
        list_WeekDate.append(datetime.fromisocalendar(year, int_weekNum, n+1).strftime('%d-%m-%Y'))
    

    for ind, comment_bar in enumerate(list_commentsbar):
        list_association_LeftDate.append([list_WeekDate[ind], comment_bar['left'], comment_bar['left'] + comment_bar['width']])         

    return list_association_LeftDate

def Deprecated_create_List_Events_Week (list_association_LeftDate, dict_association_TopWorker, list_actbars_data, list_workers):
    
    list_events_week_worker = list()
    dict_events_week = dict()
    
    for key, worker in dict_association_TopWorker.items() :
        for actbar in list_actbars_data :
            if actbar['top'] == key :                                
                list_events_week_worker.append([actbar['left'], actbar['period']])
                
        dict_events_week[worker] = list_events_week_worker
        list_events_week_worker = []
               
    
    dict_events_week_1 = dict()
    list_events_week_worker_1 = list()
    
    for worker, events in dict_events_week.items() :
        for event in events :
            for dat in list_association_LeftDate :
                #print('La date est ', dat, 'et l event est ', event)
                if event[0] > dat[1] and event[0] < dat[2] :
                    #print(worker, 'travaille le ',dat[0],'sur ces horaires', event[1])
                    start_wp = datetime(int(dat[0].split('-')[2]), int(dat[0].split('-')[1]), int(dat[0].split('-')[0]), event[1][0][0], event[1][0][1])
                    end_wp = datetime(int(dat[0].split('-')[2]), int(dat[0].split('-')[1]), int(dat[0].split('-')[0]), event[1][1][0], event[1][1][1])
                    #print(start_wp.strftime('%d-%m-%Y à %H h %M'))
                    #print(end_wp.strftime('%d-%m-%Y à %H h %M'))
                    #print(end_wp-start_wp)
                    list_events_week_worker_1.append([start_wp, end_wp])
            
        dict_events_week_1[worker] = pd.DataFrame(list_events_week_worker_1, columns = ['start_wp', 'end_wp'])
        list_events_week_worker_1 = []


    return dict_events_week_1

def create_List_Events_Week (list_association_LeftDate, dict_association_TopWorker, list_actbars_data, list_workers):
    
    list_events_week_worker = list()
    dict_events_week = dict()
    
    for key, worker in dict_association_TopWorker.items() :
        for actbar in list_actbars_data :
            if actbar['top'] == key :                                
                list_events_week_worker.append([actbar['left'], actbar['period']])
                
        dict_events_week[worker] = list_events_week_worker
        list_events_week_worker = []
               
    
    dict_events_week_1 = dict()
    list_events_week_worker_1 = list()
    
    for worker, events in dict_events_week.items() :
        for event in events :
            for dat in list_association_LeftDate :
                #print('La date est ', dat, 'et l event est ', event)
                if event[0] > dat[1] and event[0] < dat[2] :
                    #print(worker, 'travaille le ',dat[0],'sur ces horaires', event[1])
                    start_wp = datetime(int(dat[0].split('-')[2]), #année
                                        int(dat[0].split('-')[1]), #month
                                        int(dat[0].split('-')[0]), #day
                                        event[1][0][0], #hour
                                        event[1][0][1]) #minutes
                    
                    year_st = int(dat[0].split('-')[2])
                    month_st = int(dat[0].split('-')[1])
                    day_st = int(dat[0].split('-')[0])
                    hour_st = event[1][0][0]
                    min_st = event[1][0][1]
                    
                    end_wp = datetime(int(dat[0].split('-')[2]), 
                                      int(dat[0].split('-')[1]), 
                                      int(dat[0].split('-')[0]), 
                                      event[1][1][0], 
                                      event[1][1][1])
                    
                    year_nd = int(dat[0].split('-')[2])
                    month_nd = int(dat[0].split('-')[1])
                    day_nd = int(dat[0].split('-')[0])
                    hour_nd = event[1][1][0]
                    min_nd = event[1][1][1]
                    
                    
                    #print(start_wp.strftime('%d-%m-%Y à %H h %M'))
                    #print(end_wp.strftime('%d-%m-%Y à %H h %M'))
                    #print(end_wp-start_wp)
                    list_events_week_worker_1.append([year_st, month_st, day_st, hour_st, min_st, year_nd, month_nd, day_nd, hour_nd, min_nd])
            
        dict_events_week_1[worker] = pd.DataFrame(list_events_week_worker_1, columns = ['year_st', 'month_st', 'day_st', 'hour_st', 'min_st', 'year_nd', 'month_nd', 'day_nd', 'hour_nd', 'min_nd'])
        list_events_week_worker_1 = []

    return dict_events_week_1

def save_Datas_Week (list_events_week, int_weekNum):
    
    for worker in list_events_week.keys() :
        
        directory = 'save_datas/{}'.format(worker)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        fileName =  worker + '_' + str(int_weekNum) + '.csv'
        
        list_events_week[worker].to_csv(path_or_buf=directory + '/' + fileName, index = False )

            
    
#____________________________________________________________________________

year = 2021
start = 44
end = 45

for int_weekNum in range(start, end):
    soup_week = BeautifulSoupCreator(int_weekNum)
    num_week_check = weekNumberFinder(soup_week)
    
    if int_weekNum != num_week_check :
        print('Error Data File')
        
    list_workers = scrapWorkers(soup_week)
        
    list_opehrbars = scrapReferencesTable(soup_week)
    
    list_commentsbar = scrapCommentsBars(soup_week) 
    
    list_actbars_data = scrapTimePeriods(soup_week)
        
    dict_association_TopWorker = matchTopsWithWorkers (list_actbars_data, list_opehrbars, list_workers)
    
    list_association_LeftDate = matchLeftWithDays(list_commentsbar, year, int_weekNum)
    
    list_events_week = create_List_Events_Week(list_association_LeftDate, dict_association_TopWorker, list_actbars_data, list_workers)
    
    save_Datas_Week(list_events_week, int_weekNum)