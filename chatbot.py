import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import re

class SafeXChatbot:
    def __init__(self, intents_file='data/intents.json'):
        with open(intents_file, 'r') as file:
            data = json.load(file)
        
        self.intents = data['intents']
        
        # ML: Prepare training data
        self.patterns = []
        self.tags = []
        self.responses = {}
        
        for intent in self.intents:
            tag = intent['tag']
            self.responses[tag] = intent['responses']
            for pattern in intent['patterns']:
                self.patterns.append(pattern.lower())
                self.tags.append(tag)
        
        # ML: TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.pattern_vectors = self.vectorizer.fit_transform(self.patterns)
        
        # ML: Label Encoder for tags
        self.label_encoder = LabelEncoder()
        self.encoded_tags = self.label_encoder.fit_transform(self.tags)
        
        print(f"✅ Chatbot trained on {len(self.patterns)} patterns across {len(self.responses)} intents")
    
    def preprocess(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s?]', '', text)
        return text
    
    def get_response(self, user_query):
        processed_query = self.preprocess(user_query)
        
        # ML: Convert query to TF-IDF vector
        query_vector = self.vectorizer.transform([processed_query])
        
        # ML: Calculate cosine similarity with all patterns
        similarities = cosine_similarity(query_vector, self.pattern_vectors)[0]
        
        # Get best match
        best_idx = np.argmax(similarities)
        confidence = similarities[best_idx] * 100
        matched_tag = self.tags[best_idx]
        
        if confidence > 45:  # Higher threshold = stricter matching:  # Threshold
            response = random.choice(self.responses[matched_tag])
            return {
                'answer': response,
                'confidence': round(confidence, 1),
                'matched_question': self.patterns[best_idx],
                'intent': matched_tag
            }
        else:
            # Fallback response
            fallback = random.choice(self.responses.get('unverified_fallback', 
                ["Please contact us at contact@safexsolutions.com for more information."]))
            return {
                'answer': fallback,
                'confidence': round(confidence, 1),
                'matched_question': "No close match found",
                'intent': 'fallback'
            }
    
    def get_suggestions(self):
        # Return unique intent examples as suggestions
        suggestions = []
        seen_tags = set()
        for intent in self.intents:
            if intent['tag'] not in seen_tags and intent['tag'] not in ['unverified_fallback', 'goodbye']:
                suggestions.append(intent['patterns'][0])
                seen_tags.add(intent['tag'])
                if len(suggestions) >= 5:
                    break
        return suggestions