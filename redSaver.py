import praw
import os
import csv
import urllib
#these are just for the imgur specific methods
import requests
from bs4 import BeautifulSoup

r = praw.Reddit(user_agent = 'redSaver by /u/neph001')

def downloadImage(imageUrl, localFileName):
    response = requests.get(imageUrl)
    if response.status_code == 200:
        print('Downloading %s to %s...' % (imageUrl, localFileName))
        with open(localFileName, 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

try:
    r.login()
except praw.errors.APIException:
    pass
while r.is_logged_in() == False:
    os.system('cls' if os.name == 'nt' else 'clear')
    print "Invalid Username or password"
    try:
        r.login()
    except praw.errors.APIException:
        pass


os.system('cls' if os.name == 'nt' else 'clear')

def loadRules():
    try:
        reader = csv.reader(open('redSaver.csv', 'rb'))
        rules = dict(x for x in reader)
        return rules
    except IOError:
        print "File did not exist, empty ruleset."
        return {}


def saveRules(rules):
    writer = csv.writer(open('redSaver.csv', 'wb'))
    for key, value in rules.items():
        writer.writerow([key, value])

def makeRule():
    rules = loadRules()
    subreddit = raw_input("Enter a subreddit name: ")
    dir = raw_input("Enter an absolute path: ")
    rules[subreddit] = dir
    saveRules(rules)

def deleteRule():
    rules = loadRules()
    subreddit = raw_input("Enter the subreddit for the rule you wish to delete: ")
    del(rules[subreddit])
    saveRules(rules)


def listRules():
    rules = loadRules()
    if rules == {}:
        print "No rules found."
    else:
        for subreddit in rules:
            print subreddit + " : " + rules[subreddit]
    raw_input("Press Enter to continue...")

def save():
    rules = loadRules()
    links = r.user.get_saved(limit=None)
    count = 0
    for link in links:
        if rules.has_key(str(link.subreddit)):
            if str(link.url).endswith('.jpg') or str(link.url).endswith('.png') or str(link.url).endswith('.gif'):
                saveGenericImage(link, rules)
                count+=1
            elif str(link.url).startswith("http://imgur.com/a/"):
                count += saveImgurAlbum(link, rules)
            elif str(link.url).startswith("http://imgur.com/"):
                count += saveImgurSingle(link, rules)
    print "Saved " + str(count) + " images."
    raw_input("Press Enter to continue...")

def saveGenericImage(link, rules):
    print "Saving " + str(link).decode('utf-8') + " to " + rules[str(link.subreddit)] + "/" + link.url.split('/')[-1]
    if not os.path.isdir(rules[str(link.subreddit)]):
        os.makedirs(rules[str(link.subreddit)])
        print "Directory did not exist, created it..."
    urllib.urlretrieve(link.url, rules[str(link.subreddit)] + "/" + link.url.split('/')[-1])

def saveImgurAlbum(submission, rules):
    """
    This code comes directly from:
    http://inventwithpython.com/blog/2013/09/30/downloading-imgur-posts-linked-from-reddit-with-python/
    All credit to original author. I didn't find it until I was half done with this project,
    but he mostly already solved the problem I was trying to solve here so it made sense to use
    some of that code. I also learned a lot about BeautifulSoup by studying that example, so thanks.
    """

    if not os.path.isdir(rules[str(submission.subreddit)]):
        os.makedirs(rules[str(submission.subreddit)])
        print "Directory did not exist, created it..."

    #force blog layout
    if '#' in submission.url:
        url = submission.url[:submission.url.rfind('#')] + "/layout/blog"
    elif '/layout' in submission.url:
        url = submission.url[:submission.url.rfind('/layout')] + "/layout/blog"
    else:
        url = submission.url + "/layout/blog"

    print "Downloading imgur album: " + str(submission)
    print "From: " + url
    htmlSource = requests.get(url).text

    soup = BeautifulSoup(htmlSource)
    matches = soup.select('.album-view-image-link a')
    count = 0
    for match in matches:
        imageUrl = match['href']
        if '?' in imageUrl:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
        else:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:]
        if imageFile != "":
            localFileName = rules[str(submission.subreddit)] + "/" + imageFile
            downloadImage('http:' + match['href'], localFileName)
            count +=1
            return count
        else:
            print "Attempted to download null-string image filename. Weird issue. Skipping file."
            print "Already attempting to force blog layout, not sure why this would still happen."
    return count
def saveImgurSingle(submission, rules):
    """
    This code comes directly from:
    http://inventwithpython.com/blog/2013/09/30/downloading-imgur-posts-linked-from-reddit-with-python/
    All credit to original author. I didn't find it until I was half done with this project,
    but he mostly already solved the problem I was trying to solve here so it made sense to use
    some of that code. I also learned a lot about BeautifulSoup by studying that example, so thanks.
    """
    print "Downloading imgur single: " + str(submission)

    if not os.path.isdir(rules[str(submission.subreddit)]):
        os.makedirs(rules[str(submission.subreddit)])
        print "Directory did not exist, created it..."

    try:
        htmlSource = requests.get(submission.url).text # download the image's page
        soup = BeautifulSoup(htmlSource)
        #print soup.select('.image img')[0]['src']
        imageUrl = soup.select('.image img')[0]['src']
        if imageUrl.startswith('//'):
            # if no schema is supplied in the url, prepend 'http:' to it
            imageUrl = 'http:' + imageUrl
        imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]

        if '?' in imageUrl:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
        else:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:]

        localFileName = rules[str(submission.subreddit)] + "/" + imageFile
        downloadImage(imageUrl, localFileName)
        return 1
    except IndexError:
        print "Something went wrong downloading this single. (IndexError)"
        return 0

def menu():
    print '(1) Make a new rule'
    print '(2) Delete a rule'
    print '(3) List all existing rules'
    print '(4) Save all reddit saved images according to rules'
    print '(5) Exit'

    choice = int(raw_input('Enter the number of your selection: '))

    if choice == 1:
        makeRule()
    elif choice == 2:
        deleteRule()
    elif choice == 3:
        listRules()
    elif choice == 4:
        save()
    elif choice == 5:
        exit()
    else:
        print 'Invalid choice'




while 1:
    os.system('cls' if os.name == 'nt' else 'clear')
    menu()









