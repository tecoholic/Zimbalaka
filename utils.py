import os
import sys
import urllib
import urllib2
import hashlib
import tempfile
import shutil
from subprocess import call
from pyquery import PyQuery as pq


dloc = tempfile.mkdtemp()
baseurl = "http://en.wikipedia.org"

def download_image(url):
    """Download the image from the given url and add it to the assets"""
    url = "http:"+url
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Zimbalaka/1.0 based on OpenZim')]
    # print "Downloading .. ", url
    infile = opener.open(url)
    parts = url.strip().split("/")
    ext = url.strip().split(".")[-1]
    # noticed strange queries so hardcoding png as extension
    if len(ext) > 3:
        ext = 'png'
    m = hashlib.md5()
    m.update(parts[-1].encode("utf-8"))
    md5name = m.hexdigest()[0:8]
    filename = os.path.join("assets", md5name + "." + ext)
    f = open(os.path.join(dloc,filename), 'w')
    f.write(infile.read())
    f.close()
    return filename

def clean_page(html):
    """Cleans the html read from the url opener"""
    doc = pq(html)
    #To remove other sections, add the class or id of the section below
    sections="""#mw-page-base,#mw-head-base,#top,#siteNotice,.mw-indicators,
    #mw-navigation,#footer,script,.suggestions,#siteSub,#contentSub,#jump-to-nav,
    .hatnote,.reference,.ambox,.portal,#Notes,.reflist,#References,.refbegin,
    #printfooter,#catlinks,.visualClear,#mw-indicator-pp-default,#toc,.mw-editsection,
    .navbox,.sistersitebox,link,#coordinates,.references,sup.no#print,.stub
    """
    seclist = sections.split(",")
    for sec in seclist:
        doc.remove(sec.strip())
    # add the styles
    if not os.path.isfile(os.path.join(dloc,"assets","style1.css")):
        shutil.copytree("assets", dloc+'/assets') # copt the stylesheets to the tmp folder
    doc('head').append('<link rel="stylesheet" href="assets/style1.css" type="text/css">')
    doc('head').append('<link rel="stylesheet" href="assets/style2.css" type="text/css">')
    # place the images
    for image in doc('img'):
        localfile = download_image(pq(image).attr('src'))
        pq(image).attr('src', localfile)
    # fix the links
    for link in doc('a'):
        absolute = baseurl + pq(link).attr('href')
        pq(link).attr('href', absolute)
    return doc.html().encode("utf-8")

def download_file(title):
    """Downloads the file from wikipedia with all the associated files"""
    url = baseurl + '/wiki/' + urllib.quote( title.encode('utf-8') )
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Zimbalaka/1.0 based on OpenZim')]
    #print "Opening .. ", url
    infile = opener.open(url)
    page = infile.read()
    # clean the page now
    page = clean_page(page)
    htmlname = os.path.join(dloc, title + ".html")
    f = open(htmlname, 'w')
    f.write(page)
    f.close()
    return htmlname

def zimit(titles):
    """Prepare a zim file for the given title using zimwriterfs command line tool

    Usage: zimwriterfs [mandatory arguments] [optional arguments] HTML_DIRECTORY ZIM_FILE

     Mandatory arguments:
     -w, --welcome      path of default/main HTML page. The path must be relative to HTML_DIRECTORY.
     -f, --favicon      path of ZIM file favicon. The path must be relative to HTML_DIRECTORY and the image a 48x48 PNG.
     -l, --language     language code of the content in ISO639-3
     -t, --title        title of the ZIM file
     -d, --description  short description of the content
     -c, --creator      creator(s) of the content
     -p, --publisher    creator of the ZIM file itself

    HTML_DIRECTORY      is the path of the directory containing the HTML pages you want to put in the ZIM file,
    ZIM_FILE        is the path of the ZIM file you want to obtain.

    Example:
        zimwriterfs --welcome=index.html --favicon=m/favicon.png --language=fra --title=foobar --description=mydescription \
                --creator=Wikipedia --publisher=Kiwix ./my_project_html_directory my_project.zim
    """
    print 'zimit has been called'
    index = pq('''<html><head>
        <title>WelcomeePage</title>
        </head>
        <body>
                <ol>
                </ol>
        </body>
        </html>''')
    for title in titles.split('\n'):
        htmlfile = download_file(title)
        pq(index('ol')).append('<li><a href="'+os.path.split(htmlfile)[1]+'">'+title+"</a></li>")
    f = open(os.path.join(dloc,'index.html'), 'w')
    f.write(index.html())
    f.close()
    w = "index.html" # change this when packaging more than 1 file
    f = os.path.join("assets","wiki_w.png")
    l = "en" # change this when multiple languages are supported
    t = title
    d = "'Wikipedia article on " + title +"'"
    c = "'Wikipedia Contributors'"
    p = "'Zimbalaka 1.0'"
    directory = dloc
    zimfile = os.path.join(dloc, title+".zim")
    command = "/usr/local/bin/zimwriterfs -w "+w+" -f "+f+" -l "+l+" -t "+t+" -d "+d+" -c "+c+" -p "+p+" "+directory+" "+zimfile
    call(command, shell=True)
    #print zimfile
    return zimfile


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "insufficient params"
    else:
        zimit(sys.argv[1])
