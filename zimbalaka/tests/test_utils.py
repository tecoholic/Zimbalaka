from zimbalaka.utils import articles_of_cat

def test_articlesofcat():
    """test to ensure that all the articles under a category are fetched byi
    articles_of_cat function
    
    Test input should be manually modifies before running. Depends on
    external resources.
    """
    url = 'https://en.wikipedia.org'
    cat = 'Category:Tamil Nadu'
    assert len(articles_of_cat(url,cat)) == 11
    cat = 'Tamil Nadu'
    assert len(articles_of_cat(url,cat)) == 11
    cat = 'Inavlid Category With 0'
    assert len(articles_of_cat(url,cat)) == 0



