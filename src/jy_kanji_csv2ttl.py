import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL

JK  = Namespace("https://example.org/joyokanji#")

# get the unicode
def kanji_uri(ch: str):
    return JK[f"kanji_U{ord(ch):04X}"] 

graph = Graph()
graph.bind("jk", JK)
graph.bind("owl", OWL)
graph.bind("rdfs", RDFS)

graph.add((JK.KanjiCharacter, RDF.type, OWL.Class))


with open("data/joyo_kanji.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        new = (row.get("new") or "").strip()
        if not new:
            continue

        instance = kanji_uri(new)
        graph.add((instance, RDF.type, JK.KanjiCharacter))
        graph.add((instance, RDFS.label, Literal(new)))


graph.serialize("out/joyo_kanji.ttl", format="turtle")
print("Wrote out/joyo_kanji.ttl")