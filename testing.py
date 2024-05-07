

import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Sample text for NER
text = "Apple is a technology company based in California. John works at Google in New York."

# Process the text using the loaded model
doc = nlp(text)

# Iterate over the entities in the processed text and print their labels and text
for ent in doc.ents:
    print(f"Label: {ent.label_}, Text: {ent.text}")