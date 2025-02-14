import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from simhash import Simhash # implement Simhash to combat similar webs like doku


visited = set()


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
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
        print("Skibidi error")
        print(resp.error)
        return list()

    content = resp.raw_response.content
    scraped_hyperlinks = []
    parser = BeautifulSoup(content, "html.parser")

    ### SIMHASH ###
    text = parser.get_text().lower()
    current_simhash_value = Simhash(text.split()).value

    # Check if we have seen this before
    for seen in visited: # Loop thru the set that contains all pages we have seen
        distance = current_simhash_value.distance(Simhash(seen)) # If distance is too low, that means it is too similar.
        if distance <= 3: # Example of too similar is dokus.
            print(f"Too similar, skipping {resp.url}.")
            return [] # Return empty list to not add any new links from here

    ### Add new links ###
    hyperlinks = []
    for tags in parser.find_all('a', href=True):
        full_url = urljoin(url, tags['href'])

        # TODO: Implement fragmentation remover
        hyperlinks.append(full_url)
    
    #print(hyperlinks)
    return hyperlinks

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
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
