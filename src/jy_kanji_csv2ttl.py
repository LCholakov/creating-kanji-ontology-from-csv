import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL
from rdflib.namespace import XSD

JK  = Namespace("https://example.org/joyokanji#")

def unicode_uri(ch: str):
    # return JK[f"kanji_U{ord(ch):04X}"] 
    # print(ch)
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
GradeLevel = JK.GradeLevel # what year in school it's taught or S if it's in secondary (highschool).
Reading = JK.Reading
OnyomiReading = JK.OnYomiReading
KunyomiReading = JK.KunYomiReading

graph.add((KanjiCharacter, RDF.type, OWL.Class))
graph.add((Radical, RDF.type, OWL.Class))
graph.add((GradeLevel, RDF.type, OWL.Class))
graph.add((Reading, RDF.type, OWL.Class))
graph.add((OnyomiReading, RDF.type, OWL.Class))
graph.add((OnyomiReading, RDFS.subClassOf, Reading))
graph.add((KunyomiReading, RDF.type, OWL.Class))
graph.add((KunyomiReading, RDFS.subClassOf, Reading))


# datatype properties
hasOldForm = JK.hasOldForm
stroke_count = JK.strokeCount
yearAdded = JK.yearAdded

graph.add((hasOldForm, RDF.type, OWL.DatatypeProperty))
graph.add((stroke_count, RDF.type, OWL.DatatypeProperty))
graph.add((yearAdded, RDF.type, OWL.DatatypeProperty))

# object properties
hasRadical = JK.hasRadical
taughtInGrade = JK.taughtInGrade
hasReading = JK.hasReading

graph.add((hasRadical, RDF.type, OWL.ObjectProperty))
graph.add((taughtInGrade, RDF.type, OWL.ObjectProperty))
graph.add((hasReading, RDF.type, OWL.ObjectProperty))

# Make the grade level a separate class cuz it's not just a simple integer.
grade_map = {}
for i in range(1, 7):
    uri = JK[f"Grade{i}"]
    grade_map[str(i)] = uri
    graph.add((uri, RDF.type, GradeLevel))
    graph.add((uri, RDFS.label, Literal(f"Grade {i}")))
secondary_uri = JK["Secondary"]
grade_map["S"] = secondary_uri
graph.add((secondary_uri, RDF.type, GradeLevel))
graph.add((secondary_uri, RDFS.label, Literal("Secondary education")))

# first convert radicals and build a local dict to match radicals from kanji dataset to specific entity in radicals dataset
radical_uri_by_char = {}
with open("data/kanji_radicals.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
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
        # if i > 1000:
        #     break
        new_form = normalize_cell(row.get("new"))
        if not new_form:
            continue
        
        instance = unicode_uri(new_form)
        graph.add((instance, RDF.type, KanjiCharacter))
        graph.add((instance, RDFS.label, Literal(new_form)))

        # old form of the kanji
        old_form = normalize_cell(row.get("old"))
        if old_form:
            graph.add((instance, hasOldForm, Literal(old_form)))

        # stroke count
        strokes = (row.get("strokes") or "").strip()
        if strokes:
            graph.add((instance, stroke_count, Literal(int(strokes), datatype=XSD.integer)))

        # year kanji was added 
        year_raw = (row.get("year_added") or "").strip()
        # replace empty field with 1946 when the language reform was implemented
        year = 1946 if year_raw == "" else int(year_raw)
        graph.add((instance, yearAdded, Literal(str(year), datatype=XSD.gYear)))

        # match radical from 
        # apparently at least one entry "1814,弁,辨瓣辯,辛瓜辛,5,5,,"
        # has multiple values so need to accomodate that. And deal with duplicates in this netry.
        radical_field = normalize_cell(row.get("radical"))
        
        if radical_field:
            for radical_char in set(radical_field): 
                radical_uri = radical_uri_by_char.get(radical_char)

                if radical_uri is None:
                    radical_uri = unicode_uri(radical_char)
                    radical_uri_by_char[radical_char] = radical_uri

                    graph.add((radical_uri, RDF.type, Radical))
                    graph.add((radical_uri, RDFS.label, Literal(radical_char)))

                graph.add((instance, hasRadical, radical_uri))

        # grade when kanji is taught
        grade_raw = normalize_cell(row.get("grade"))
        if grade_raw in grade_map:
            graph.add((instance, taughtInGrade, grade_map[grade_raw]))

graph.serialize("out/joyo_kanji.ttl", format="turtle")
print("Wrote out/joyo_kanji.ttl")