"""
amazon_scraper.py
=================
Usage:
    python amazon_scraper.py <amazon_url_or_asin> [--api-key YOUR_KEY] [--domain amazon.com]

Examples:
    python amazon_scraper.py B09G9FPHY6
    python amazon_scraper.py https://www.amazon.com/dp/B09G9FPHY6
    python amazon_scraper.py B09G9FPHY6 --api-key abc123 --domain amazon.co.uk

Set SERPAPI_KEY env var to avoid passing --api-key every time.
"""

import re
import os
import sys
import json
import textwrap
import argparse
import urllib.parse
import urllib.request
from datetime import datetime


# ─────────────────────────────────────────────
# 1. CONFIG
# ─────────────────────────────────────────────

SERPAPI_ENDPOINT = "https://serpapi.com/search"
DEFAULT_DOMAIN   = "amazon.com"


# ─────────────────────────────────────────────
# 2. HELPERS — URL / ASIN PARSING
# ─────────────────────────────────────────────

def extract_asin(raw: str) -> str:
    """
    Accept a bare ASIN, a full Amazon URL, or a /dp/ path and return the ASIN.
    Raises ValueError when nothing recognisable is found.
    """
    raw = raw.strip()

    # Looks like a plain ASIN already (10 alphanumeric chars)
    if re.fullmatch(r"[A-Z0-9]{10}", raw, re.IGNORECASE):
        return raw.upper()

    # Try to pull /dp/XXXXXXXXXX or /gp/product/XXXXXXXXXX from a URL
    match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", raw, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    raise ValueError(
        f"Could not extract an ASIN from: {raw!r}\n"
        "Pass a 10-character ASIN or a full Amazon product URL."
    )


def detect_domain(url: str) -> str:
    """Best-effort: pull 'amazon.co.uk' etc. from a URL, else return DEFAULT_DOMAIN."""
    match = re.search(r"(amazon\.[a-z.]+)", url, re.IGNORECASE)
    return match.group(1).lower() if match else DEFAULT_DOMAIN


# ─────────────────────────────────────────────
# 3. API CALL
# ─────────────────────────────────────────────

def fetch_product(asin: str, api_key: str, domain: str = DEFAULT_DOMAIN) -> dict:
    """Call SerpAPI Amazon Product engine and return raw JSON dict."""
    params = {
        "engine":         "amazon_product",
        "asin":           asin,
        "amazon_domain":  domain,
        "api_key":        api_key,
    }
    url = SERPAPI_ENDPOINT + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} from SerpAPI: {body}") from e
    except Exception as e:
        raise RuntimeError(f"Request failed: {e}") from e


# ─────────────────────────────────────────────
# 4. EXTRACTION — pull only the good stuff
# ─────────────────────────────────────────────

def extract_product_info(data: dict) -> dict:
    pr = data.get("product_results", {})
    ri = data.get("reviews_information", {})
    summary = ri.get("summary", {})
    cr = summary.get("customer_reviews", {})

    return {
        "title":            pr.get("title"),
        "brand":            pr.get("brand"),
        "asin":             data.get("product_details", {}).get("asin") or pr.get("asin"),
        "price":            pr.get("price"),
        "old_price":        pr.get("old_price"),
        "discount":         pr.get("discount"),
        "rating":           pr.get("rating"),
        "reviews_count":    pr.get("reviews"),
        "bought_last_month":pr.get("bought_last_month"),
        "stock":            pr.get("stock"),
        "badges":           pr.get("badges", []),
        "thumbnails":       pr.get("thumbnails", [])[:3],   # first 3 images
        "about_item":       pr.get("about_item", []),
        "delivery":         pr.get("delivery", []),
        "product_details":  data.get("product_details", {}),
        "item_specifications": data.get("item_specifications", {}),
    }


