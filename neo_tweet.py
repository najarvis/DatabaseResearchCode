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
    GRAPH.push(tweet_node)

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

def get_full_feed():
    """Gets the most recent tweets as a cursor"""
    query = "MATCH (t:Tweet) RETURN t ORDER BY t.tweeted_on DESC LIMIT 25;"
    return GRAPH.run(query)

def get_user_feed(handle):
    """Gets the most recent tweets only from the accounts that the account
    specified by the handle parameter follow"""
    query = """
        MATCH (t:Tweet)<-[:TWEETED]-(u)
        WHERE (:User {handle: {handle}})-[:FOLLOWS]->(u)
        RETURN t ORDER BY t.tweeted_on DESC LIMIT 25;
    """
    return GRAPH.run(query, handle=handle)

def get_author(tweet_id):
    """Helper method to get the author of a tweet"""

    query = """
        MATCH (t:Tweet {tweet_id: {tweet_id}})<-[:TWEETED]-(a)
        RETURN a.handle as handle, a.name as name;
    """
    return GRAPH.run(query, tweet_id=tweet_id)

def format_tweet(tweet_node):
    """Helper method to take a tweet node and print it out"""

    author = next(get_author(tweet_node['tweet_id']))
    print("{} - {}".format(author.get('name', author['handle'][1:]), author['handle']))
    print(tweet_node['text'])
    print("Likes: {}\tTweeted on: {}".format(tweet_node['num_likes'], tweet_node['tweeted_on']))

def run():
    """Main twitter client"""

    # A good exercise would be how to authenticate users with passwords.
    handle = input("What is your handle?: ")
    if not handle.startswith("@"):
        handle = "@" + handle

    print("Attempting to create user with handle:", handle)
    create_user(handle)
    print()

    # Options Menu
    print("Options:")
    print("(l)ike")
    print("(t)weet")
    print("(r)efresh")
    print("(f)ollow")
    print("(q)uit")
    print()

    tweets = get_full_feed()
    while True:
        try:
            current_tweet = next(tweets)['t']
            format_tweet(current_tweet)
        except StopIteration:
            print("No more tweets, fetching new ones")
            tweets = get_full_feed()
            input("(hit enter to continue): ")
            current_tweet = None

        option = input("Enter Command (Press enter to continue): ")

        # Like
        if option.lower() in ["like", "l"]:
            if current_tweet is not None:
                like(handle, current_tweet['tweet_id'])

        # Tweet
        elif option.lower() in ["tweet", "t"]:
            print("Enter Tweet: (leave blank to cancel)")
            tweet_text = input(": ")
            if tweet_text:
                tweet(handle, tweet_text)

        # Refresh
        elif option.lower() in ["refresh", "r"]:
            print("Refreshing tweets...")
            tweets = get_full_feed()

        # Follow
        elif option.lower() in ["follow", "f"]:
            other_handle = input("Other handle?: ")
            if not other_handle.startswith("@"):
                other_handle = "@" + other_handle
            follow(handle, other_handle)

        # Quit
        elif option.lower() in ["quit", "q"]:
            print("Goodbye")
            break



        print()


if __name__ == "__main__":
    run()
    #create_user("@nickj")
    #create_user("@nickj", **{"bio": "Cool Kid", "name": "Nick Jarvis"})
    #create_user("@google", name="Google Inc.")
    #t_id = tweet("@ThePSF", "Python 3 is better than Python 2")
    #like("@nickj", t_id)
    #like("@neo4j", t_id)
