"""Basic querying with neo4j. Checking the relationship of words in Hamlet"""

from py2neo import Graph
import random

GRAPH = Graph(password="password")

# Queries for creating the database

def says(voice, word):
    query = """
        MERGE (c:Character {name: {voice}})
        MERGE (w:Word {value: {word}})
        MERGE (c)-[s:SAYS]->(w)
        ON MATCH SET s.count = s.count + 1
        ON CREATE SET s.count = 1
        RETURN c, w;
    """
    GRAPH.run(query, voice=voice, word=word)

def comes_after(after_word, before_word):
    query = """
        MERGE (w1:Word {value: {word1}})
        MERGE (w2:Word {value: {word2}})
        MERGE (w1)-[c:COMES_AFTER]->(w2)
        ON MATCH SET c.count = c.count + 1
        ON CREATE SET c.count = 1
        RETURN w1, w2;
    """
    GRAPH.run(query, word1=after_word, word2=before_word)

def create():
    """Creates the graph. DO NOT RUN TWICE or the numbers will get messed upself.

    Also it takes like a half hour to run on my computer. The merges don't help"""
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
                        final = final.lower()
                        # print("{},{}".format(voice, final.lower()))
                        # Add to the database here
                        says(voice, final)
                        comes_after(final, last)

                        last = final

                    last_voice = voice

# Queries on the finished database below

def get_next_words(word):
    query2 = """
        MATCH (w2:Word)-[c:COMES_AFTER]->(w1:Word {value: {word}})
        RETURN w2.value, c.count as percentage
        ORDER BY percentage DESC;
    """

    # Create the percentages for the next words.
    next_words = list(GRAPH.run(query2, word=word))
    initial = 0
    final = {}
    for i in next_words:
        initial += i['percentage']
        final[i['w2.value']] = initial

    return final

def calc_next_word(next_words):
    # Basic markov chain
    val = random.uniform(0, max(next_words.values()))
    for word in sorted([w for w in next_words], key=lambda x: next_words[x]):
        if val < next_words[word]:
            return word

    return "No word?"

def run():
    """Shakespeare text generator. It would have made sense to keep words with punctuation,
    but since I didn't this creates a long run on sentance. it can be as long as you would
    like, just adjust the 100 below to any length you want (it is the maximum length of
    the string)"""

    previous_word = "alas"
    #for _ in range(5):
    words = ""
    while len(words + previous_word) < 100:
        words += previous_word + ' '
        previous_word = calc_next_word(get_next_words(previous_word))
    print(words)
    print()

if __name__ == "__main__":
    run()
