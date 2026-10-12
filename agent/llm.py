"""Model calls with cost controls: prompt caching, cheap triage, optional free local model, usage log."""
import json
import re

import httpx

from . import config

# $ per million tokens (input, output). Edit if prices change. Cached reads bill at ~10% of input.
PRICES = {"claude-haiku-5-5": (1, 5), "claude-sonnet-5-5": (3, 15), "claude-opus-5-5": (5, 25)}

_client = None


def _anthropic():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def cost(model, usage):
    i, o = PRICES.get(model, (3, 15))
    fresh = usage.input_tokens
    cached = getattr(usage, "cache_read_input_tokens", 0) or 0
    written = getattr(usage, "cache_creation_input_tokens", 0) or 0
    return (fresh * i + cached * i * 0.1 + written * i * 1.25 + usage.output_tokens * o) / 1e6


def create(model, system, messages, tools=None, max_tokens=3000):
    """Anthropic call with the system prompt and tool list cached (they never change between calls)."""
    sys_blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    kw = {}
    if tools:
        tools = [dict(t) for t in tools]
        tools[-1]["cache_control"] = {"type": "ephemeral"}
        kw["tools"] = tools
    r = _anthropic().messages.create(model=model, max_tokens=max_tokens, system=sys_blocks, messages=messages, **kw)
    return r, cost(model, r.usage)


TRIAGE_PROMPT = """You screen headlines for a long-only crypto/gold spot trader (products: {products}).
Reply with JSON only: {{"act": true|false, "products": [...], "why": "<one line>"}}.
act=true only if something could plausibly move a product by several percent over the next days and
might NOT already be fully priced in. Routine news, opinion pieces, and already-old stories -> false."""


def triage(text):
    """Cheap yes/no screen. Uses a local Ollama model if TRIAGE_MODEL starts with 'ollama:' (free)."""
    prompt = TRIAGE_PROMPT.format(products=", ".join(config.UNIVERSE))
    if config.TRIAGE_MODEL.startswith("ollama:"):
        r = httpx.post(f"{config.OLLAMA_URL}/api/chat", timeout=120, json={
            "model": config.TRIAGE_MODEL.split(":", 1)[1], "stream": False, "format": "json",
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}]})
        raw, spent = r.json()["message"]["content"], 0.0
    else:
        r, spent = create(config.TRIAGE_MODEL, prompt, [{"role": "user", "content": text}], max_tokens=200)
        raw = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        out = json.loads(m.group(0)) if m else {"act": False, "why": "unparseable"}
    except json.JSONDecodeError:
        out = {"act": False, "why": "unparseable"}
    return out, spent
