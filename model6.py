from scrapper import (
    scrape_links,
    page_title_from_url
)

from NLPmodel import (
    get_embedding,
    cosine_sim
)

def choose_next_source(
    source_url,
    visited,
    dest_url,
    dest_embedding
):
    
    links = scrape_links(
        source_url,
        visited,
        dest_url
    )

    if dest_url in links:
        return [dest_url]

    scored = []

    for url in links:
        title = page_title_from_url(url)
        title_emb = get_embedding(title)

        final_score = cosine_sim(
            title_emb,
            dest_embedding
        )

        scored.append(
            (final_score, url, title)
        )

    scored.sort(reverse=True, key=lambda x: x[0])

    print("\nTop candidates:")
    for fs, u, t in scored[:5]:
        print(
            f"{fs:.3f} → {t}"
        )

    return [url for _, url, _ in scored[:5]] if scored else None


# ---------------- RUN ---------------- #


def run(source_url, dest_url):
    print("\nEnter destination-related content (comma separated)")
    print("Example: country in south asia, culture, geography, population")
    dest_content = input("Content: ").strip()
    print("\nPreparing destination vectors...")

    dest_title = page_title_from_url(dest_url)

    # merge comma-separated content into ONE semantic string
    merged_content = " ".join(
        [c.strip() for c in dest_content.split(",") if c.strip()]
    )

    print("Destination title:", dest_title)
    print("Merged destination content:", merged_content)

    dest_embedding = get_embedding(merged_content)

    current = source_url
    visited = set()
    step = 0

    while True:
        print(f"\nSTEP {step + 1}: {page_title_from_url(current)}")

        visited.add(current)

        next_pages = choose_next_source(
            current,
            visited,
            dest_url,
            dest_embedding
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