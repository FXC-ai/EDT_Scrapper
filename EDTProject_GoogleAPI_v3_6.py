#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 09:42:43 2021

@author: oem
"""

import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from datetime import datetime
from time import sleep
import pickle

from pprint import pprint

import pandas as pd   

def create_list_workersID (parent_directorie):

    list_directories = os.listdir(parent_directorie)
    
    return list_directories


def load_df_events_week_worker (intWeekNum,  worker_id) :

    fileName = worker_id + '_' + str(intWeekNum) + '.csv'

    path = os.path.join('save_datas', worker_id, fileName)
    
    return  pd.read_csv(path, index_col=False)


def create_list_events_week_worker (worker_id, df_events_week_worker):
    
    list_events_week_worker = list()
    
    for ind in df_events_week_worker.index:
           
        start_wp = datetime(df_events_week_worker['year_st'][ind],
                            df_events_week_worker['month_st'][ind],
                            df_events_week_worker['day_st'][ind],
                            df_events_week_worker['hour_st'][ind],
                            df_events_week_worker['min_st'][ind])
        
        end_wp = datetime(df_events_week_worker['year_nd'][ind],
                          df_events_week_worker['month_nd'][ind],
                          df_events_week_worker['day_nd'][ind],
                          df_events_week_worker['hour_nd'][ind],
                          df_events_week_worker['min_nd'][ind])

        
        event = {
                  'summary': worker_id,
                  'location': 'Route des Rottes 50, 1964 Conthey',
                  'description': 'Travail Pharmacie',
                  'start': {
                    'dateTime': start_wp.isoformat() + '+02:00',
                    'timeZone': 'Europe/Zurich',
                  },
                  'end': {
                    'dateTime': end_wp.isoformat()+'+02:00',
                    'timeZone': 'Europe/Zurich',
                  },     
                }

        list_events_week_worker.append(event)
        
    return list_events_week_worker


def createAPI_object(SCOPES):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    
    return service


def create_list_Calendars (service) :
    
    page_token = None
    
    while True:
      list_calendars = service.calendarList().list(pageToken=page_token).execute()

      page_token = list_calendars.get('nextPageToken')
      if not page_token:
        break

    return list_calendars['items']


def create_new_calendars (service, list_calendars, list_workersID) :
    
    list_summary = list()
    for calendar in list_calendars :
        list_summary.append(calendar['summary'])
        
    list_new_calendars = list(filter(lambda x : x not in list_summary, list_workersID))
        
    for workerID in list_new_calendars:
        calendar = {
            'summary': workerID,
            'timeZone':'Europe/Zurich'
        }
        
        created_calendar = service.calendars().insert(body=calendar).execute()
        
        pprint(created_calendar)

def create_dict_worker_calendarId (list_calendars):
    
    dict_worker_calendarId = dict()
    
    for calendar in list_calendars:
        dict_worker_calendarId[calendar['summary']] = calendar['id']
        
    return dict_worker_calendarId

def delete_events_Week_Worker (service, worker_calendarId , intWeekNum) :
    
    # Enables to delete every events belonging to the worker during the given week
    
    monday = datetime.fromisocalendar(2021, intWeekNum, 1).isoformat()+ '+02:00'
    sunday = datetime.fromisocalendar(2021, intWeekNum, 7).isoformat()+'+02:00'
    period = (monday, sunday)
    
    page_token = None
    while True:
      worker_events = service.events().list(calendarId=worker_calendarId, 
                                     timeMin = period[0], 
                                     timeMax = period[1],
                                     pageToken=page_token).execute()  
      page_token = worker_events.get('nextPageToken')
      if not page_token:
        break

    for event in worker_events['items'] :
        service.events().delete(calendarId=worker_calendarId, eventId=event['id']).execute()
        
    print('Les évènements de la semaine {} ont été supprimés'.format(intWeekNum))


def add_events_week_worker (service, worker_calendarId, list_events_week_worker):
    
    # Enables to add events to the google calendar
    
    for event in list_events_week_worker:
        service.events().insert(calendarId=worker_calendarId, body=event).execute()

    print('Les évènements de la semaine ont été ajoutés.')

def create_list_WeekNum_worker (parent_directorie, worker_id, start,end):
    
    # Enables to list every INt weeks of a worker
    
    worker_directorie = parent_directorie + '/' + worker_id

    
    listeFichiers = []
    for (repertoire, sousRepertoires, fichiers) in os.walk(worker_directorie):
        listeFichiers.extend(fichiers)
    
    list_WeekNum = list()
    for fichier in listeFichiers :
        weekNum = int(fichier.split('_')[1].split('.')[0])
        if weekNum >= start and weekNum <= end :
            list_WeekNum.append(weekNum)
    
    return sorted(list_WeekNum)

#______________________________________________________________________________

SCOPES = ['https://www.googleapis.com/auth/calendar']
service = createAPI_object(SCOPES)

parent_directorie = 'save_datas'
start = 41
end = 49

list_workersID = create_list_workersID(parent_directorie)

list_calendars = create_list_Calendars (service)

create_new_calendars(service,list_calendars,list_workersID)

list_calendars = create_list_Calendars (service)

dict_worker_calendarId = create_dict_worker_calendarId(list_calendars)

for worker_id in list_workersID:
    
    print('Current worker : {}'.format(worker_id))
    
    list_WeekNum_worker = create_list_WeekNum_worker(parent_directorie, worker_id, start, end)
    
    for intWeekNum in list_WeekNum_worker :
        
        df_events_week_worker = load_df_events_week_worker(intWeekNum, worker_id)
        
        list_events_week_worker = create_list_events_week_worker (worker_id, df_events_week_worker)
                      
        worker_calendarId = dict_worker_calendarId[worker_id]
        
        delete_events_Week_Worker(service, worker_calendarId, intWeekNum)
        sleep(3.5)
        add_events_week_worker(service, worker_calendarId, list_events_week_worker)
        sleep(4.)
