import os
import json
from talon.voice import Context
from talon import resource

from . import config
from .text import shrink

vocab_alternate = config.load_config_json("vocab_alternate.json", dict)

vocab_alternate.update({f"shrink {k}": v for k, v in shrink.shrink_map.items()})

ctx = Context("vocab")

try:
    vocab_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.json")
    with resource.open(vocab_path) as fh:
        vocab = json.load(fh)
except FileNotFoundError:
    vocab = []

def add_vocab(words):
    global vocab
    vocab += [re.sub("[^a-zA-Z0-9]+", "", w) for w in words]
    vocab = sorted(list(set(vocab)))
    with open(vocab_path, "w") as f:
        json.dump(vocab, f, indent=0)

ctx.vocab = vocab + list(vocab_alternate.keys())
ctx.vocab_remove = config.load_config_json("vocab_remove.json", list)
