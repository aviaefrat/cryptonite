# Cryptonite: A Cryptic Crossword Benchmark for Extreme Ambiguity in Language

### tl;dr

A dataset of cryptic crosswords :black_large_square::white_large_square::detective:

### Paper

https://arxiv.org/pdf/2103.01242.pdf

### Abstract

Current NLP datasets targeting ambiguity can be solved by a native speaker with relative ease.
We present Cryptonite, a large-scale dataset based on _cryptic_ crosswords, which is both linguistically complex and naturally sourced.
Each example in Cryptonite is a _cryptic clue_, a short phrase or sentence with a misleading surface reading, whose solving requires disambiguating semantic, syntactic, and phonetic wordplays, as well as world knowledge.
Cryptic clues pose a challenge even for experienced solvers, though top-tier experts can solve them with almost 100% accuracy.
Cryptonite is a challenging task for current models; fine-tuning T5-Large on 470k cryptic clues achieves only 7.6% accuracy, on par with the accuracy of a rule-based clue solver (8.6%).

### Available on HuggingFace (:hugs:) Datasets:

##### Explore
https://huggingface.co/datasets/viewer/?dataset=cryptonite

##### Use
```python
!pip install datasets
from datasets import load_dataset
dataset = load_dataset('cryptonite')
```

### Alternative Title
Cryptonite: How I Stopped Worrying and Learned(?) to Love Ambiguity :black_large_square::white_large_square::detective:
