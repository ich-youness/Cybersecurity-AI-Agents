import numpy as np
import pandas as pd
from collections import defaultdict
import random
import pickle

class MarkovModel:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(lambda: defaultdict(int))

    def train(self, sequences):
        for sequence in sequences:
            padded_sequence = ['<START>'] * self.order + list(sequence) + ['<END>']
            for i in range(len(padded_sequence) - self.order):
                n_gram = tuple(padded_sequence[i:i + self.order])
                next_item = padded_sequence[i + self.order]
                self.model[n_gram][next_item] += 1

        # Convert counts to probabilities
        for n_gram, next_items in self.model.items():
            total_count = sum(next_items.values())
            for next_item in next_items:
                next_items[next_item] /= total_count

    def generate(self, length=10):
        current_n_gram = tuple(['<START>'] * self.order)
        output = []

        for _ in range(length):
            next_items = self.model[current_n_gram]
            if not next_items:
                break
            next_item = random.choices(list(next_items.keys()), weights=next_items.values())[0]
            if next_item == '<END>':
                break
            output.append(next_item)
            current_n_gram = current_n_gram[1:] + (next_item,)

        return ''.join(output)

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f.readlines()]

def main():
    # Load the RockYou dataset
    data = load_data('../data/raw/rockyou.txt')
    
    # Train the Markov Model
    markov_model = MarkovModel(order=2)
    markov_model.train(data)

    # Save the trained model
    with open('../models/markov_model/model.pkl', 'wb') as f:
        pickle.dump(markov_model, f)

if __name__ == "__main__":
    main()