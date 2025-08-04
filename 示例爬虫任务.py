# tasks/example_task.py
task_config = {
    "name": "Example News Crawler",
    "description": "Crawl news from example site",
    "spider": "requests_spider",
    "processor": "html_processor",
    "storage": "json_storage",
    "url": "https://example-news-site.com/latest",
    "extraction_rules": {
        "titles": {
            "selector": "h2.news-title",
            "attr": "text",
            "multiple": True
        },
        "summaries": {
            "selector": "div.news-summary",
            "attr": "text",
            "multiple": True
        },
        "published_date": {
            "selector": "span.publish-date",
            "attr": "text",
            "regex": r"(\d{4}-\d{2}-\d{2})"
        }
    },
    "schedule": "daily",
    "proxy": True
}