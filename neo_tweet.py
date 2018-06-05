"""Basic twitter-like application that uses neo4j as a database"""

from uuid import uuid4
from datetime import datetime
from py2neo import Graph, Node, Relationship

GRAPH = Graph(password="password")

def find_one(label, *args):
    """Finds a node given a label and any optional args we want to pass. A
    typical usage would be:
        find_node("User", "handle", "@userhandle")

    Returns None if the node isn't found in the database, or a Node object if
    it is.

    NOTE: If multiple nodes match the given criteria, only the first will
    be returned.
    """

    nodes = GRAPH.find(label, *args)
    try:
        return next(nodes)
    except StopIteration:
        return None

def create_user(handle, **kwargs):
    """Attempts to create a user based on a handle and other keyword
    arguments. If the handle is already taken we print a message and return.

    returns: None

    Note: in this implementation twitter handles ARE case-sensitive
    """

    if find_one("User", "handle", handle) is not None:
        print("Handle", handle, "already taken!")
        return

    user = Node("User", handle=handle, **kwargs)
    GRAPH.create(user)

    print("Created User:", user.get('handle'))

def tweet(user, tweet_text):
    """Creates a tweet and attaches it to a user. This example shows
    how we can write native cypher queries in Python."""

    # Random unique identifier for each tweet. While tecnically not truly "unique",
    # the odds of getting a duplicate value after generating 100 trillion records
    # is about 1 in a billion.
    tweet_id = str(uuid4())

    # While technically neo4j provides it's own datetime implementation, bolt
    # (the underlying engine) cannot pass those datetime objects back to python,
    # so instead we store them as a string.
    tweet_datetime = datetime.now().isoformat()

    # The query is stored as a multi-line string.
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

def follow(follower, followed):
    """Similar to the 'like' function, this provides a way for users to follow each other."""
    follower_node = find_one("User", "handle", follower)
    if follower_node is None:
        print("User:", follower, "not found!")

    followed_node = find_one("User", "handle", followed)
    if followed_node is None:
        print("User:", followed, "not found!")

    GRAPH.create(Relationship(follower_node, "FOLLOWS", followed_node))

if __name__ == "__main__":
    create_user("@nickj")
    create_user("@nickj", **{"bio": "Cool Kid", "name": "Nick Jarvis"})
    create_user("@Google", **{"name": "Google Inc."})
    #t_id = tweet("@ThePSF", "Python 3 is better than Python 2")
    #like("@nickj", t_id)
    #like("@neo4j", t_id)
