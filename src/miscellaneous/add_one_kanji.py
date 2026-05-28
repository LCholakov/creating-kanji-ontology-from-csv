from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL

JK  = Namespace("https://example.org/joyokanji#")

graph = Graph()
graph.bind("jk", JK)
graph.bind("owl", OWL)
graph.bind("rdfs", RDFS)

graph.add((JK.KanjiCharacter, RDF.type, OWL.Class))

# Create one instance: 愛
kanji = JK["kanji_U611B"]
graph.add((kanji, RDF.type, JK.KanjiCharacter))
graph.add((kanji, RDFS.label, Literal("愛")))

graph.serialize("out/add_one_kanji.ttl", format="turtle")
print("Wrote out/add_one_kanji.ttl")