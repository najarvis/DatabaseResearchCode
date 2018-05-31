"""Basic querying with neo4j. Building a game database."""

import datetime
from py2neo import Graph, Node

GRAPH = Graph(password="password")

def create_game(name):
    game_node = GRAPH.run("MATCH (c:Game {name: {n}}) RETURN c", n=name).evaluate()
    if game_node is None:
        GRAPH.create(Node("Game", name=name))
    else:
        print(name, "already exists.")

def create_console(name, base_price):
    console_node = GRAPH.run("MATCH (c:Console {name: {n}}) RETURN c", n=name).evaluate()
    if console_node is None:
        GRAPH.create(Node("Console", name=name, price=base_price))
    else:
        print(name, "already exists.")

def create_person(name):
    person_node = GRAPH.run("MATCH (p:Person {name: {n}}) RETURN p", n=name).evaluate()
    if person_node is None:
        GRAPH.create(Node("Person", name=name))

def create_is_on(game, console, release_date=None):
    # A query to check if the relationship already exists.
    query = """
        MERGE (g:Game {name: {game_name}})
        MERGE (c:Console {name: {console_name}})
        MERGE (g)-[:IS_ON {release_date: {release_date}}]->(c)
        RETURN g, c;
    """
    GRAPH.run(query, game_name=game, console_name=console, release_date=release_date)

def create_likes(person, game):
    query = """
        MERGE (p:Person {name: {person_name}})
        MERGE (g:Game {name: {game_name}})
        MERGE (p)-[:LIKES]->(g)
        RETURN p, g;
    """
    GRAPH.run(query, game_name=game, person_name=person)


create_console("Xbox", 400.00)
create_console("PC", None)
create_console("Nintendo Wii", 249.99)
create_console("Nintendo Switch", 299.99)
create_console("Nintendo Wii U", 299.99)
create_game("Halo: Combat Evolved")
create_game("Crackdown")
create_is_on("Halo: Combat Evolved", "Xbox", datetime.date(2001, 11, 15).isoformat())
create_is_on("Halo: Combat Evolved", "PC", datetime.date(2003, 9, 30).isoformat())
create_is_on("Crackdown", "Xbox", datetime.date(2007, 2, 20).isoformat())
create_is_on("Halo 2", "PC", datetime.date(2007, 5, 31).isoformat())

create_person("Nick")
create_likes("Nick", "Crackdown")
create_likes("Nick", "Halo: Combat Evolved")

create_likes("Nick", "The Legend of Zelda: Breath of the Wild")
create_is_on("The Legend of Zelda: Breath of the Wild", "Nintendo Switch", datetime.date(2017, 3, 3).isoformat())
create_is_on("The Legend of Zelda: Breath of the Wild", "Nintendo Wii U", datetime.date(2017, 3, 3).isoformat())
