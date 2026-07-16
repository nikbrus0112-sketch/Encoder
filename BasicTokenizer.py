class BasicTokenizer:
    def train(self, text, vocab_size, verbose=False):
        def get_stats(ids):
            counts = {}
            for pair in zip(ids, ids[1:]):
                counts[pair] = counts.get(pair, 0) + 1
            return counts

        def merge(ids, pair, idx):
            newids = []
            i = 0
            while i < len(ids):
                if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
                    newids.append(idx)
                    i += 2
                else:
                    newids.append(ids[i])
                    i += 1
            return newids

        tokens = text.encode("utf=8")
        tokens = list(map(int, tokens))

        max_num_in_vocab = 0
        for k in tokens:
            if k > max_num_in_vocab:
                max_num_in_vocab = k

        num_merges = vocab_size - max_num_in_vocab
        ids = list(tokens)

        self.merges = {}
        for i in range(num_merges):
            stats = get_stats(ids)
            pair = max(stats, key=stats.get)
            idx = max_num_in_vocab + 1 + i
            ids = merge(ids, pair, idx)
            self.merges[pair] = idx

    def encode(self, text):
        tokens = list(text.encode("utf=8"))

        for pair in self.merges:
            i = 0
            new_tokens = []
            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
                    new_tokens.append(self.merges.get(pair))
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1

            tokens = new_tokens
        return tokens

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
