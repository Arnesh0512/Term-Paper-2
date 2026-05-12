from scrapper import (
    scrape_links,
    scrape_dest_lead_para,
    scrape_contents
)

from NLPmodel import (
    get_embedding,
    cosine_sim
)

# ---------------- SOURCE SELECTION ---------------- #

def choose_next_source(
    source_url,
    dest_embedding,
    dest_url,
    visited
):

    links = scrape_links(
        source_url,
        visited,
        dest_url
    )
    if dest_url in links:
        return [dest_url]
    
    contents = scrape_contents(links)

    scored = []

    for url, text in zip(links, contents):

        if not text:
            continue

        emb = get_embedding(text)
        score = cosine_sim(emb,dest_embedding)
        scored.append((score, url))

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    print("\nTop candidates:")

    for score, url in scored[:5]:
        print(f"{score:.3f} → {url}")

    return [url for _, url in scored[:5]] if scored else None

# ---------------- MAIN RUN ---------------- #

def run(source_url,dest_url):
    print("\nFetching destination embedding...")
    dest_content = scrape_dest_lead_para(dest_url)
    dest_embedding = get_embedding(dest_content)

    current = source_url
    visited = set()
    step = 0

    while True:
        print(f"\nSTEP {step + 1}: {current}")
        visited.add(current)

        next_pages = choose_next_source(
            current,
            dest_embedding,
            dest_url,
            visited
        )

        for next_page in next_pages:
            if next_page == dest_url:
                print("\n🎯 DESTINATION REACHED!")
                return
            if next_page in visited:
                print("Loop detected, skipping:", next_page)
                continue
            current = next_page
            step += 1
            break

        else:
            print("No path forward")
            break