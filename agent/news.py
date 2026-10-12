"""Live headlines from RSS; deduped against what the agent has already seen."""
import calendar
import time

import feedparser

from . import config


def fetch(seen, max_age_hours=4, limit=40):
    out, cutoff = [], time.time() - max_age_hours * 3600
    for url in config.NEWS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue
        for e in feed.entries[:30]:
            uid = e.get("id") or e.get("link")
            if not uid or uid in seen:
                continue
            ts = e.get("published_parsed") or e.get("updated_parsed")
            ts = calendar.timegm(ts) if ts else time.time()
            if ts >= cutoff:
                out.append({"id": uid, "ts": int(ts), "source": feed.feed.get("title", url),
                            "title": e.get("title", ""), "summary": (e.get("summary") or "")[:300]})
    return sorted(out, key=lambda x: -x["ts"])[:limit]
