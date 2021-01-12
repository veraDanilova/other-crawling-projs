
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import pandas as pd, numpy as np
import re

def get_user_details(link_user, browser):
    browser.get(link_user)
    print(browser.current_url)
    wait = WebDriverWait(browser, 50)
    try:
        if browser.find_element_by_xpath('//title').text != "Error 451":
            try:
                name = browser.find_element_by_xpath('//div[@class = "b-profile-group-header"][span[@class = "b-profile-group-subheader"][contains(text(), "Nombre:")]]/following-sibling::div[@class = "b-profile-group-body"]').text
            except NoSuchElementException:
                try:
                    name = browser.find_element_by_xpath('//h1[@class = "b-profile-intro-title"]/a[@href]').text
                except NoSuchElementException:
                    name = "None"

            try:
                locality = browser.find_elements_by_xpath('//div[@class = "b-profile-group-header"][span[@class = "b-profile-group-subheader"][contains(text(), "Localidad:")]]/following-sibling::div[@class = "b-profile-group-body"]/a')
                location_data = {}
                for geo in locality:
                    location_data[geo.get_attribute('class')] = geo.get_attribute('text')
            except NoSuchElementException:
                location_data = "None"
            try:
                birthdate = browser.find_element_by_xpath('//div[@class = "b-profile-group-header"][span[@class = "b-profile-group-subheader"][contains(text(), "Fecha de nacimiento:")]]/following-sibling::div[@class = "b-profile-group-body"]').text
            except NoSuchElementException:
                birthdate = "None"
            #print(name, birthdate, location_data)
            return name, birthdate, location_data


        else:
            return "blocked_user", "None", "None"
    except NoSuchElementException or StaleElementReferenceException:
        return "no_user", "None", "None"

def check_link_art(link_art, browser):
    browser.get(link_art)
    browser.implicitly_wait(5)
    if "livejournal" in browser.current_url:
        if browser.find_element_by_xpath('//title').text != "Error 451":
            
            try:
                text_parts = browser.find_element_by_xpath('//*[contains(@class, "j-e-text") or contains(@class, "aentry-post__text") or contains(@class, "entry-content") or contains(@class, "asset-body")]').text
            except NoSuchElementException or StaleElementReferenceException:
                text_parts = ""
            
            return text_parts
        else:
            return "None"
    else:
        return browser.current_url



def parse_data(browser, all_data, hashtag):
    wait = WebDriverWait(browser, 50)
    per_acc_data = []
    links_to_posts = []
    links_to_profiles = []

    for person_post in wait.until(lambda browser: browser.find_elements_by_class_name('rsearch-note__content')):
        time_art = person_post.find_element_by_xpath('.//div/span[contains(@class, "rsearch-note__time")]').text
        time = datetime.datetime.strptime(time_art, "%Y-%m-%d %H:%M:%S")
        if time.year >= 2020 and time.month >= 3:
            link_art = person_post.find_element_by_xpath('.//a[contains(@class, "rsearch-note__caption")][@href]')
            
            account_art = person_post.find_element_by_xpath('.//div/span/a[@class = "i-ljuser-username"][@title]')
            title_art = person_post.find_element_by_xpath('.//a[contains(@class, "rsearch-note__caption")][@href]').text
            tags_art = person_post.find_elements_by_xpath('.//div[contains(@class, "rsearch-tags-bar")]/a[contains(@class, "rsearch-tags-bar__link")][@href]')
            time_art = person_post.find_element_by_xpath('.//div/span[contains(@class, "rsearch-note__time")]').text
            
            print(title_art)
            print(account_art.get_attribute('title'))
            print(time_art)
            for tag_p in tags_art:
                print(tag_p.text)
            print(link_art.get_attribute('href'))
            
            per_acc_data.append([link_art.get_attribute('href'), title_art, account_art.get_attribute('title'), str([tag_p.text for tag_p in tags_art]), time_art])

            links_to_posts.append(link_art.get_attribute('href'))
            
            link_user = person_post.find_element_by_xpath('.//div/span/a[@class = "i-ljuser-profile"][@href]')
            print(link_user.get_attribute('href'))
            links_to_profiles.append(link_user.get_attribute('href'))
            #check foreign links
        else:
            print("Time Before March")
            break
    
    """['эпидемия', 'https://777hawk.livejournal.com/2790752.html', 'Небывалое - бывает! Провокаторов начали щемить', '777hawk', ['провокаторы', 'великие революционеры', 'эпидемия'], '2020-04-04 10:33:10', 'Задержана глава профсоюза "Альянс врачей"\neuronews (на русском)\nApr 3, 2020\n\nTags: Великие революционеры, Провокаторы, Эпидемия', '777hawk', '8 November', {'locality': 'Москва', 'country-name': 'Russian Federation'}]"""
    texts=[]
    user_dets=[]
    print(links_to_posts)
    if links_to_posts and links_to_profiles:
        for l in links_to_posts:
            text = check_link_art(l, browser)
            text = ' '.join(text.split())

            texts.append([text])

        for l in links_to_profiles:
            if "livejournal" not in l:
                user_dets.append(["celebrity_account", "None", "None"])
            elif l == "https://LJ_media.livejournal.com" or l == "https://www.livejournal.com" or l == "https://lj_media.livejournal.com":
                user_dets.append(["lj_media", "None", "None"])
            elif l == "https://marafonec.livejournal.com/profile":
                user_dets.append(["марафонец", "None", "None"])
            else:
                name, age, geo = get_user_details(l, browser)
                user_dets.append([name, age, str(geo)])
        for p1,p2,p3 in zip(per_acc_data, texts, user_dets):
            #'hashtag','art_link','title','acc_name','tags','time','text','name','age','geo'
            p4 = [hashtag]+p1+p3+p2

            print(len(p4), "\n")
            print(p4)
            #print(all_data.columns)
            #all_data.loc[len(all_data)] = p4
            with open('/Users/Nami/Desktop/LJ_crawl_by_tag_karantin7.csv', 'a+') as f:
                f.write('\t\t'.join(p4)+"\n")
            
    else:
        print("link lists are empty")
    
    


    Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    


    """time span class contains rsearch-note__time
    title a class rsearch-note__caption ng-binding text"""

    return all_data#[e.text for e in followers_elems]

def parse_by_tag(browser):
    hashtags=['карантин']
    all_data = pd.DataFrame(columns = ['hashtag','art_link','title','acc_name','tags','time','text','name','birthdate','geo'])
    
    
    for hashtag in hashtags:
        dataframes = []
        for pNo in range(258,500):
            print("PAGE: "+str(pNo))
            browser.get('https://www.livejournal.com/rsearch?page='+str(pNo)+'&tags='+hashtag)
            data = parse_data(browser, all_data, hashtag)
            
            
            dataframes.append(data)

            
        result = pd.concat(dataframes, axis=0, join='outer', ignore_index=False)
    return result

if __name__ == "__main__":
    browser = webdriver.Chrome('/Users/Nami/Desktop/chromedriver')
    try:
        all_data = parse_by_tag(browser)
        print (all_data)
        #all_data.to_csv('/Users/Nami/Desktop/LJ_crawl_by_tag_final.csv')
    finally:
        browser.quit()

