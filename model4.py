from scrapper import scrape_links, page_title_from_url
from NLPmodel import get_embedding, cosine_sim

def choose_next_source(
    source_url,
    visited,
    dest_url,
    dest_title_emb,
    dest_content_emb
):
    links = scrape_links(source_url, visited)

    if dest_url in links:
        return dest_url

    if not links:
        return None

    scored = []

    for url in links:
        title = page_title_from_url(url)
        title_emb = get_embedding(title)

        score_title = cosine_sim(title_emb, dest_title_emb)
        score_content = cosine_sim(title_emb, dest_content_emb)

        # weighted score
        final_score = 0.6 * score_title + 0.4 * score_content

        scored.append(
            (final_score, url, title, score_title, score_content)
        )

    scored.sort(reverse=True, key=lambda x: x[0])

    print("\nTop candidates:")
    for fs, u, t, st, sc in scored[:5]:
        print(
            f"{fs:.3f} → {t} "
            f"(title={st:.3f}, content={sc:.3f})"
        )

    return scored[0][1] if scored else None


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

    dest_title_emb = get_embedding(dest_title)
    dest_content_emb = get_embedding(merged_content)

    current = source_url
    visited = set()
    step = 0

    while True:
        print(f"\nSTEP {step + 1}: {page_title_from_url(current)}")
        visited.add(current)

        next_page = choose_next_source(
            current,
            visited,
            dest_url,
            dest_title_emb,
            dest_content_emb
        )

        if not next_page:
            print("No path forward")
            break

        if next_page == dest_url:
            print("\n🎯 DESTINATION REACHED!")
            break

        if next_page in visited:
            print("Loop detected, stopping")
            break

        current = next_page
        step += 1


