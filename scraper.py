import re
import nltk
from nltk.corpus import words
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from simhash import Simhash # implement Simhash to combat similar webs like doku
from urllib.parse import urldefrag
from collections import Counter # Better than dictionary


### DECLARE GLOBALS ###
visited = set() # contains simhashes, used for content
visited_urls = set() # contains all the urls we have visited. For unique pages, we will just use the len function on this
seen1 = set() #keep track of what we have seen and visited so we never add them to the queue ever again
common_words = Counter() # will contain the frequency of words
global_max = 0 # Initiate max to see which url has the most words
ics_domains = {} # Keep track of subdomains in ics.uci.edu

nltk.download('words')
word_list = words.words()

stop_words = (
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
) # STOP WORDS we will not count as per spec.

def is_actual_word(word):
  return word.lower() in word_list

def write_top50_file(filename="top50_words.txt:"):
    '''Writing top 50 words to a txt file so we can use it for the report.'''
    with open(filename, "w") as f:
        for word, count in common_words.most_common(50):
            f.write(f"{word}: {count}\n")

def write_uniqueurls_count(filename = "unique_url_count.txt"):
    '''Writing unique url count to a file to use for report'''
    with open(filename, "w") as f:
        f.write(f"{len(visited_urls)}\n")

def write_new_largest(specific_url, filename = "largest_url.txt"):
    '''Writing largest url to a file to use for report'''
    with open(filename, "w") as f:
        f.write(f"{specific_url}\n")

def write_subdomain(filename = "ics_subdomain.txt"):
    '''Write subs'''
    with open(filename, "w") as f:
        for key, value in ics_domains.items():
            f.write(f"{key}, {value}\n")

    
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

    '''
    ### Redirection check? ###
    final_url = resp.raw_response
    if final_url != url:
        print("Redirection detected")
        visited_urls.add(final_url)
        url = final_url
    '''
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

    global seen1

    ### EXTRACT LOWERCASE TEXT, UPDATE MOST FREQUENT WORDS ### 
    text = parser.get_text().lower()
    words = re.findall(r'\w+', text)

    current_word_amt = len(words)

    ### IF WORDCOUNT LESS THAN 20, DEAD PAGE ###
    if current_word_amt < 20:
        print("Low information")
        return [] # DEAD PAGE

    
    ### SIMHASH ###
    current_simhash = Simhash(text.split())
    current_simhash_value = current_simhash.value

    # Check if we have seen this before
    for seen in visited: # Loop thru the set that contains all pages we have seen
        distance = current_simhash.distance(Simhash(seen)) # If distance is too low, that means it is too similar.
        if distance <= 10:
            print(f"Too similar, skipping {resp.url}.")
            seen1.add(resp.url)
            return [] # Return empty list to not add any new links from here
    visited.add(current_simhash_value)

    ### OBTAIN WORD COUNT, SEE IF ITS LARGEST ###
    global global_max
    if current_word_amt > global_max:
        global_max = current_word_amt
        write_new_largest(url)

    for word in words:
        if (word not in stop_words) and (len(word) > 2) and (is_actual_word(word)):
            common_words[word] += 1

    ### UPDATE TOP50 WORDS FILE ###
    write_top50_file()

    
    ### Add new links ###
    hyperlinks = []
    for tags in parser.find_all('a', href=True):
        full_url = urldefrag(urljoin(url, tags['href']))[0]

        # TODO: Implement fragmentation remover
        if (full_url not in visited_urls) and (is_valid(full_url) and (full_url not in seen1)): # Have we visited it before? If not, add it to the return list
            hyperlinks.append(full_url)
            visited_urls.add(full_url)
            seen1.add(full_url)
            parsed_full = urlparse(full_url)

            if parsed_full.netloc.endswith("ics.uci.edu"):
                # Use a canonical representation: force an "http://" prefix regardless of original scheme.
                subdomain = "http://" + parsed_full.netloc
                ics_domains[subdomain] = ics_domains.get(subdomain, 0) + 1 # <-- need this cuz dictionary may tweak out if value didnt exist beforehand
                write_subdomain() # Update the txt file


    ### UPDATE URL COUNT ###
    write_uniqueurls_count()

    return hyperlinks # maybe make it a set so it removes duplicates? -- RESPONSE: idk default code made it a lst so i just didnt change it lol

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
        path_lower = parsed.path.lower()
        query_lower = parsed.query.lower()
        domains = (
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu",
        ) # Tuple containing domains we ONLY want to crawl
        domain_trap_words = ["plrg", "password", "swiki"]

        for trap in domain_trap_words:
            if trap in parsed.netloc.lower():
                return False

        if parsed.scheme not in set(["http", "https"]):
            return False

        if not any(parsed.netloc.endswith(domain) for domain in domains):
            return False

        ### Check if its a common trap thing ###

        common_trap_words = ["calendar", "session", "token", "cgi-bin", "login", "logout", "ml", "datasets", "dataset", "events", "event", "week", "weeks", "schedule", "doku", "virtual_environments", "date"] # Common trap words given by GPT. ADDED: datasets and dataset to avoid too large files
        

        for traps in common_trap_words:
            if traps in path_lower:
                return False
        

        if "doku.php" in path_lower:
            return False
        if "doku" in path_lower:
            return False
        ### Trap in Query ###
        query_trap = ["tab_files", "tab_details", "do=media"]
        for trap in query_trap:
            if trap in query_lower:
                return False

        ### Make sure I dont go thru gitlab commits ###
        if "/-/commits" in parsed.path.lower():
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|jpg|jpeg|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|mpg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|asm|vb|sql" # Added more code ends
            + r"|epub|dll|cnf|tgz|sha1|rs|swift|kt|kts|scala|r|lua|sh|bat|ps1|hs|erl|ex|exs|clj|cljs|cljc|f|f90|f95"
            + r"|thmx|mso|arff|rtf|jar|csv|py|ipynb|hpp|cpp|php|ts|c|cc|cxx|cs|rb|pl|pm|go"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

#running list of things to avoid
# wics
# calendars -- RESPONSE: Not sure how to check this. Most likely observe its contents and find a pattern to filter it out
# i think some things are up to us we just have to defend our choices

#things to do????:
# i dont think we make sure things are only in the ics domain -- RESPONSE: Domain tuple may solve
# making sure we dont crawl stuff we alr did, i think frontier maybe does it -- RESPONSE: Hopefully the line of code checking if its in the visited_url set solves this

#     maintain list of visted urls, makes it so crawler can detect infinite loops -- RESPONSE: created set for this


# idk how we should like log stuff so we can do the report and get stats like length etc -- RESPONSE: Most likely accessing it directly with the contents on the page (content = resp.raw_response.content)
