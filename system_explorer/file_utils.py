import os
import re
from collections import Counter

def find_common_terms(data, min_length=5, min_count=2):
    all_words = []
    for item in data:
        description = item['description'].lower()
        words = re.findall(r'\b\w+\b', description)
        all_words.extend([word for word in words if len(word) >= min_length])

    word_counts = Counter(all_words)
    common_terms = [word for word, count in word_counts.items() if count >= min_count]
    
    return common_terms

def group_files_by_functionality(data, common_terms):
    functionality_groups = {}
    for item in data:
        filename = item['filename']
        description = item['description']
        group = extract_functionality_group(filename)
        if group not in functionality_groups:
            functionality_groups[group] = []
        functionality_groups[group].append({'filename': filename, 'description': description})
    return functionality_groups

def extract_functionality_group(filename):
    directory_path = os.path.dirname(filename)
    functionality_group = os.path.basename(directory_path)
    return functionality_group.capitalize()
