import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from simhash import Simhash # implement Simhash to combat similar webs like doku
from urllib.parse import urldefrag

visited = set() # contains simhashes, used for content
visited_urls = set()

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


    ### ERROR CHECKING ###
    if resp.status != 200: # Check if it was successful
        print("Skibidi error status code {resp.status}")
        print(resp.error)
        return list()

    if not resp.raw_response or not resp.raw_response.content: # check if there is content to parse
        print("No content to parse")
        return list()

    content = resp.raw_response.content
    scraped_hyperlinks = []
    parser = BeautifulSoup(content, "html.parser")

    ### SIMHASH ###
    text = parser.get_text().lower()

    current_simhash = Simhash(text.split())
    current_simhash_value = current_simhash.value

    # Check if we have seen this before
    for seen in visited: # Loop thru the set that contains all pages we have seen
        distance = current_simhash.distance(Simhash(seen)) # If distance is too low, that means it is too similar.
        #print("CURRENT DISTANCE:", distance)
        if distance <= 3: # Example of too similar is dokus.
            print(f"Too similar, skipping {resp.url}.")
            return [] # Return empty list to not add any new links from here
    visited.add(current_simhash_value)

    ### Add new links ###
    hyperlinks = []
    for tags in parser.find_all('a', href=True):
        full_url = urldefrag(urljoin(url, tags['href']))

        # TODO: Implement fragmentation remover
        if full_url not in visited_urls:
            hyperlinks.append(full_url)
            visited_urls.add(full_url)
    

    return hyperlinks # maybe make it a set so it removes duplicates?

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

        domains = (
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu",
        )


        if parsed.scheme not in set(["http", "https"]):
            return False

        if not any(parsed.netloc.endswith(domain) for domain in domains):
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

#running list of things to avoid
# wics
# calendars
# i think some things are up to us we just have to defend our choices

#things to do????:
# i dont think we make sure things are only in the ics domain
# making sure we dont crawl stuff we alr did, i think frontier maybe does it
#     maintain list of visted urls, makes it so crawler can detect infinite loops
# idk how we should like log stuff so we can do the report and get stats like length etc
