from bs4 import BeautifulSoup
import yt_dlp
import os
import shutil
import glob
#import logging
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

sys.setrecursionlimit(10000)

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

soup = BeautifulSoup()
with open('./temp1.html', 'rb') as file1:
    soup = BeautifulSoup(file1.read(), 'html.parser', from_encoding='utf-8')

nextDownload = False
currentEntry = 0

def videoOptions(alternativeTitle, checkSameTitle):
    options = {
    ####'format': 'm4a',
    'verbose': True,
    'format': 'm4a/bestaudio/best',
    'nooverwrites': True,
    'download_archive': 'video-logger-and-error-files/downloadList.txt',
    'outtmpl': f'downloaded-files/audio-files/%(title)s.%(ext)s' if checkSameTitle else f'downloaded-files/audio-files/%(title)s - ({alternativeTitle}).%(ext)s',
    'writedescription': True,
    'writeinfojson': True,
    'writethumbnail': True,
    'embedthumbnail': True,
    "noplaylist":   True, # Remove if I need to download a whole playlist
    'ignoreerrors': nextDownload, #Delete Later or add a way to write the names of the files I can't download
    'retries': 1000,
    'fragment_retries': 1000,
    ##'format': 'bestaudio[ext=mp3]/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
        ####'preferredquality': '320',
        'preferredquality': 'best',
        'nopostoverwrites': True },
        ##{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3','preferredquality': '192'},
        {'key': 'FFmpegMetadata', 'add_metadata': 'True'},
        {'key': 'XAttrMetadata'},
        {'key': 'EmbedThumbnail'},
    ],
    }

    return options

# ADD LOGGER AND PROGRESS HOOK (CHECK GITHUB DOCS PAGE)

def moveFiles(extension):

    sourcePath = os.path.abspath('downloaded-files/audio-files/*.' + extension)
    if (extension != 'json' and extension != 'description'):
        newPath = os.path.abspath('downloaded-files/thumbnail-files/') 
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        destinationPath = newPath
    else:
        newPath = os.path.abspath('downloaded-files/' + extension + '-files/')
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        destinationPath = newPath
    
    print(extension)

    for file in glob.glob(sourcePath):
        shutil.move(file, destinationPath)
        print(file)

def translateTitleToObtainAlternativeTitle(link):
    # titleOptions = {
    #     'extractor_args' : {'youtube' : {'lang' : ['sk']}},
    # }
    try:
        # with yt_dlp.YoutubeDL(titleOptions) as ydl:
        with yt_dlp.YoutubeDL() as ydl:
            infoDictionary = ydl.extract_info(link, download = False)
            videoTitle = infoDictionary.get("title", None)
            print(videoTitle)

            alternativeTitleTemp = getTranlatedTitle(videoTitle)
    except Exception as ex:
        videoTitle = ""
        alternativeTitleTemp = ""

    return (str(alternativeTitleTemp), videoTitle)
    
def getTranlatedTitle(title):
    custom_options = Options()
    custom_options.add_argument('--headless=new')

    driver = webdriver.Chrome(executable_path = './selenium_chrome_driver/chromedriver-win64/chromedriver.exe', options = custom_options)

    driver.delete_all_cookies()
    
    driver.get('https://translate.google.com/?sl=ja&tl=en&op=translate')

    driver.implicitly_wait(30)

    driver.find_element(by=By.CLASS_NAME, value="er8xn")
    time.sleep(3)

    driver.find_element(by=By.CLASS_NAME, value="er8xn").send_keys(title)
    time.sleep(3)
    
    outputTitle = driver.find_element(by=By.CLASS_NAME, value="ryNqvb").text
    if ("--" in outputTitle):
        outputTitle = outputTitle.replace('--', '- ')
    if ("-" in outputTitle):
        outputTitle = outputTitle.replace('-', '- ')

    if ("/" in outputTitle):
        outputTitle = outputTitle.replace('/', '-')   
    print(outputTitle)
    driver.quit()

    return outputTitle

def embedThumbnailToAudio():
    sourcePath = os.path.abspath('downloaded-files/audio-files/')

    for file in glob.glob(sourcePath):
        print(file)
        print(file.endswith(".webp"))
        #if (file.endswith(".webp")):
        #    os.system(f"ffmpeg -i {file} {file}.jpg")
        #shutil.move(file, destinationPath)
        #print(file)

for link in soup.find_all('a'):
    video = link.get('href')
    currentEntry += 1

    # TEMP
    alternativeTitleFinal = translateTitleToObtainAlternativeTitle(video)

    # check if same title and also add cover art
    if (isEnglish(alternativeTitleFinal[1])):
        sameTitle = True
    else:
        sameTitle = False  

    print(sameTitle)    

    options = videoOptions(alternativeTitleFinal[0], sameTitle)

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video])
            #shutil.copy()
        print(currentEntry)
        nextDownload = False
    except Exception as ex:
        newPath = os.path.abspath('video-logger-and-error-files/')
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        with open('video-logger-and-error-files/error-file.txt', 'a', encoding = 'utf-8') as errorFile:
            errorFile.write('\n' + str(link.text) + ' Line Number in Bookmark Bar File: ' + str(currentEntry + 10) + '\n')
            print(link.text)
        print("HELLO " + str(link))
    #nextDownload = True

embedThumbnailToAudio()
# Move all files
moveFiles('json')
moveFiles('description')
moveFiles('webp')
moveFiles('png')
moveFiles('jpg')


# FIX JPG FILES NOT MOVING INTO OTHER FOLDER
# Remove Playlist
# REMOVE 1 HOUR LONG LOOP TRACKS FROM BOOKMARK FOLDER