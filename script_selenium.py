import time
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

URL = "https://www.youtube.com/results?search_query="

def p(str):
    print("%s| %s" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S") , str))
pass


def getData(Search_URL, driver):
    b = driver
    b.get(Search_URL)
    duration = ""

    try:
       # WebDriverWait(b, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='video-title']")))
        time.sleep(1)
        web_page = b.page_source
        soup = BeautifulSoup(web_page, 'html.parser')
        duration = (soup.find("a", {"id": "thumbnail"})
          .find("div", {"id":"overlays"})
          .find("ytd-thumbnail-overlay-time-status-renderer")
          .span
          .get_text())
        
        duration = duration.replace("\n", "")
        duration = duration.replace(" ", "")

        b.find_element_by_xpath("//*[@id='video-title']").click()
        p("Video found")
    except:
        p("Can't find video")
        return "null"

    time.sleep(2)
    b.execute_script("window.scrollTo(0, 300);")
    time.sleep(0.1)
    b.execute_script("window.scrollTo(0, 400);")
    time.sleep(0.1)
    b.execute_script("window.scrollTo(0, 500);")
    time.sleep(0.1)
    b.execute_script("window.scrollTo(0, 600);")
    time.sleep(0.1)
    b.execute_script("window.scrollTo(0, 700);")
  
   
    comment = ""
    try:
        web_page = b.page_source
        soup = BeautifulSoup(web_page, 'html.parser')
        comment = (soup.find("ytd-item-section-renderer", {"id": "sections"})
          .h2
          .find("yt-formatted-string")
          .find("span", {"class": "style-scope yt-formatted-string"})
          .get_text())
    except:
        p("Durations: " +  duration + ", but can't find Comments for "+ Search_URL)
        return ["disabled", duration]


    p(comment + " Comments for " + Search_URL)
    res= [comment, duration]
    return res


pass

"""
def getTitles():
    titlesList = []
    with open('clean_tedx_dataset.csv', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            title = row[2]
            title = title.replace("\"", "")
            title = title.replace("\"", "")
            titlesList.append(title)
            line_count += 1
        p(f'Processed {line_count} lines.')
        return titlesList
pass
"""
def getIds():
    idList = []
    with open('clean_tedx_dataset.csv', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            id = row[0]
            idList.append(id)
            line_count += 1
        p(f'Processed {line_count} lines.')
        return idList
pass

def getUrls():
    urlsList = []
    base_url = "https://www.youtube.com/results?search_query="
    with open('clean_tedx_dataset.csv', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            title = row[2]
            title = title.replace("\"", "")
            title = title.replace("\\", "")
            title = title.replace(" ", "+")
            title = title.replace("'", "%27")
            url = base_url + title
            urlsList.append(url)
            line_count += 1
        p(f'Processed {line_count} lines.')
        return urlsList
pass

def openBrowser (s) :
    try:
        driver = webdriver.Chrome()
        driver.get(URL+ s)
        p("Started browser for " + URL + s)
    except:
        p("Failed to open browser")
        
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button")))
        element = driver.find_element_by_xpath(
            "//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button")
        driver.execute_script("arguments[0].click();", element)
    except:
        p("Can't accept YT Conditions")
    p("YT conditions accepted")

    return driver
pass

if __name__ == "__main__":

    urls = getUrls()
    ids= getIds()
    
    driver = openBrowser("sasso")

    for i in range(len(urls)): 
        data = getData(urls[i], driver)
        count= 0
        while((data== "null" or data[0] == "disabled") and count<3) :
            driver.close()
            driver.quit() 
            try:
                driver = openBrowser(urls[i])
            except:
                p("can't switch tab")
            count+= 1
            data= getData(urls[i], driver)

        if(i == 0):
            datastr = ids[i] + "," + data[0] + "," + data[1]
        else:
            datastr += "\n" + ids[i] + "," + data[0] + "," + data[1]
        with open('dataset.csv', 'w') as f:
            f.write(datastr)
pass
