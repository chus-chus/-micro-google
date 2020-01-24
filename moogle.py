
import pickle
import urllib.request
import time
from bs4 import BeautifulSoup
import unicodedata
import util
from collections import deque
import networkx as nx

# ============================================================================
#                                AUTHORS
# ============================================================================

# Returns a string with the name of the authors of the work.


def authors():
    return "Cristina Aguilera, Jesus Antonanzas"

# ============================================================================
#                                 STORE
# ============================================================================

# From a database and a file, saves the database in the file.


def store(db, filename):
    with open(filename, "wb") as f:
        print("store", filename)
        pickle.dump(db, f)
        print("done")

# ==============================================================================
#                                 CRAWLER
# ==============================================================================

# ----------------------------- Crawler ----------------------------------

# Performs all the actions required to fill the database (crawl).


def crawler(url, maxdist):
    database = dict()
    visited = set()
    Graph = nx.MultiDiGraph()
    Graph.add_node(url)
    print("Crawling...")
    start = time.time()
    errors = bfs(url, maxdist, database, visited, Graph)
    end = time.time()
    runtime = end - start
    pageRank(Graph, database)
    stats(url, maxdist, database, visited, runtime, errors)
    return database


# ----------------------------- Pagerank ---------------------------------

# Creates the Page Rank score for all pages in the Graph and updates the
# database.

def pageRank(Graph, database):
    pr = nx.pagerank_scipy(Graph)
    for word in database:
        for url in database[word]:
            url[0] = pr[url[4]]

# ------------------------------- Stats ----------------------------------

# Prints information about the crawling process.


def stats(url, maxdist, database, visited, runtime, errors):
    print("- Crawling and parsing done starting from '{}'".format(url),
          "up to maxdist {} in {} s.".format(maxdist, round(runtime, 3)))
    print("- Number of exceptions handled:", errors)
    print("- Number of (different) urls visited:", len(visited))
    print("- Number of (different) words saved:", len(database))

# --------------------------------- BFS ----------------------------------

# Performs  an interative BFS starting from "url" and returns a database
# filled.


def bfs(url, maxdist, database, visited, Graph):
    queue = deque([[url, maxdist]])
    link_crawl = url
    errors = 0
    while queue:
        page = queue.popleft()
        link_crawl, dist_crawl = page[0], page[1]
        if link_crawl not in visited:
            visited.add(link_crawl)
            try:
                soup, text, title = soupify(link_crawl)
                parse(link_crawl, text, title, database)
                if dist_crawl > 0:
                    for link in soup.find_all('a', href=True):
                        link = urllib.parse.urljoin(url, link.get("href"))
                        Graph.add_edge(link_crawl, link)
                        if link not in visited:
                            queue.append([link, dist_crawl - 1])
            except BaseException:
                errors = errors + 1
                pass
    return errors

# Transforms a url address into a soup object. Returns the latter, its text and
# title, respectively.


def soupify(url):
    response = urllib.request.urlopen(url)
    page = response.read()
    soup = BeautifulSoup(page, "html.parser")
    text = util.clean_words(soup.get_text())
    title = util.clean_words(soup.title.string)
    return soup, text, title

# -------------------------------- Parse ---------------------------------

# Fills the database with all necessary information from one URL.


def parse(url, text, title, db):
    text_list = text.split()
    text_lenght = len(text_list)
    for i in range(text_lenght):
        if not text_list[i] in db:
            db[text_list[i]] = []
        lst = create_info_word(text_list, i, text_lenght, title, url)
        db[text_list[i]].append(lst)

# Parsing algorithm, append the information into the database depending on the
# position of the word it is visiting.


def create_info_word(text_list, i, text_lenght, title, url):
    if i == 0:
        prev = ""
        next = text_list[i + 1]
    elif i == text_lenght - 1:
        prev = text_list[i - 1]
        next = ""
    else:
        prev = text_list[i - 1]
        next = text_list[i + 1]
    return [100, prev, next, title, url]

# ============================================================================
#                               LOAD
# ============================================================================

# Reads an object from file filename and returns it.


def load(filename):
    with open(filename, "rb") as f:
        print("load", filename)
        database = pickle.load(f)
        print("done")
        return database

# ============================================================================
#                               ANSWER
# ============================================================================

# -------------------------------- Answer --------------------------------

# Key to sort by scores when returning the final URL list.


def useScore(elem):
    return -elem["score"]

# Searches for a given query in the database and returns all the pages where
# the whole query can be found.


def answer(database, query):
    try:
        if len(query.split()) == 1:
            list = search_word(database, query)
        else:
            list = search_sentence(database, query)
    except BaseException:
        return []
    list.sort(key=useScore)
    return list

# ----------------------- Search one word query --------------------------

# Searches for the URLS where a given word appears.


def search_word(database, query):
    list = []
    links = set()
    for link_list in database[query]:
        url = link_list[4]
        if url not in links:
            links.add(url)
            title = link_list[3]
            score = link_list[0]
            info = {
                "title": title,
                "url": url,
                "score": score
            }
            list.append(info)
    return list

# ---------------------- Search a sentence query -------------------------

# Returns all links that conatin exactly the given sentence from the query.


def search_sentence(database, query):
    list = []
    coincidences = trigram_search(database, query)
    for link_list in coincidences:
        info = create_answer(link_list)
        list.append(info)
    return list

# Peforms an algortihm based on trigrams, looking at the previous and next
# words in order to find the sentence.


def trigram_search(database, query):
    to_search = query.split()
    n = len(to_search)
    coincidences = set()
    for i in range(n - 1):
        word = to_search[i]
        map_entry = database[word]
        if i == 0:
            for link_list in map_entry:
                if link_list[2] == to_search[1]:
                    coincidences.add(
                        (link_list[0], link_list[3], link_list[4]))
        elif i == n - 1:
            coincidences_aux = set()
            for link_list in map_entry:
                if link_list[1] == to_search[i - 1]:
                    coincidences_aux.add(
                        (link_list[0], link_list[3], link_list[4]))
            coincidences = coincidences & coincidences_aux
        else:
            coincidences_aux = set()
            for link_list in map_entry:
                if link_list[1] == to_search[i - \
                    1] and link_list[2] == to_search[i + 1]:
                    coincidences_aux.add(
                        (link_list[0], link_list[3], link_list[4]))
            coincidences = coincidences & coincidences_aux
    return coincidences

# Collects necessary information for the answer.


def create_answer(link_list):
    score = link_list[0]
    title = link_list[1]
    url = link_list[2]
    info = {"title": title, "url": url, "score": score}
    return info
