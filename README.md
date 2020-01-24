# µoogle, a *Data Science and Engineering* project
### Politechnic University of Catalonia
#### Aguilera Gonzalez, Cristina | Antoñanzas Acero, Jesus M.

## What, Why & How

This is *µoogle*, a "micro-Google". By that, we mean a search engine comprising of a small
database, scraped from whatever url you want and its adjacent urls up to a
certain level, from which you can search either words or whole sentences.

This project has been a practical application of the previously learned knowledge on Graphs and Data Structures at UPC, and by no means it is intended to behave as a commonly used Web Search Engine (*i.e. Google, Mozilla Firefox*).

This project's backbone consists of the following algorithms:
- B.F.S. (*Breadth First Search*)
- Trigram parsing

Which in fact allow everything to work: the former to "explore" urls, and the latter to search a query correctly.

## Functionality

Here is a small summary of the code implemented and how it works:

- First off, receive an instruction to crawl and do so using our "crawler", which performs a BFS from the url one might have given it and parses every webpage contained in it up to a certain "maxdist".

- At each parsing, save some content in particular on our database using a trigram structure for words --*previous* and *next*.

- Receive an "answer" call from the search bar and navigate through the database while taking advantage of the aforementioned trigram structure.

- Lastly, return all *urls* containing the query.

## Algorithms, explained

### Crawler

Performs all the actions required to fill the database and returns it. Also, gathers some information about the crawling.
Calls two auxiliary functions:

- BFS, which in turn calls "parse"
- Stats


### BFS

Performs an iterative BFS starting from "url" and returns a database filled by the "parse" function.
It also fills the graph used for later sorting URLS.


    Level:            2                   1                   0
     ---------------
    |dc = dist_crawl|
     ---------------

                                                     -> link11 (dc = 0)
                                 -> link1 (dc = 1) --
                               --                    -> link12 (dc = 0)
                url (dc = 2) --
                               --                    -> link21 (dc = 0)
                                 -> link2 (dc = 1) --
                                                     -> link22 (dc = 0)


For the iterative part, we use a queue of pairs, each of them containing the URL to work with sometime next and a "dist_crawl" indicator. This indicator is equal to the original "maxdist" for the first url and equals "maxdist" minus the level we are at for all others. The algorithm won't work links whose "dist_crawl" <= 0.

Also, we keep track of the links we have visited with a set:
If we haven't done so with the link we're currently at, parse it.

By "working a URL", we mean parsing it. That is why BFS calls "parse". Let's see what it does.

### Parse
Fills the database with all necessary information from just one URL. The thought behind it is that we visit every word of our document and call "create_info_word" on it.

**Input parameters**:
  - *url*: url which we'd like to parse.
  - *text*: a list containing all the text from our url.
  - *title*: the title of our webpage.
  - *database*: database to be filled in.

### Create Info Word

Our parsing algorithm. Given a URL, its title, our current position, its text and the length of it, return a list containing all info that will be appended into the database.

The main idea is, knowing the position of the word it is visiting, consider three different cases:

     -> 1
        We're visiting the first word of the document:
        Then, the previous word will be null (save it as an empty string).    

     -> 2
        We're neither at the beginning nor the end of the document:
        Simply save the previous and following words.    

     -> 3
        We're at the end of the document:
        The following position will be null (save it as an empty string).

For example, for each word in the following list:

  *list = ["hi hello bye"]*

we would find in our database (amongst other things):

  - *hi*  
  [  ""        ,    "hello" ]

  - *hello*  
  [  "hi"      ,    "bye"   ]

  - *bye*  
  [  "hello"   ,    ""      ]

that is, in fact, the previous and following words to the one we're visiting: a trigram.

Our database is a map, where each key would be a word from any of
our crawled documents (without repetition). Then, in each key we'll keep a
vector of lists. For each entry there will be a list for every occurrence of a word in
any visited URL, and it will have the following structure:    



      0   |       1       |       2        |        3          |    4
    score | previous word | following word | title of the page |   url

                                                                 (figure 1)





 ### Page Ranking

 Perform a "Page Rank" algorithm from the "Network X" library. First, though,
 one has to build a graph, also thanks Network X. In this case, it is a
 "MultiDiGraph", meaning a graph where one node can have various outbound edges.
 There is another graph type choice one could have chosen: "DiGraph", but
 it would be a mistake, as nodes in that graph cannot have various outbound edges,
 so the pageRank would not be entirely correct.

 Our MultiDiGraph is built when performing the BFS. For each URL contained in
 another one, whether it has visited it before or not, add an edge from the latter
 to the former.

 Once the graph is completely built, we perform the Page Rank algorithm
 ("nx.pagerank_scipy", which is the only one from Network X which supports
 MultiDiGraphs) and update the scores on the pages visited.

### Answer


Searches for a given query in the database previously created and returns all the pages where the whole query (in the correct order) can be found.

Depending on the length of the query (*n*) we have two different cases:

    -> 1  

    If n == 1 (just one word): We only need to take all
    the pages containing that word. Call "Search Word".

    -> 2

    If n > 1 (a sentence): Call "search_sentence".

### Search Word

Called when the user query is just one word.
Searches in the database for
the entry with the query as its key. Then, gather the title, url and score from each of the
link_list returned from searching, and create and return a list of maps with each map having the latter three as keys and entries. Bear in mind that all lists within the map entry will be formatted as shown in *figure 1*.


