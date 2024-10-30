import argparse
import gspread
import bibtexparser
import json
import os

from sp_key import SHEET_NAME, SP_SHEET_KEY

# headers of spreadsheet
HEADERS = ['mrnumber', 
            'mrclass', 
            'issn', 
            'pages', 
            'number', 
            'year', 
            'volume',
            'fjournal',
            'journal',
            'title',
            'author',
            'ENTRYTYPE',
            'ID',
            'url',
            ]

# if header is not in article, put empty string
def _append_empty_str(article, selected_header):
    for header in HEADERS:
        if selected_header == header:
            if header not in article:
                column.append(" ")
            else:
                column.append(article[selected_header])

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

gc = gspread.service_account(filename="service_account.json")
sp = gc.open_by_key(SP_SHEET_KEY)
wks = sp.worksheet(SHEET_NAME)

# parse command-line arguments
parser =argparse.ArgumentParser(description="BibTeX to JSON Converter")
parser.add_argument("bibtex_input", help="Input BibTeX file")
parser.add_argument("json_output", help="Output JSON file")
parser.add_argument(
    "--include_bibtex",
    action="store_true",
    help="Include BibTeX field in the JSON output",
)

args = parser.parse_args()

# load the BibTeX file
with open(args.bibtex_input, "r") as bibtex_input:
    bib_database = bibtexparser.load(bibtex_input)

# function to convert a JSON entry back to BibTeX format
def json_to_bibtex(entry):
    bibtex = f"@{entry['ENTRYTYPE']}{entry['ID']},\n"
    for key, value in entry.items():
        if key not in ["ENTRYTYPE", "ID"]:
            bibtex += f"    {key} = {{{value}}},\n"
    bibtex = bibtex.rstrip(",\n") + "\n}\n\n"
    return bibtex


# add BibTeX field to each JSON entry if requested
if args.include_bibtex:
    for entry in bib_database.entries:
        entry["bibtex"] = json_to_bibtex(entry)

# write the JSON file
os.makedirs("out", exist_ok=True)
with open(os.path.join("out", args.json_output), "w") as json_file:
    json.dump(bib_database.entries, json_file, indent=4)

print(
    f"""
    The BibTeX input file '{args.bibtex_input}'
    has been converted to '{args.json_output}'
    """
)

# read JSON file
json_open = open('out/output.json', 'r')
json_data = json.load(json_open)
all_length = len(json_data)

# get all IDs from column "N" in spreadsheet
ids = wks.col_values(13)

# remove duplicates comparing ID
new_data = [i for i in json_data if i['ID'] not in ids]
length = len(new_data)
print("The number of new references is {} / {}.".format(length, all_length))
if length != 0:
    print("New References:")
    for i in new_data:
            print(
            f"""
            {i['author']},
            {i['title']},
            """
            )

# create lists
for article in new_data:
    column = []
    for header in HEADERS:
        _append_empty_str(article, header)
        
    # put data into spreadsheet
    wks.append_row(column)

if length == 0:
    print(
    f"""
    No new references are added.
    """
    )
else:
    print(
    f"""
    New references are added! Please check the spreadsheet.
    """
    )

