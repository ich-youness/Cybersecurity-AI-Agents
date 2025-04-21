import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LeakyReLU
from keras.optimizers import Adam
from keras import initializers

# Load the processed password data
def load_data(file_path):
    return pd.read_csv(file_path)

# Define the generator model
def build_generator(latent_dim):
    model = Sequential()
    model.add(Dense(256, input_dim=latent_dim, kernel_initializer=initializers.RandomNormal(stddev=0.02)))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1024))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1, activation='sigmoid'))  # Output layer for password generation
    return model

# Define the discriminator model
def build_discriminator():
    model = Sequential()
    model.add(Dense(512, input_dim=1, kernel_initializer=initializers.RandomNormal(stddev=0.02)))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1, activation='sigmoid'))  # Output layer for classification
    return model

# Compile the GAN model
def compile_gan(generator, discriminator):
    discriminator.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5), metrics=['accuracy'])
    discriminator.trainable = False  # Freeze the discriminator when training the generator
    gan_input = Sequential()
    gan_input.add(generator)
    gan_input.add(discriminator)
    gan_input.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5))
    return gan_input

# Train the GAN
def train_gan(epochs, batch_size, latent_dim, data):
    generator = build_generator(latent_dim)
    discriminator = build_discriminator()
    gan = compile_gan(generator, discriminator)

    for epoch in range(epochs):
        # Train the discriminator
        idx = np.random.randint(0, data.shape[0], batch_size)
        real_passwords = data[idx]
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        generated_passwords = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(real_passwords, np.ones((batch_size, 1)))
        d_loss_fake = discriminator.train_on_batch(generated_passwords, np.zeros((batch_size, 1)))
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # Train the generator
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        g_loss = gan.train_on_batch(noise, np.ones((batch_size, 1)))

        # Print the progress
        if epoch % 100 == 0:
            print(f"{epoch} [D loss: {d_loss[0]:.4f}, acc.: {100 * d_loss[1]:.2f}%] [G loss: {g_loss:.4f}]")

    # Save the trained models
    generator.save('models/gan/generator.h5')
    discriminator.save('models/gan/discriminator.h5')

if __name__ == "__main__":
    data = load_data('data/processed/passwords.csv').values
    train_gan(epochs=10000, batch_size=64, latent_dim=100, data=data)