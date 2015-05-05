import sys
import urllib
import urllib2
from pyquery import PyQuery as pq


dloc = "downloads/"
baseurl = "http://en.wikipedia.org/wiki/"

def clean_page(html):
    """Cleans the html read from the url opener"""
    doc = pq(html)
    #To remove other sections, add the class or id of the section below
    sections="""#mw-page-base,#mw-head-base,#top,#siteNotice,.mw-indicators,
    #mw-navigation,#footer,script,.suggestions,#siteSub,#contentSub,#jump-to-nav,
    .hatnote,.reference,.ambox,.portal,#Notes,.reflist,#References,.refbegin,
    .printfooter,#catlinks,.visualClear,#mw-indicator-pp-default,#toc,.mw-editsection,
    .navbox,.sistersitebox,link,#coordinates
    """
    seclist = sections.split(",")
    for sec in seclist:
        doc.remove(sec.strip())
    # add the styles
    doc('head').append('<link rel="stylesheet" href="assets/style1.css" type="text/css">')
    doc('head').append('<link rel="stylesheet" href="assets/style2.css" type="text/css">')
    return doc.html().encode("utf-8")

def download_file(title):
    """Downloads the file from wikipedia with all the associated files"""
    url = baseurl + urllib.quote( title.encode('utf-8') )
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Zimbalaka/1.0 based on OpenZim')]
    infile = opener.open(url)
    page = infile.read()
    # clean the page now
    page = clean_page(page)
    htmlname = dloc + title + ".html"
    f = open(htmlname, 'w')
    f.write(page)
    f.close()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "insufficient params"
    else:
        download_file(sys.argv[1])
