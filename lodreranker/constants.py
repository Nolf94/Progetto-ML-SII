MOVIE = 'movies'
BOOK  = 'books'
MUSIC = 'artists'

# limit the number of API calls to prevent saturating the app's rate limit
FB_FETCH_PAGE_LIMIT = 5

SPARQL_TIMEOUT = 60  # set the query timeout (in seconds)
SPARQL_LIMIT_DEFAULT = 30  # TODO increase dynamically

WIKIDATA = 'https://query.wikidata.org/sparql'
DBPEDIA = 'http://dbpedia.org/sparql'
SUPPORTED_LODS = [WIKIDATA, DBPEDIA]

CLUSTERING_EPS = 0.62

METHODS = ['clustering', 'summarize', 'outdegree']

COLDSTART_MIN_CHOICES = 5