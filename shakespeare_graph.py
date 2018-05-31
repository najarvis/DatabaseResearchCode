"""Basic querying with neo4j. Checking the relationship of words in Hamlet"""

from py2neo import Graph, Node

GRAPH = Graph(password="password")

def says(voice, word):
    query = """
        MERGE (c:Character {name: {voice}})
        MERGE (w:Word {value: {word}})
        MERGE (c)-[:SAYS]->(w)
        RETURN c, w;
    """
    GRAPH.run(query, voice=voice, word=word)

def comes_after(after_word, before_word):
    query = """
        MERGE (w1:Word {value: {word1}})
        MERGE (w2:Word {value: {word2}})
        MERGE (w1)-[:COMES_AFTER]->(w2)
        RETURN w1, w2;
    """
    GRAPH.run(query, word1=after_word, word2=before_word)

def run():
    reserved = ["ACT", "SCENE", "["]

    last = ""
    last_voice = ""
    start = False
    with open("TextDocs/shakespeare-hamlet-25.txt") as f:
        data = f.read()
        phrases = data.split("\n\n")
        for phrase in phrases:
            if phrase[:3] == "ACT":
                start = True

            if start:
                p = phrase.strip()
                for r in reserved:
                    if p.startswith(r):
                        break
                else:
                    s = p.split('\t')
                    voice, text = s[0], "".join(s[1:]).replace('\n', ' ')
                    if not voice.isupper():
                        voice = last_voice
                    for word in [t for t in text.split(' ') if len(t) > 0]:
                        if not word[-1].isalpha():
                            final = word[:-1]
                        else:
                            final = word
                        # print("{},{}".format(voice, final.lower()))
                        # Add to the database here
                        says(voice, final)
                        comes_after(final, last)

                        last = final

                    last_voice = voice

if __name__ == "__main__":
    run()
