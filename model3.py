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
    keyword_embeddings, 
    keywords, 
    visited, 
    dest_url
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

        best_score = -1
        best_keyword = None

        # compare against ALL destination keywords
        for kw, kw_emb in zip(keywords, keyword_embeddings):
            score = cosine_sim(title_emb, kw_emb)
            if score > best_score:
                best_score = score
                best_keyword = kw

        scored.append((best_score, url, title, best_keyword))

    scored.sort(reverse=True, key=lambda x: x[0])

    print("\nTop candidates (best keyword match):")
    for s, u, t, kw in scored[:5]:
        print(f"{s:.3f} → {t}  (matched: {kw})")

    return [url for _, url, _, _ in scored[:5]] if scored else None

# ---------------- RUN ---------------- #

def run(source_url, dest_url):
    print("\nEnter destination-related keywords (comma separated)")
    print("Example: country, asia, geography, culture, south asia")
    kw_input = input("Keywords: ").strip()

    dest_keywords = [k.strip() for k in kw_input.split(",") if k.strip()]

    print("\nPreparing destination keyword embeddings...")

    # include destination title automatically
    all_keywords = [page_title_from_url(dest_url)] + dest_keywords
    keyword_embeddings = [get_embedding(k) for k in all_keywords]

    print("Destination keywords:")
    for k in all_keywords:
        print(" -", k)

    current = source_url
    visited = set()

    step = 0
    while(True):
        print(f"\nSTEP {step + 1}: {page_title_from_url(current)}")
        visited.add(current)

        next_pages = choose_next_source(
            current,
            keyword_embeddings,
            all_keywords,
            visited,
            dest_url
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


