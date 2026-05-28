import csv

# can I read the the headers

for path in ["data/joyo_kanji.csv", "data/kanji_radicals.csv"]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(path, "headers:", reader.fieldnames)
        first = next(reader)
        print("first row:", first)
        print("-" * 50)
