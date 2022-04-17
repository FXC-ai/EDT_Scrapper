#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:55:05 2021

@author: oem

Pour installer geckoDriver, il suffit d'écrire
geckodriver dans l'invite de commande
et de suivre les instructions

sudo install geckodriver 

"""


#Simple assignment
from selenium.webdriver import Firefox
from time import sleep
import os


def open_ontime_benu (driver) :
      
    driver.maximize_window()
    sleep(3.0)
        
    driver.get("https://ontime.benu.ch")
    driver.find_element_by_name("username").send_keys("")
    driver.find_element_by_name("password").send_keys("")
    driver.find_element_by_name("loginButton").click()
    sleep(3.)
    
    driver.find_element_by_xpath("//input[@id='eventTypesButton:2']/./..").click()
    sleep(6.)
    driver.find_element_by_xpath("//input[@id='eventTypesButton:1']/./..").click()
    sleep(3.)
    
    header2 = driver.find_element_by_class_name('header2').text
    int_week_origin = int(header2.split(' ')[1])
    return int_week_origin

def go_to_week_start (driver, int_week_start, int_week_origin) :
    
    int_week_current = int_week_origin
    
    while int_week_current != int_week_start+1:
        header2 = driver.find_element_by_class_name('header2').text
        int_week_current = int(header2.split(' ')[1])
        print(int_week_current)
        driver.find_element_by_name("previous").click()
        sleep(2.5)
        

def save_html_week (driver, int_week_start, int_week_end):
    
    for _ in range((int_week_end - int_week_start)+1):
        header2 = driver.find_element_by_class_name('header2').text
        int_week_current = int(header2.split(' ')[1])
        
        html_code = driver.page_source
        with open('ScrapEDTest/PEP_{}.html'.format(int_week_current), 'w') as fichier :
            fichier.write(html_code)
            print('Semaine {} sauvée'.format(int_week_current))
                
        try:
            driver.find_element_by_name("next").click()
        except :
            print('Voila ça a pas marché')
        
        sleep(3.5)
        
        

driver = Firefox()
int_week_start = 39
int_week_end = 49

int_week_origin = open_ontime_benu(driver)
go_to_week_start(driver, int_week_start, int_week_origin)
save_html_week(driver, int_week_start, int_week_end)

'''
for _ in range(10) :
    html_code = driver.page_source
    
    header2 = driver.find_element_by_class_name('header2').text
    week_Nb = int(header2.split(' ')[1])
    
    with open('ScrapEDTest/PEP_{}.html'.format(week_Nb), 'w') as fichier :
        fichier.write(html_code)
        
    driver.find_element_by_name("previous").click()
    sleep(3.)

driver.find_element_by_name("next").click()
'''

'''


driver.find_element_by_name("next").click()

week_min = 2
week_max = 52
press_previous = week_Nb - week_min
press_next = week_max - week_min

html_code = driver.page_source
    
    
with open('ScrapEDTest/PEP_{}.html'.format(week_Nb), 'w') as fichier :
    fichier.write(html_code)   

for _ in range(press_previous) :
    driver.find_element_by_name("previous").click()
    sleep(1.0)

for week_num in range (press_next+1):
    html_code = driver.page_source
    
    
    with open('ScrapEDTest/PEP_{}.html'.format(str(week_num  + week_min)), 'w') as fichier :
        fichier.write(html_code)    
    
    driver.find_element_by_name("next").click()
    
    

    sleep(2.)

'''
