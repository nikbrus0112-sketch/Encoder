import regex as re


class RegexTokenizer:
    def __init__(self):
        GPT4_SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
        self.pat = re.compile(GPT4_SPLIT_PATTERN)

    def train(self, text, vocab_size, verbose=False):

        def get_stats(text):
            counts = {}
            for word in text:
                for pair in zip(word, word[1:]):
                    counts[pair] = counts.get(pair, 0) + 1
            return counts

        def merge(word, pair, idx):
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
                    new_word.append(idx)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            return new_word

        text_chunks = re.findall(self.pat, text)
        ids = [list(chunk.encode("utf-8")) for chunk in text_chunks]

        num_merges = vocab_size - 256

        self.merges = {}
        for i in range(num_merges):
            stats = get_stats(ids)
            if not stats:
                print("stopped at: ", i, " merges")
                break
            pair = max(stats, key=stats.get)
            idx = 256 + i
            for i in range(len(ids)):
                ids[i] = merge(ids[i], pair, idx)
            self.merges[pair] = idx

    def encode(self, text):
        text_chunks = re.findall(self.pat, text)
        ids = [list(chunk.encode("utf-8")) for chunk in text_chunks]

        new_text = []
        for word in ids:
            for pair in self.merges:
                i = 0
                new_tokens = []
                while i < len(word):
                    if i < len(word) - 1 and (word[i], word[i + 1]) == pair:
                        new_tokens.append(self.merges.get(pair))
                        i += 2
                    else:
                        new_tokens.append(word[i])
                        i += 1

                word = new_tokens
            new_text.append(word)
        flat_tokens = [tok for word in new_text for tok in word]
        return flat_tokens

    def decode(self, tokens):
        for key, val in reversed(self.merges.items()):
            i = 0
            new_tokens = []
            while i < len(tokens):
                if tokens[i] == val:
                    new_tokens.append(key[0])
                    new_tokens.append(key[1])
                    i += 1
                else:
                    new_tokens.append(tokens[i])
                    i += 1

            tokens = new_tokens

        byte_data = bytes(tokens)
        return byte_data.decode("utf-8", errors="replace")

    def save_merges_escaped(self, filepath):
        vocab = {i: bytes([i]) for i in range(256)}

        for (p0, p1), val in self.merges.items():
            vocab[val] = vocab[p0] + vocab[p1]

        with open(filepath, "w", encoding="utf-8") as f:
            for (p0, p1), val in self.merges.items():
                p0_bytes = vocab[p0]
                p1_bytes = vocab[p1]
                merged_bytes = vocab[val]

                p0_text = (
                    p0_bytes.decode("utf-8", errors="replace")
                    .encode("unicode_escape")
                    .decode("utf-8")
                )
                p1_text = (
                    p1_bytes.decode("utf-8", errors="replace")
                    .encode("unicode_escape")
                    .decode("utf-8")
                )
                merged_text = (
                    merged_bytes.decode("utf-8", errors="replace")
                    .encode("unicode_escape")
                    .decode("utf-8")
                )

                f.write(f"[{p0_text}] + [{p1_text}] -> [{merged_text}] {val}\n")
