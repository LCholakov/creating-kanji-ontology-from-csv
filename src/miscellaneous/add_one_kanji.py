from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL

kanji_ns  = Namespace("https://example.org/kanji#")

graph = Graph()
graph.bind("kanji", kanji_ns)
graph.bind("owl", OWL)
graph.bind("rdfs", RDFS)

graph.add((kanji_ns.KanjiCharacter, RDF.type, OWL.Class))

# Create one instance: 愛
kanji = kanji_ns["kanji_U611B"]
graph.add((kanji, RDF.type, kanji_ns.KanjiCharacter))
graph.add((kanji, RDFS.label, Literal("愛")))

graph.serialize("out/add_one_kanji.ttl", format="turtle")
print("Wrote out/add_one_kanji.ttl")