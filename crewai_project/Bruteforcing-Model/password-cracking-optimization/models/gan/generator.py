from keras.models import Sequential
from keras.layers import Dense, LeakyReLU, Reshape, Flatten
import numpy as np

class PasswordGenerator:
    def __init__(self, input_dim, output_dim):
        self.model = self.build_generator(input_dim, output_dim)

    def build_generator(self, input_dim, output_dim):
        model = Sequential()
        model.add(Dense(128, input_dim=input_dim))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(256))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(output_dim, activation='sigmoid'))
        model.add(Reshape((output_dim,)))
        return model

    def generate(self, noise):
        return self.model.predict(noise)

    def train(self, noise, passwords):
        self.model.compile(loss='binary_crossentropy', optimizer='adam')
        self.model.fit(noise, passwords, epochs=100, batch_size=32)

# Example usage:
# generator = PasswordGenerator(input_dim=100, output_dim=20)
# noise = np.random.normal(0, 1, (1, 100))
# generated_password = generator.generate(noise)