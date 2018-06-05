"""Basic twitter-like application that uses neo4j as a database"""

from uuid import uuid4
from datetime import datetime
from py2neo import Graph, Relationship

GRAPH = Graph(password="password")

def find_one(label, *args):
    """Finds a node given a label and any optional args we want to pass. A
    typical usage would be:
        find_node("User", "handle", "@userhandle")

    Returns None if the node isn't found in the database, or a Node object if
    it is. Note: If multiple nodes match the given criteria, only the first will
    be returned.
    """
    nodes = GRAPH.find(label, *args)
    try:
        return next(nodes)
    except StopIteration:
        return None

def tweet(user, tweet_text):
    """Creates a tweet and attaches it to a user. This is an example to show
    how we can write native cypher queries in Python."""

    # Random unique identifier for each tweet. While tecnically not truly "unique",
    # the odds of getting 2 duplicate values after generating a billion records
    # is about 1 in a quintillion.
    tweet_id = str(uuid4())

    # While technically neo4j provides it's own datetime implementation, bolt
    # (the underlying engine) cannot pass those datetime objects back to python,
    # so instead we store them as a string.
    tweet_datetime = datetime.now().isoformat()
    query = """
        MATCH (u:User {handle: {u_handle}})
        CREATE (u)-[:TWEETED]->(t:Tweet {text: {t_text},
                                         tweet_id: {t_id},
                                         num_likes: 0,
                                         tweeted_on: {t_on}})
    """

    # This is just a way to avoid really long function calls. This is essentially
    # GRAPH.run(query, handle=user, text=tweet_text, ...)
    kwargs = {"u_handle": user,
              "t_text": tweet_text,
              "t_id": tweet_id,
              "t_on": tweet_datetime}
    GRAPH.run(query, **kwargs)

    print("Tweet created with id:", tweet_id)
    return tweet_id

def like(user, tweet_id):
    """Creates a "LIKE" relationship between user and a tweet based on
    the user's handle and the tweet's tweet_id field. This is an example on how
    we can use py2neo's built in types and features to avoid writing cypher
    queries. A more 'pythonic' approach.

    Also increments the tweet's num_likes by 1.
    """
    # Tries to match the user node
    user_node = find_one("User", "handle", user)
    if user_node is None:
        print("User:", user, "not found!")
        return

    # Tries to match the tweet node
    tweet_node = find_one("Tweet", "tweet_id", tweet_id)
    if tweet_node is None:
        print("Tweet:", tweet_id, "not found!")
        return

    # Increment the property value
    tweet_node["num_likes"] += 1

    # Add to graph.
    GRAPH.create(Relationship(user_node, "LIKES", tweet_node))

t_id = tweet("@ThePSF", "Python 3 is better than Python 2")
like("@nickj", t_id)
#like("@neo4j", t_id)
