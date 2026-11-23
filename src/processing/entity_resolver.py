import re
from rapidfuzz import process, fuzz

SEED_CANONICAL = {
    "OpenAI": ["Open AI", "OpenAI Inc", "OpenAI, Inc."],
    "Google": ["Google LLC", "Google AI"],
    "Microsoft": ["Microsoft Corporation", "Microsoft AI"],
    "Anthropic": ["Anthropic PBC"],
    "Meta": ["Meta Platforms", "Facebook AI"],
    "NVIDIA": ["Nvidia Corporation", "NVIDIA AI"],
    "Hugging Face": ["HuggingFace", "Hugging Face Inc"],
    "Cohere": ["Cohere Inc"],
    "Mistral AI": ["Mistral", "Mistral AI SAS"],
    "Stability AI": ["Stability"],
}

def normalize(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def resolve_name(raw, threshold=92):
    if not raw:
        return None, "EMPTY"
    aliases = {}
    for canonical, variants in SEED_CANONICAL.items():
        aliases[normalize(canonical)] = canonical
        for v in variants:
            aliases[normalize(v)] = canonical
    key = normalize(raw)
    if key in aliases:
        return aliases[key], "SEED_ALIAS"
    choices = list(aliases.keys())
    match = process.extractOne(key, choices, scorer=fuzz.ratio)
    if match and match[1] >= threshold:
        return aliases[match[0]], "FUZZY_SEED_MATCH"
    # Preserve unknown names rather than guessing a canonical identity.
    return raw.strip(), "UNMATCHED_PRESERVED"

def mapping_log(names):
    rows = []
    for raw in sorted(set(x for x in names if x)):
        canonical, method = resolve_name(raw)
        rows.append({"raw_name":raw, "canonical_name":canonical, "method":method})
    return rows
