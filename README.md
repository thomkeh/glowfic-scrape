# glowfic scraper

Requires Python 3.10+ (with `lxml` and `smartypants`) and `ebook-convert`.

Example usage
```
python -m glowfic_scrape.download_thread 4582
python -m glowfic_scrape.download_images mad_investor_chaos_and_the_woman_of_asmodeus.json
python -m glowfic_scrape.to_html mad_investor_chaos_and_the_woman_of_asmodeus.json
python -m glowfic_scrape.to_ebook mad_investor_chaos_and_the_woman_of_asmodeus.html
```
