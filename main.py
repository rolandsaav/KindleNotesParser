import sys
from typing import Optional
import datetime
from dataclasses import dataclass, asdict
import json

@dataclass
class Annotation:
    book: str
    author: str
    time: str

@dataclass
class Highlight(Annotation):
    begin: int
    end: int
    content: str
    page: Optional[int]
    kind: str = "Highlight"

@dataclass
class Bookmark(Annotation):
    location: int
    page: Optional[int]
    kind: str = "Bookmark"

@dataclass
class Note(Annotation):
    location: int
    page: Optional[int]
    content: str
    kind: str = "Note"

def get_title_author(s:str) -> tuple[str,str]:
    start = s.rfind("(")
    end = s.rfind(")")

    author = s[start + 1: end].strip()
    title = s[:start].strip()

    return title, author

def get_page_location_type(s:str) -> tuple[int, str, str]:
    values = s.split(" ")

    anno_type = values[2]
    page_or_location = values[4]

    # If highlight on page, then there is a location.
    # Else, highlight on location, no page
    # Final section is always added timestamp

    if page_or_location == "page":
        page = int(values[5])
        location = values[8]
        return page, location, anno_type
    else:
        page = -1
        location = values[5]
        return page, location, anno_type

def get_time(s:str):
    time_chunk = s.split("|")[-1]
    s_clean = time_chunk.replace("Added on", "").strip()
    dt = datetime.datetime.strptime(s_clean, "%A, %B %d, %Y %I:%M:%S %p")
    return dt

def main():
    if len(sys.argv) == 1:
        print("Must have at least one argument")
        quit()

    file_name = sys.argv[1]

    with open(file_name, encoding="utf-8-sig") as file:
        content = file.read()

    cleaned = content.replace('\ufeff', '')

    items = cleaned.split("==========\n")

    annotations = []

    for item in items:
        # skip empty items
        if item.strip() == "":
            continue
        lines = item.splitlines(keepends=False)

        # # TODO: Fix the splits so that this bug can't happen
        # if(len(lines)) == 0:
        #     continue

        book = lines[0]
        title, author = get_title_author(book)
        annotation = lines[1]
        time = get_time(annotation).isoformat()
        page, location, anno_type = get_page_location_type(annotation)

        content = "".join(lines[2:]).strip()

        match anno_type:
            case "Highlight":
                begin, end = location.split("-")
                highlight = Highlight(
                    title, 
                    author, 
                    time, 
                    int(begin), 
                    int(end), 
                    content,
                    page
                )

                annotations.append(highlight)

            case "Note":
                note = Note(
                    book=title,
                    author=author,
                    time=time,
                    location=int(location),
                    page=page,
                    content=content
                )

                annotations.append(note)
            case "Bookmark":
                bookmark = Bookmark(
                    book=title,
                    author=author,
                    time=time,
                    location=int(location),
                    page=page
                )

                annotations.append(bookmark)
            case _:
                print("Something unexpected occured")
                print(item)
    

    asdicts = [asdict(x) for x in annotations]
    out = json.dumps(asdicts, indent=2)
    print(out)

if __name__ == "__main__":
    main()