### Search Sentence

Given a user query with length bigger than 1, returns a list of maps formatted exactly as those returned by "search_word".

Calls two functions:
- trigram parsing
- create_answer

### Trigram Search

Given a database and a sentence, returns a set containing all urls that contain the latter as is, along with their title and score.

We are going to iterate for each word in the query (*query[i]*) and each list
in the map entry with *query[i]* as its key.

For each word in our query, grab the map entry with the word as its key. Then
we are going to differentiate three distinct cases depending on the position
of the current word in the query.  

      i.e.: "the pretty word", we will have a case for "the", another for "word"
      and another for all in between, in this case, just "pretty").

- For the first word, we just need to collect from our map entry the
   "link_lists" which have as the "following word" (*link_list[2]*) the 2nd
   word (*to_search[1]*) from our query. If that happens, add a new list
   containing the score, title and url of the coincident "link_list" to our
   "coincidences" set.

- For all words in between, the procedure is similar, but we are checking
   that the "previous word" and "following word" of the link_list coincide
   with the previous and following words of "to_search[i]"(that is,
   "*to_search[i - 1]*" and "*to_search[i + 1]*"). If that is the case, add a
   new list to an *auxuliar* coincidences set.

- Last case. We just check that the "previous word" coincides with the
   second-to-last word of our query (*to_search[n - 1]*). If that's the case,
   again, add a tuple as before to an *auxiliar* coincidences set.

Now, *how* do we treat the coincidences? First off, before even iterating
over our query, we create the "general" coincidences set. When checking the
first word, if a coincidence happens, the list is going to be added to the
"general" set. Remember: all lists added will just contain a url, a title
and a score. Once that is done, for all other cases we'll do the following:

- Create an empty set ("auxiliar").  

- Search for coincidences as explained above (2nd and 3rd point).
- Coincidences will be added to "auxiliar".  

- Perform an intersection between "auxiliar" and "general", so that
  the only lists remaining will be the ones which happened to contain
  the words from the query (up to where we are in the iteration) in the
  correct order.
  The last point guarantees that when the algorithm finishes, the only tuples
  remaining will be the ones that point to a/an url containing the whole query
  in the correct order.

### Create Answer
Called from "answer"'s second case after having searched for the whole query.

If the set returned from "trigram_search" is not empty, gather the title, url and score from each of the elements of the set and create and return a list of maps with each map having the latter three as keys and entries (*title, url, score*). We know, in fact, where we can
find the score, title and url from each list as saved on our database
(refer to figure 1 and 2 for each case).  
For the first case we don't call "create_answer", because the structure that the returned "link_list" has in the first case is slightly different from the second one.



    Info as saved in the lists contained in the "coincidences" set:

                            0       1      2
                          score | title | url

                                             (figure 2)



### Stats

Collects information about the crawling process such as:

- URL of origin
- Maximum distance
- Execution time
- Error handling
- Number of URLS visited
- Number of different words compiled


### Other functions used and implemented

##### Authors

Returns the name of the authors.

##### Store

Using the "pickle" module, saves the filled database onto the user's filesystem.

##### Load

Using the "pickle" module, loads the database from the user's filesystem.

##### Clean Words

Transform some words so that they can be treated correctly.

##### Soupify

Creates a "soup" object from a URL so it can be treated (get its text and title,
for example).

## Benchmarks

Here are some benchmarking tests.  
Machine: *MacBook Pro late 2014, Intel Core i5 @ 2.6 GHz, 8 Gb RAM.  
Tests performed twice and averaged (although some variables did not change).*

1|
- URL of origin: http://www.foodsubs.com/
        Max Dist                     ->    1        2        3

        Crawling time (m)            ->   0.2      2.9     15.2

        (different) URLS visited     ->   23       225     1173

        (different) words saved      ->  1046      9118    14030

        Database size (MB)           ->  0.135     5.8     18.1  

        Errors handled               ->    1        16      76

A maximum distance level greater than 3 for this URL would be impractical to test on.

2|
- URL of origin: http://www.google.com/
        Max Dist                     ->    1        2

        Crawling time (m)            ->   0.86      17.4

        (different) URLS visited     ->   25        885

        (different) words saved      ->   5387      23504

        Database size (MB)           ->   1.3       33.2

        Errors handled               ->    5        442

We can clearly see an increase in the number of words available with 1 exploring-level less than before. A maximum distance level greater than 2 for this URL would be again take too much time.

3|
- URL of origin: http://www.jutge.org/
        Max Dist                     ->    1        2

        Crawling time (m)            ->   6.2      14.3

        (different) URLS visited     ->   16       2600

        (different) words saved      ->  2997      20747

        Database size (MB)           ->  0.57      29.5

        Errors handled               ->    0       985

### Notes

There has been implemented some basic error handling ("try and except") in order to, for example, skip invalid URLS or not parse uncleanable words.

Also note that our BFS works not just within the domain of the given original
URL, but roams around freely, so a bigger number of visited URLS is expected
than if it were to stick to the given domain.

For this project, the following libraries have been used:

- pickle
- urllib.request
- time
- from bs4 -> BeautifulSoup
- unicodedata
- from collections -> deque
- networkx
