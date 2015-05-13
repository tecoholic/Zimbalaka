import os
import sys
import urllib
import urllib2
import hashlib
import tempfile
import shutil
import re
import codecs
from subprocess import call
from pyquery import PyQuery as pq

from zimbalaka.default_settings import assets, static, zimwriterfs

def download_image(dloc, url, baseurl):
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
    with open(os.path.join(dloc,filename), 'w') as f:
        f.write(infile.read())
    return filename

def clean_page(dloc, html, baseurl):
    """Cleans the html read from the url opener"""
    doc = pq(html)
    #To remove other sections, add the class or id of the section below
    sections="""#mw-page-base,#mw-head-base,#top,#siteNotice,.mw-indicators,
    #mw-navigation,#footer,script,.suggestions,#siteSub,#contentSub,#jump-to-nav,
    .hatnote,.reference,.ambox,.portal,#Notes,.reflist,#References,.refbegin,
    #printfooter,#catlinks,.visualClear,#mw-indicator-pp-default,#toc,.mw-editsection,
    .navbox,.sistersitebox,link,#coordinates,.references,sup.no#print,.stub,#stub,
    .metadata
    """
    seclist = sections.split(",")
    for sec in seclist:
        doc.remove(sec.strip())
    # add the styles
    if not os.path.isfile(os.path.join(dloc,"assets","style1.css")):
        shutil.copytree(assets, os.path.join( dloc,'assets') ) # copt the stylesheets to the tmp folder
    doc('head').append('<link rel="stylesheet" href="assets/style1.css" type="text/css">')
    doc('head').append('<link rel="stylesheet" href="assets/style2.css" type="text/css">')
    # place the images
    for image in doc('img'):
        localfile = download_image(dloc, pq(image).attr('src'), baseurl)
        pq(image).attr('src', localfile)
    # fix the links
    for link in doc('a'):
        absolute = baseurl + pq(link).attr('href')
        pq(link).attr('href', absolute)
    return doc.html().encode("utf-8")

def download_file(dloc, title, baseurl):
    """Downloads the file from wikipedia with all the associated files"""
    url = baseurl + '/wiki/' + urllib.quote( title.encode('utf-8') )
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Zimbalaka/1.0 based on OpenZim')]
    print "Opening .. ", url
    infile = opener.open(url)
    page = infile.read()
    # clean the page now
    page = clean_page(dloc, page, baseurl)
    htmlname = os.path.join(dloc, title + ".html")
    with open(htmlname, 'w') as f:
        f.write(page)
    return htmlname

def zimit(title, articles, lang, logger):
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
    dloc = tempfile.mkdtemp()
    baseurl = 'http://{0}.wikipedia.org'.format(lang)
    print 'zimit has been called'
    index = pq(u'''
        <!DOCTYPE html>
        <html lang="{0}">
        <head>
                <meta charset="UTF-8">
                <title>{1}</title>
        </head>
        <body>
                <ol></ol>
        </body>
        </html>
        '''.format(lang, title))

    # download the list of articles
    articlist = articles.strip().split('\n')
    for i, article in enumerate(articlist):
        if article:
            # The redis logger to log the article and the count
            logger.log(article.strip())
            logger.count(i*100/len(articlist))
            try:
                htmlfile = download_file(dloc, article.strip(), baseurl)
                link = u'<li><a href="{0}">{1}</a></li>'.format(os.path.split(htmlfile)[1], article.strip())
                print link
                pq(index(u'ol')).append(link)
            except (urllib2.URLError, urllib2.HTTPError) as e:
                logger.log(str(e))
                print e
                shutil.rmtree(dloc)
                return False
    with codecs.open(os.path.join(dloc,'index.html'), mode='w', encoding='utf-8') as f:
        f.write(index.html())

    logger.log("Creating your Zim file")
    # build the parameters for zimwriterfs
    w = u"index.html" # change this when packaging more than 1 file
    f = os.path.join(u"assets",u"wiki_w.png")
    l = u"en" # change this when multiple languages are supported
    # Sanity check title
    t = re.sub(u'[\+\-\.\,\!\@\#\$\%\^\&\*\(\)\;\\\/\|\<\>\"\'\{\}\[\]\?\:\=\s]',u'_',title)
    d = u"'Wikipedia article on " + title +"'"
    c = u"'Wikipedia Contributors'"
    p = u"'Zimbalaka 1.0'"
    directory = dloc
    zimfile = os.path.join(dloc, "output.zim")
    command = u"{0} -w {1} -f {2} -l {3} -t {4} -d {5} -c {6} -p {7} {8} {9}".format(
                     zimwriterfs, w, f, l, t, d, c, p, directory, zimfile )
    call(command, shell=True)
    newzim = os.path.join( static, 'zim', "output.zim")
    shutil.copy(zimfile, newzim)
    print 'Removing tmp dir ', dloc
    # shutil.rmtree(dloc)
    print newzim
    return newzim


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "insufficient params"
    else:
        zimit(sys.argv[1], sys.argv[2])