def extract_ratings_breakdown(data: dict) -> dict:
    ri = data.get("reviews_information", {})
    cr = ri.get("summary", {}).get("customer_reviews", {})
    return {
        "ratings_count": cr.get("ratings_count"),
        "reviews_count": cr.get("reviews_count"),
        "histogram":     cr.get("histogram", {}),
        "summary_text":  ri.get("summary", {}).get("text"),
    }


def extract_reviews(data: dict) -> list[dict]:
    ri = data.get("reviews_information", {})
    raw = ri.get("authors_reviews", [])
    out = []
    for r in raw:
        out.append({
            "position":         r.get("position"),
            "title":            r.get("title"),
            "rating":           r.get("rating"),
            "date":             r.get("date"),
            "author":           r.get("author"),
            "verified_purchase":r.get("verified_purchase"),
            "helpful_votes":    r.get("helpful_votes"),
            "text":             r.get("text"),
            "product_variant":  r.get("product", {}).get("title"),
            "has_images":       bool(r.get("images")),
            "has_video":        bool(r.get("video")),
        })
    return out


def extract_purchase_options(data: dict) -> dict:
    po = data.get("purchase_options", {})
    result = {}
    for option_type, details in po.items():
        result[option_type] = {
            "caption":        details.get("caption"),
            "price":          details.get("price"),
            "price_unit":     details.get("price_unit"),
            "stock":          details.get("stock"),
            "delivery":       details.get("delivery", []),
        }
    return result


def extract_similar_products(data: dict) -> list[dict]:
    items = data.get("compare_with_similar", []) or data.get("related_products", [])
    return [
        {
            "position": i.get("position"),
            "title":    i.get("title"),
            "price":    i.get("price"),
            "rating":   i.get("rating"),
            "reviews":  i.get("reviews"),
            "asin":     i.get("asin"),
        }
        for i in items[:6]
    ]


def extract_sustainability(data: dict) -> dict | None:
    sf = data.get("sustainability_features")
    if not sf:
        return None
    return {
        "summary":                sf.get("summary"),
        "climate_pledge_friendly":sf.get("climate_pledge_friendly"),
        "features": [
            {"title": f.get("title"), "text": f.get("text")}
            for f in sf.get("features", [])
        ],
    }


# ─────────────────────────────────────────────
# 5. DISPLAY — pretty console output
# ─────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
BLUE   = "\033[34m"
WHITE  = "\033[97m"


def _hr(char="─", width=70, color=DIM):
    print(f"{color}{char * width}{RESET}")


def _section(title: str):
    print()
    _hr()
    print(f"{BOLD}{CYAN}  {title.upper()}{RESET}")
    _hr()


def _kv(label: str, value, indent=2):
    if value is None or value == [] or value == {}:
        return
    pad = " " * indent
    label_str = f"{DIM}{label:<22}{RESET}"
    if isinstance(value, list):
        print(f"{pad}{label_str}{value[0]}")
        for v in value[1:]:
            print(f"{pad}{'':22}{v}")
    else:
        print(f"{pad}{label_str}{BOLD}{value}{RESET}")


def _stars(rating: float | None) -> str:
    if rating is None:
        return "n/a"
    filled = int(round(rating))
    return f"{'★' * filled}{'☆' * (5 - filled)}  {rating:.1f}/5"


