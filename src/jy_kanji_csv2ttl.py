import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL
from rdflib.namespace import XSD

JK  = Namespace("https://example.org/joyokanji#")

def unicode_uri(ch: str):
    return JK[f"kanji_U{ord(ch):04X}"] 

def normalize_cell(val):
    return (val or "").strip()

graph = Graph()
graph.bind("jk", JK)
graph.bind("owl", OWL)
graph.bind("rdfs", RDFS)

#classes
KanjiCharacter = JK.KanjiCharacter
Radical = JK.Radical

graph.add((KanjiCharacter, RDF.type, OWL.Class))
graph.add((Radical, RDF.type, OWL.Class))


# properties
hasOldForm = JK.hasOldForm
graph.add((hasOldForm, RDF.type, OWL.DatatypeProperty))

stroke_count = JK.strokeCount
graph.add((stroke_count, RDF.type, OWL.DatatypeProperty))

yearAdded = JK.yearAdded
graph.add((yearAdded, RDF.type, OWL.DatatypeProperty))


# convert kanji character data from input dataset joyo_kanji.csv
with open("data/joyo_kanji.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        new_form = normalize_cell(row.get("new"))
        if not new_form:
            continue
        
        instance = unicode_uri(new_form)
        graph.add((instance, RDF.type, KanjiCharacter))
        graph.add((instance, RDFS.label, Literal(new_form)))

        old_form = normalize_cell(row.get("old"))
        if old_form:
            graph.add((instance, hasOldForm, Literal(old_form)))

        strokes = (row.get("strokes") or "").strip()
        if strokes:
            graph.add((instance, stroke_count, Literal(int(strokes), datatype=XSD.integer)))

        
        year_raw = (row.get("year_added") or "").strip()
        # replace empty field with 1946 when the language reform was implemented
        year = 1946 if year_raw == "" else int(year_raw)
        graph.add((instance, yearAdded, Literal(str(year), datatype=XSD.gYear)))

with open("data/kanji_radicals.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        # using bushu, the jp term for radical, as var name, to avoid confusion with class Radical
        bushu = normalize_cell(row.get("radical"))
        if not bushu:
            continue
        
        instance = unicode_uri(bushu)
        graph.add((instance, RDF.type, Radical))
        graph.add((instance, RDFS.label, Literal(bushu)))

        strokes = (row.get("stroke_count") or "").strip()
        if strokes:
            graph.add((instance, stroke_count, Literal(int(strokes), datatype=XSD.integer)))


graph.serialize("out/joyo_kanji.ttl", format="turtle")
print("Wrote out/joyo_kanji.ttl")