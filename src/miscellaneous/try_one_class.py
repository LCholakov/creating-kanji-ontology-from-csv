from rdflib import Graph, Namespace, RDF, URIRef

owl = Namespace("http://www.w3.org/2002/07/owl#")
kanji  = Namespace("https://example.org/kanji#")

graph = Graph()
graph.bind("kanji", kanji)
graph.bind("owl", owl)

# try to define a single class
graph.add((kanji.KanjiCharacter, RDF.type, owl.Class))

# output to ttl
graph.serialize("out/try_one_class.ttl", format="turtle")
print("Wrote out/try_one_class.ttl")
