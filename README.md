# encoder

A byte-pair encoding (BPE) tokenizer built from scratch. Implements both a 
basic tokenizer and a GPT-4-style regex-based tokenizer, both trained on 
real text and verified to round-trip correctly.

## What this is

Two tokenizer implementations:

- **BasicTokenizer** — written independently, from my own understanding of 
  byte-pair encoding, *before* watching Karpathy build the equivalent in his 
  tokenizer video. Counts adjacent byte-pair frequencies, iteratively merges 
  the most frequent pair into a new token, and builds a merge table used for 
  both encoding and decoding.
- **RegexTokenizer** — extends the basic version with GPT-4's pre-splitting 
  regex pattern (which the video explains conceptually but doesn't provide 
  code for), chunking text by word, number, punctuation run, and whitespace 
  before BPE merging, so merges never cross those boundaries. Implementation 
  is my own, based on the video's explanation of GPT-4's approach.

## Testing

Trained and tested on real-world text — Wikipedia article text (Taylor 
Swift's page) and assorted paragraphs pulled from the internet, rather than 
just toy strings. Verified full round-trip correctness: 
`decode(encode(text)) == text` for every test case.

## What I learned

- How byte-pair encoding actually compresses text — iteratively merging the 
  most frequent adjacent pair, building up a vocabulary from raw UTF-8 bytes
- Why raw BPE without pre-splitting can merge across word/punctuation 
  boundaries in ways that bloat the vocabulary, and how GPT-4's regex 
  pre-split pattern prevents that by chunking text first
- Unicode property escapes (`\p{L}`, `\p{N}`) and why they matter for 
  handling non-English text and emoji correctly
- Why merges have to be applied in the exact order they were learned, both 
  for encoding new text and for correctly reversing them during decoding
- Caught and debugged a batch-merge variant in my own initial implementation 
  that diverged from the standard one-merge-per-pass algorithm — same core 
  idea, different compression behavior

## Contents

- `basic_tokenizer.py` — plain byte-pair encoding tokenizer
- `regex_tokenizer.py` — GPT-4-style tokenizer with regex pre-splitting

## Credit

Conceptual grounding from [Karpathy's tokenizer video](https://www.youtube.com/watch?v=zduSFxRajkE); 
implementations are original.