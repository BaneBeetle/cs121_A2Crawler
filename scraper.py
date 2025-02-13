import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scraper(url, resp):
    ''' Parses the response and extracts valid URLs from downloaded content'''
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """ Extracts hyperlinks from the content of the given Response object
        Arguments:
            url (str): The URL that was used to fetch the page.
            resp: The response object containing status(resp.status), error(resp.error), and raw content.
        Returns:
            list: A list of extracted hyperlinks as strings
    """

    # transform relative to absolute urls
    # remove url fragments
    # exceptions


    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.

    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!


    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if resp.status != 200: # Check if it was successful
        print("Skibidi error")
        print(resp.error)
        return list()

    content = resp.raw_response.content

    scraped_hyperlinks = []

    parser = BeautifulSoup(content, "html.parser")

    hyperlinks = []
    for tags in parser.find_all('a', href=True):
        full_url = urljoin(url, tags['href']) # turns relative to absolute urls
        hyperlinks.append(urldefrag(full_url)) # defrags url
    
    #print(hyperlinks)
    return hyperlinks

def is_valid(url):
    """
    Decide whether to crawl this url or not.
    :param url: the url (string)
    :return bool: True if the URL is valid for crawling, False otherwise.
    """
    # There are already some conditions that return False.
    # steps?
    #
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

#running list of things to avoid:
# wics
