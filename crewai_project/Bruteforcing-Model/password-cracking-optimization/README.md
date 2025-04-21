# Password Cracking Optimization Project

This project implements password cracking optimization using machine learning techniques, specifically training a Markov Model and a Generative Adversarial Network (GAN) on the RockYou.txt dataset to predict likely passwords. The generated passwords can be integrated with popular password cracking tools such as Hashcat and John the Ripper.

## Project Structure

- **data/**: Contains the datasets used in the project.
  - **raw/**: Raw datasets, including the RockYou password dataset.
  - **processed/**: Processed outputs, such as generated passwords.
  
- **models/**: Contains the trained models.
  - **markov_model/**: Trained Markov Model for password prediction.
  - **gan/**: Trained GAN model and its components (generator and discriminator).
  
- **src/**: Source code for data processing, model training, and integration with password cracking tools.
  - **data_preprocessing.py**: Functions for cleaning and formatting the RockYou dataset.
  - **train_markov_model.py**: Implementation for training the Markov Model.
  - **train_gan.py**: Implementation for training the GAN.
  - **integrate_hashcat.py**: Integration functionality for Hashcat.
  - **integrate_john.py**: Integration functionality for John the Ripper.
  - **utils/**: Utility functions and helper methods.
  
- **notebooks/**: Jupyter notebooks for data exploration and model training documentation.
  - **data_exploration.ipynb**: Notebook for exploring the RockYou dataset.
  - **model_training.ipynb**: Notebook for training the models and documenting results.
  
- **requirements.txt**: Lists the dependencies required for the project.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd password-cracking-optimization
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download the RockYou password dataset and place it in the `data/raw/` directory.

## Usage

- To preprocess the dataset, run:
  ```
  python src/data_preprocessing.py
  ```

- To train the Markov Model, run:
  ```
  python src/train_markov_model.py
  ```

- To train the GAN, run:
  ```
  python src/train_gan.py
  ```

- To integrate the generated password list with Hashcat, run:
  ```
  python src/integrate_hashcat.py
  ```

- To integrate the generated password list with John the Ripper, run:
  ```
  python src/integrate_john.py
  ```

## Goals

The primary goal of this project is to enhance password cracking techniques by leveraging machine learning models to generate likely passwords based on historical data. By integrating these models with existing password cracking tools, we aim to improve the efficiency and effectiveness of password recovery efforts.

## Acknowledgments

- The RockYou dataset for providing a comprehensive list of passwords.
- The developers of Hashcat and John the Ripper for their contributions to password cracking tools.