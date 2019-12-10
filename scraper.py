from sys import argv
from sys import exit as sysexit
import requests
from PIL import Image
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud

#list of html tags to ignore when grabbing text
tag_blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    'style',
]

#list of words to exempt from the final list, namely javascript keywords that are unlikely to show up in great frequency in human writing
word_blacklist = [
    'var',
    'null',
]

#list of acceptable filetypes to export to
filetypes = [
    '.png',
    '.jpg',
    '.pdf',
]

def main():

    #make sure user entered a link and a filename
    check_args()

    #get url from command line argument
    url = argv[1].strip()

    #make sure url has proper format
    url = check_url(url)

    #initiate http session
    r = requests.session()

    #get html of the url's page
    try:
        raw_html = r.get(url).text
    except:
        try:
            url = make_https(url)
            raw_html = r.get(url).text
        except:
            print("unable to fetch HTML")
            exit()

    #create BeautifulSoup object 
    formatted_html = bs(raw_html, "html.parser")

    #find all text within the BeautifulSoup object 
    data = formatted_html.find_all(text=True)

    #find words to use for wordcloud
    word_list = find_real_words(data)

    #visualize data and create wordcloud
    create_visualization(word_list)

def find_real_words(data):
    """gets words from the raw BeautifulSoup object, ignoring whitespace and non-english characters"""

    words = ""

    for line in data:
        if line.parent not in tag_blacklist and line.parent.parent not in tag_blacklist:
            for word in line.split():
                word = word.strip()
                word = word.rstrip(',')
                word = word.rstrip('.')
                if len(word) < 20 and not word.isspace() and word.isalpha() and word not in word_blacklist:
                    words += " "
                    words += word
    return(words)

def create_visualization(word_list):
    """creates the wordcloud and attempts to display it with matplotlib, also saves wordcloud to a local file"""

    wordcloud = WordCloud(background_color="white", scale=10, min_font_size=3, collocations=False).generate(word_list)

    try:
        wordcloud.to_file("img/" + argv[2].strip())
        print("successfully wrote image as " + argv[2].strip())
    except:
        print("unable to write image to file, exiting")
        sysexit()
    
    img = Image.open("img/" + argv[2].strip())
    img.show()

def check_url(url):
    """if the url doesn't start with http:// or https://, adds http:// at the start."""

    if not url[0:8] == "https://" and not url[0:7] == "http://":
        fixed_url = "http://" + url
        return(fixed_url)
    else:
        return(url)

def make_https(url):
    """to be used in conjunction with check_url, replaces http:// with https://. ONLY USE WITH URLS THAT ARE KNOWN TO START WITH http://"""

    new_url = "https://" + url[7:]

def check_args():
    """checks if the user properly gave arguments"""

    if(argv[1] == "help"):
        print("usage: py scraper.py [WEBSITE LINK] [FILENAME]")
        print("links that start with http:// or https:// are preferred.")
        print("filenames must end in .pdf, .png, or .jpg.")
        sysexit()

    #if there are no arguments provided 
    if(len(argv) == 1):
        print("missing arguments, please enter a link and a filename")
        sysexit()
    #if there is only a link provided
    elif(len(argv) == 2):
        print("missing filename, exiting")
        sysexit()
    #if the filename given doesn't have an accepted filetype
    elif(argv[2][-4:] not in filetypes):
        print("filename must have a proper extension, exiting")
        sysexit()
    
if __name__ == "__main__": 
    main()
