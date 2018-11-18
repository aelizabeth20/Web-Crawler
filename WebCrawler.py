import urllib.request, urllib.error, http.client
import os, re, threading

numOfSites = 1
index = 0


def process():
    if os.path.exists('./output.txt'):
        os.remove('./output.txt')
    if os.path.exists('./checkedsites.txt'):
        os.remove('./checkedsites.txt')
    print("Enter starting site in form: http(s)://www.example.com")
    url = input()
    writeToFile(url, './output.txt')
    while numOfSites > 0:
        myIndex = getIndex()
        scrape(readFromFile('./output.txt')[myIndex])
        adjust()
    print('Finished')


def scrape(url):
    if alreadyScraped(url):
        return
    writeToFile(url, "./checkedsites.txt")
    regex = 'href ?= ?"(http(s)?:\/\/.[^"]*[\.com|\.org|\.gov|\.edu|\.net](\/)?(\/.[^">\s]*))?"'
    try:
        html = urllib.request.urlopen(url)
    except BaseException:
        print("Error when opening:", url.strip('\n'))
        return
    try:
        source = html.read().decode('utf-8')
    except UnicodeDecodeError or http.client.IncompleteRead or ConnectionResetError:
        print("Cannot decode:", url.strip('\n'))
        return
    print(url.strip('\n'))
    matches = re.findall(regex, source)
    addToSites(len(matches))
    for match in matches:
        writeToFile(match[0], './output.txt')


def adjust():
    incrementIndex()
    decrementSites()


def writeToFile(data, site):
    writeLock.acquire(blocking=True, timeout=-1)
    with open(site, "a+") as file:
        try:
            file.write(data)
            file.write('\n')
        except UnicodeEncodeError:
            print('Cannot encode:', data)
        file.close()
    writeLock.release()


def readFromFile(site):
    with open(site, "r") as file:
        lines = file.readlines()
        file.close()
    return lines


def alreadyScraped(url):
    if os.path.exists('./checkedsites.txt'):
        lines = readFromFile("./checkedsites.txt")
        if url in lines:
            return True
    return False


def decrementSites():
    sitesLock.acquire(blocking=True, timeout=-1)
    global numOfSites
    numOfSites -= 1
    sitesLock.release()


def addToSites(number):
    sitesLock.acquire(blocking=True, timeout=-1)
    global numOfSites
    numOfSites += number
    sitesLock.release()


def incrementIndex():
    indexLock.acquire(blocking=True, timeout=-1)
    global index
    index += 1
    indexLock.release()


def getIndex():
    indexLock.acquire(blocking=True, timeout=-1)
    global index
    myIndex = index
    index += 1
    indexLock.release()
    return myIndex


sitesLock = threading.RLock()
writeLock = threading.RLock()
indexLock = threading.RLock()
threads = []
for x in range(4):
    thread = threading.Thread(target=process())
    threads.append(thread)
    thread.start()
