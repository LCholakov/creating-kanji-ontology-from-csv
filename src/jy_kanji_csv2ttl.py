import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL
from rdflib.namespace import XSD

JK  = Namespace("https://example.org/joyokanji#")

def unicode_uri(ch: str):
    # return JK[f"kanji_U{ord(ch):04X}"] 
    return JK[f"U{ord(ch):04X}"] 

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
stroke_count = JK.strokeCount
yearAdded = JK.yearAdded
hasRadical = JK.hasRadical

# graph.add((hasOldForm, RDF.type, OWL.DatatypeProperty))
# graph.add((stroke_count, RDF.type, OWL.DatatypeProperty))
# graph.add((yearAdded, RDF.type, OWL.DatatypeProperty))
# graph.add((hasRadical, RDF.type, OWL.DatatypeProperty))

# first load radicals and build a local dict to match radicals from kanji dataset to specific entity in radicals dataset
radical_uri_by_char = {}
with open("data/kanji_radicals.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 15:
            break
        
        radical_char = normalize_cell(row.get("radical"))
        if not radical_char:
            continue
        
        instance = unicode_uri(radical_char)
        radical_uri_by_char[radical_char] = instance
        graph.add((instance, RDF.type, Radical))
        graph.add((instance, RDFS.label, Literal(radical_char)))

        strokes = (row.get("stroke_count") or "").strip()
        if strokes:
            graph.add((instance, stroke_count, Literal(int(strokes), datatype=XSD.integer)))


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

        # match radical from 
        radical_char = normalize_cell(row.get("radical"))
        if radical_char:
            rad_uri = radical_uri_by_char.get(radical_char)

            if rad_uri:
                graph.add((instance, hasRadical, rad_uri))



graph.serialize("out/joyo_kanji.ttl", format="turtle")
print("Wrote out/joyo_kanji.ttl")