def _bar(pct_str: str, width=20) -> str:
    """Turn '45%' into a mini bar."""
    try:
        pct = int(pct_str.strip().replace("%", ""))
    except Exception:
        return pct_str
    filled = round(pct / 100 * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {pct_str:>4}"


def display_product_info(info: dict):
    _section("📦  Product Overview")
    _kv("Title",           textwrap.shorten(info["title"] or "", 80))
    _kv("Brand",           info["brand"])
    _kv("ASIN",            info["asin"])
    _kv("Badges",          ", ".join(info["badges"]) if info["badges"] else None)
    print()
    _kv("Price",           f"{GREEN}{info['price']}{RESET}" if info["price"] else None)
    _kv("Original Price",  info["old_price"])
    _kv("Discount",        f"{RED}{info['discount']}{RESET}" if info["discount"] else None)
    _kv("Stock",           info["stock"])
    _kv("Bought/Month",    info["bought_last_month"])
    print()
    _kv("Rating",          _stars(info["rating"]))
    _kv("Total Reviews",   f"{info['reviews_count']:,}" if info["reviews_count"] else None)
    print()
    if info["delivery"]:
        _kv("Delivery",    info["delivery"])
    if info["thumbnails"]:
        _kv("Images",      info["thumbnails"])


def display_ratings_breakdown(rb: dict):
    _section("⭐  Ratings Breakdown")
    _kv("Total Ratings",   f"{rb['ratings_count']:,}" if rb["ratings_count"] else None)
    _kv("Total Reviews",   f"{rb['reviews_count']:,}" if rb["reviews_count"] else None)
    if rb["summary_text"]:
        print(f"\n  {DIM}{textwrap.shorten(rb['summary_text'], 120)}{RESET}")
    hist = rb.get("histogram", {})
    if hist:
        print(f"\n  {BOLD}Star distribution:{RESET}")
        for star in ["5 star", "4 star", "3 star", "2 star", "1 star"]:
            pct = hist.get(star, "0%")
            bar = _bar(pct)
            color = GREEN if "5" in star else (YELLOW if "4" in star or "3" in star else RED)
            print(f"    {color}{star}{RESET}  {bar}")


def display_reviews(reviews: list[dict]):
    _section(f"💬  Customer Reviews  ({len(reviews)} returned)")
    if not reviews:
        print("  No reviews in this response.")
        return
    for r in reviews:
        print()
        vp  = f"{GREEN}✔ Verified{RESET}" if r["verified_purchase"] else f"{DIM}Unverified{RESET}"
        img = f" {BLUE}[img]{RESET}"  if r["has_images"] else ""
        vid = f" {BLUE}[vid]{RESET}"  if r["has_video"]  else ""
        stars = _stars(r["rating"])
        print(f"  {BOLD}#{r['position']:>2}  {r['author']}{RESET}  {vp}{img}{vid}")
        print(f"       {YELLOW}{stars}{RESET}   {DIM}{r['date']}{RESET}")
        if r["product_variant"]:
            print(f"       {DIM}Variant: {r['product_variant']}{RESET}")
        if r["title"]:
            print(f"       {BOLD}{r['title']}{RESET}")
        if r["text"]:
            wrapped = textwrap.fill(r["text"], width=66,
                                    initial_indent="       ",
                                    subsequent_indent="       ")
            print(wrapped)
        if r["helpful_votes"]:
            print(f"       {DIM}👍 {r['helpful_votes']}{RESET}")
        _hr("·", 66, DIM)


def display_purchase_options(po: dict):
    if not po:
        return
    _section("🛒  Purchase Options")
    for otype, details in po.items():
        print(f"\n  {BOLD}{otype.replace('_', ' ').title()}{RESET}")
        _kv("Caption",  details["caption"])
        _kv("Price",    f"{GREEN}{details['price']}{RESET}" if details["price"] else None)
        _kv("Per Unit", details["price_unit"])
        _kv("Stock",    details["stock"])
        if details["delivery"]:
            _kv("Delivery", details["delivery"])


def display_similar(items: list[dict]):
    if not items:
        return
    _section("🔄  Compare / Similar Products")
    for i in items:
        stars = _stars(i["rating"]) if i["rating"] else "n/a"
        rev   = f"{i['reviews']:,}" if i["reviews"] else "—"
        price = i["price"] or "—"
        title = textwrap.shorten(i["title"] or "", 55)
        print(f"  {DIM}#{i['position']}{RESET}  {title}")
        print(f"       {GREEN}{price:<12}{RESET} {YELLOW}{stars}{RESET}  {DIM}({rev} reviews){RESET}")
        print()


def display_sustainability(sf: dict | None):
    if not sf:
        return
    _section("🌱  Sustainability")
    if sf["climate_pledge_friendly"]:
        print(f"  {GREEN}✔ Climate Pledge Friendly{RESET}")
    if sf["summary"]:
        print(f"\n  {textwrap.shorten(sf['summary'], 120)}")
    for f in sf["features"]:
        print(f"\n  {BOLD}{f['title']}{RESET}")
        if f["text"]:
            print(textwrap.fill(f["text"], width=68, initial_indent="    ", subsequent_indent="    "))


def display_specs(info: dict):
    specs = {**info.get("item_specifications", {}), **info.get("product_details", {})}
    if not specs:
        return
    _section("📋  Specifications & Details")
    for k, v in specs.items():
        if k in ("asin",):   # already shown
            continue
        _kv(str(k), str(v))


def display_about(info: dict):
    bullets = info.get("about_item", [])
    if not bullets:
        return
    _section("📝  About This Item")
    for b in bullets:
        wrapped = textwrap.fill(b, width=68, initial_indent="  • ",
                                subsequent_indent="    ")
        print(wrapped)


# ─────────────────────────────────────────────
# 6. MAIN PIPELINE
# ─────────────────────────────────────────────

def analyse(raw_input: str, api_key: str, domain: str | None = None):
    """Full pipeline: parse → fetch → extract → display."""

    # Auto-detect domain from URL if not provided
    if domain is None:
        domain = detect_domain(raw_input) if "amazon" in raw_input else DEFAULT_DOMAIN

    asin = extract_asin(raw_input)

    print(f"\n{BOLD}{WHITE}Amazon Product Analyser{RESET}")
    print(f"{DIM}ASIN: {asin}   Domain: {domain}   {datetime.now():%Y-%m-%d %H:%M}{RESET}")
    _hr("═", 70, BOLD)

    print(f"\n{DIM}Fetching from SerpAPI …{RESET}", end="", flush=True)
    data = fetch_product(asin, api_key, domain)
    print(f" {GREEN}done{RESET}")

    info     = extract_product_info(data)
    rb       = extract_ratings_breakdown(data)
    reviews  = extract_reviews(data)
    po       = extract_purchase_options(data)
    similar  = extract_similar_products(data)
    sustain  = extract_sustainability(data)

    display_product_info(info)
    display_ratings_breakdown(rb)
    display_about(info)
    display_specs(info)
    display_purchase_options(po)
    display_reviews(reviews)
    display_similar(similar)
    display_sustainability(sustain)

    _hr("═", 70, BOLD)
    print(f"\n{DIM}Done. {len(reviews)} reviews shown.{RESET}\n")

    return {
        "product":          info,
        "ratings_breakdown":rb,
        "reviews":          reviews,
        "purchase_options": po,
        "similar_products": similar,
        "sustainability":   sustain,
    }


# ─────────────────────────────────────────────
# 7. CLI ENTRY POINT
# ─────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Fetch & display Amazon product details via SerpAPI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python amazon_scraper.py B09G9FPHY6
              python amazon_scraper.py https://www.amazon.com/dp/B09G9FPHY6
              python amazon_scraper.py B09G9FPHY6 --api-key abc123 --domain amazon.co.uk
        """),
    )
    p.add_argument("input",    help="Amazon URL or bare ASIN")
    p.add_argument("--api-key",default=os.getenv("SERPAPI_KEY"), help="SerpAPI key (or set SERPAPI_KEY env var)")
    p.add_argument("--domain", default=None, help="Amazon domain, e.g. amazon.co.uk (auto-detected from URL)")
    p.add_argument("--json",   action="store_true", help="Also dump raw extracted data as JSON at the end")
    return p


def main():
    parser = _build_parser()
    args   = parser.parse_args()

    if not args.api_key:
        parser.error("Provide --api-key or set the SERPAPI_KEY environment variable.")

    try:
        result = analyse(args.input, args.api_key, args.domain)
        if args.json:
            print("\n--- JSON DUMP ---")
            print(json.dumps(result, indent=2, default=str))
    except (ValueError, RuntimeError) as e:
        print(f"\n{RED}Error: {e}{RESET}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()