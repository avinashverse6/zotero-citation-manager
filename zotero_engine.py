import re
import requests


def search_zotero(query, user_id, api_key):
    url = f"https://api.zotero.org/users/{user_id}/items"
    headers = {"Zotero-API-Key": api_key}
    params = {
        "q": query,
        "limit": 25,
        "format": "json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )
    except requests.RequestException as error:
        print("Network error:", error)
        return []

    if response.status_code != 200:
        print("Zotero error:", response.status_code)
        return []

    try:
        return response.json()
    except ValueError:
        print("Zotero returned invalid data.")
        return []



def display_search_results(items):
    print("\nSearch results:\n")

    type_names = {
        "journalArticle": "Journal Article",
        "book": "Book",
        "bookSection": "Book Section",
        "thesis": "Thesis",
        "report": "Report",
        "webpage": "Web Page",
        "blogPost": "Blog Post",
    }

    for number, item in enumerate(items, 1):
        data = item.get("data", {})
        authors = get_authors(data)
        year = get_year(data)
        title = data.get("title", "[No title]")
        display_title = title if len(title) <= 90 else title[:87] + "..."
        item_type = data.get("itemType", "")
        type_label = type_names.get(item_type, item_type or "Unknown type")

        if not authors:
            author_text = "Unknown author"
        elif len(authors) == 1:
            author_text = authors[0]["last"]
        elif len(authors) == 2:
            author_text = f'{authors[0]["last"]} & {authors[1]["last"]}'
        else:
            author_text = f'{authors[0]["last"]} et al.'

        print(
            f"{number}. {author_text} ({year}) "
            f"[{type_label}] — {display_title}"
        )


def get_authors(data):
    authors = []

    for creator in data.get("creators", []):
        if creator.get("creatorType") not in (None, "author"):
            continue

        if creator.get("lastName"):
            authors.append({
                "first": creator.get("firstName", "").strip(),
                "last": creator.get("lastName", "").strip()
            })

        elif creator.get("name"):
            authors.append({
                "first": "",
                "last": creator.get("name", "").strip()
            })

    return authors


def get_year(data):
    date = data.get("date", "") or ""
    match = re.search(r"\b(19|20)\d{2}\b", date)

    if match:
        return match.group(0)

    return "n.d."


def initials(first_name):
    parts = first_name.split()

    return " ".join(
        f"{part[0].upper()}."
        for part in parts
        if part
    )


def apa_author_name(author):
    last = author["last"]
    first = initials(author["first"])

    if first:
        return f"{last}, {first}"

    return last


def apa_in_text(data):
    authors = get_authors(data)
    year = get_year(data)

    if not authors:
        return f"(Unknown author, {year})"

    if len(authors) == 1:
        return f"({authors[0]['last']}, {year})"

    if len(authors) == 2:
        return (
            f"({authors[0]['last']} & "
            f"{authors[1]['last']}, {year})"
        )

    return f"({authors[0]['last']} et al., {year})"


def apa_narrative(data):
    authors = get_authors(data)
    year = get_year(data)

    if not authors:
        return f"Unknown author ({year})"

    if len(authors) == 1:
        return f"{authors[0]['last']} ({year})"

    if len(authors) == 2:
        return (
            f"{authors[0]['last']} and "
            f"{authors[1]['last']} ({year})"
        )

    return f"{authors[0]['last']} et al. ({year})"


def format_pages(pages):
    if not pages:
        return ""

    return pages.replace("-", "–")


def apa_full_reference(data):
    authors = get_authors(data)
    year = get_year(data)

    formatted_authors = [
        apa_author_name(author)
        for author in authors
    ]

    if len(formatted_authors) == 1:
        author_text = formatted_authors[0]
    elif len(formatted_authors) == 2:
        author_text = f"{formatted_authors[0]}, & {formatted_authors[1]}"
    elif formatted_authors:
        author_text = ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        author_text = ""

    title = data.get("title", "").strip()
    item_type = data.get("itemType", "")
    journal = data.get("publicationTitle", "").strip()
    volume = str(data.get("volume", "")).strip()
    issue = str(data.get("issue", "")).strip()
    pages = format_pages(data.get("pages", "").strip())
    doi = data.get("DOI", "").strip()
    url = data.get("url", "").strip()
    publisher = data.get("publisher", "").strip()
    institution = data.get("institution", "").strip()
    university = data.get("university", "").strip()
    report_type = data.get("reportType", "").strip()
    thesis_type = data.get("thesisType", "").strip()
    book_title = data.get("bookTitle", "").strip()
    edition = data.get("edition", "").strip()
    website_title = data.get("websiteTitle", "").strip()
    blog_title = data.get("blogTitle", "").strip()

    author_part = f"{author_text} ({year})." if author_text else f"({year})."

    if item_type == "journalArticle":
        reference = f"{author_part} {title}. {journal}"

        if volume:
            reference += f", {volume}"

        if issue:
            reference += f"({issue})"

        if pages:
            reference += f", {pages}"

        reference += "."

    elif item_type == "book":
        reference = f"{author_part} {title}"

        if edition:
            edition_text = edition.strip()
            if edition_text.isdigit():
                number = int(edition_text)
                if number == 1:
                    edition_text = "1st"
                elif number == 2:
                    edition_text = "2nd"
                elif number == 3:
                    edition_text = "3rd"
                else:
                    edition_text = f"{number}th"
            if not edition_text.lower().endswith("ed."):
                edition_text += " ed."
            reference += f" ({edition_text})"

        reference += "."

        if publisher:
            reference += f" {publisher}."

    elif item_type == "bookSection":
        editors = []

        for creator in data.get("creators", []):
            if creator.get("creatorType") != "editor":
                continue

            first = creator.get("firstName", "").strip()
            last = creator.get("lastName", "").strip()
            name = creator.get("name", "").strip()

            if last:
                initials_text = initials(first)
                editor_name = f"{initials_text} {last}".strip()
            elif name:
                editor_name = name
            else:
                continue

            editors.append(editor_name)

        if len(editors) == 1:
            editor_text = f"{editors[0]} (Ed.)"
        elif len(editors) == 2:
            editor_text = f"{editors[0]}, & {editors[1]} (Eds.)"
        elif editors:
            editor_text = ", ".join(editors[:-1]) + f", & {editors[-1]} (Eds.)"
        else:
            editor_text = ""

        reference = f"{author_part} {title}."

        if editor_text and book_title:
            reference += f" In {editor_text}, {book_title}"
        elif book_title:
            reference += f" In {book_title}"
        elif editor_text:
            reference += f" In {editor_text}"

        if pages:
            reference += f" (pp. {pages})"

        reference += "."

        if publisher:
            reference += f" {publisher}."

    elif item_type == "report":
        reference = f"{author_part} {title}"

        if report_type:
            reference += f" [{report_type}]"

        reference += "."

        organization = institution or publisher

        if organization:
            reference += f" {organization}."

    elif item_type == "thesis":
        thesis_label = thesis_type or "Thesis"
        organization = university or institution

        reference = f"{author_part} {title}"

        if organization:
            reference += f" [{thesis_label}, {organization}]."
        else:
            reference += f" [{thesis_label}]."

    elif item_type == "webpage":
        reference = f"{author_part} {title}."

        if website_title:
            reference += f" {website_title}."

        if url:
            reference += f" {url}"

    elif item_type == "blogPost":
        reference = f"{author_part} {title}."

        if blog_title:
            reference += f" {blog_title}."

        if url:
            reference += f" {url}"

    else:
        reference = f"{author_part} {title}."

        if journal:
            reference += f" {journal}"

            if volume:
                reference += f", {volume}"

            if issue:
                reference += f"({issue})"

            if pages:
                reference += f", {pages}"

            reference += "."

        elif publisher:
            reference += f" {publisher}."

    if doi:
        reference += f" https://doi.org/{doi}"
    elif url and item_type not in ("webpage", "blogPost"):
        reference += f" {url}"

    return reference

def show_details(item):
    data = item.get("data", {})

    print("\n================================")
    print("       REFERENCE DETAILS")
    print("================================")

    print("Title:", data.get("title", "Not available"))

    authors = get_authors(data)

    names = [
        f"{author['first']} {author['last']}".strip()
        for author in authors
    ]

    print(
        "Authors:",
        "; ".join(names) if names else "Not available"
    )

    print("Date:", data.get("date", "Not available"))
    print("Item type:", data.get("itemType", "Not available"))
    print(
        "Journal:",
        data.get("publicationTitle", "Not available")
    )
    print("Volume:", data.get("volume", "Not available"))
    print("Issue:", data.get("issue", "Not available"))
    print("Pages:", data.get("pages", "Not available"))
    print("DOI:", data.get("DOI", "Not available"))
    print("URL:", data.get("url", "Not available"))
    print("Zotero ID:", data.get("key", "Not available"))


def multiple_citation(items, numbers):
    selected = []
    seen = set()

    for number in numbers:
        if number in seen:
            continue

        if 1 <= number <= len(items):
            data = items[number - 1].get("data", {})
            authors = get_authors(data)

            if authors:
                surname = authors[0]["last"]
            else:
                surname = "Unknown author"

            selected.append((surname.lower(), data))
            seen.add(number)

    selected.sort(
        key=lambda item: (
            item[0],
            get_year(item[1])
        )
    )

    citations = [
        apa_in_text(data).strip("()")
        for _, data in selected
    ]

    if citations:
        return "(" + "; ".join(citations) + ")"

    return ""


def single_reference_menu(item):
    data = item.get("data", {})

    show_details(item)

    print("\n================================")
    print("          APA 7 OPTIONS")
    print("================================")
    print("1. Parenthetical citation")
    print("2. Narrative citation")
    print("3. Full reference")
    print("4. Show all")

    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        print("\nParenthetical:")
        print(apa_in_text(data))

    elif choice == "2":
        print("\nNarrative:")
        print(apa_narrative(data))

    elif choice == "3":
        print("\nFull reference:")
        print(apa_full_reference(data))

    elif choice == "4":
        print("\nParenthetical:")
        print(apa_in_text(data))

        print("\nNarrative:")
        print(apa_narrative(data))

        print("\nFull reference:")
        print(apa_full_reference(data))

    else:
        print("Invalid option.")


def main():
    print("================================")
    print("      ZOTERO CITATION MANAGER")
    print("================================")

    query = input("\nSearch Zotero: ").strip()

    if not query:
        print("Please enter a search term.")
        return

    items = search_zotero(query)

    if not items:
        print("No references found.")
        return

    print("\nSearch results:\n")

    for number, item in enumerate(items, 1):
        title = item.get("data", {}).get(
            "title",
            "[No title]"
        )
        print(f"{number}. {title}")

    print("\nCitation options:")
    print("1. Single reference")
    print("2. Multiple references")

    option = input("\nChoose an option: ").strip()

    if option == "1":
        choice = input(
            "\nEnter reference number: "
        ).strip()

        if not choice.isdigit():
            print("Invalid reference number.")
            return

        number = int(choice)

        if not 1 <= number <= len(items):
            print("Invalid reference number.")
            return

        single_reference_menu(items[number - 1])

    elif option == "2":
        numbers_text = input(
            "\nEnter reference numbers separated by commas "
            "(example: 1,3,5): "
        ).strip()

        if not numbers_text:
            print("No references selected.")
            return

        try:
            numbers = [
                int(number.strip())
                for number in numbers_text.split(",")
                if number.strip()
            ]
        except ValueError:
            print("Invalid numbers.")
            return

        citation = multiple_citation(items, numbers)

        if citation:
            print("\n================================")
            print("      MULTIPLE APA 7 CITATION")
            print("================================")
            print(citation)
        else:
            print("No valid references selected.")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
