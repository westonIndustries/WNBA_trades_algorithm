#!/usr/bin/env python3
"""Clean up README.md and add glossary reference"""
import re

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove duplicate headers and clean up the song section
# Find the first occurrence of the intro
intro_end = content.find('---\n', content.find('This document serves'))

# Find where the song section should start (after duplicates)
song_start_marker = '## 📊 The Portability Formula (Algorithm)'
song_start = content.find(song_start_marker)

# Find where Model Requirements section starts
model_req_marker = '## 📋 Model Requirements & Logic'
model_req_start = content.find(model_req_marker)

if song_start == -1 or model_req_start == -1:
    print("⚠ Could not find expected sections")
    exit(1)

# Extract the three main parts
intro = content[:intro_end + 4]  # Include the ---\n
song_section = content[song_start:model_req_start]
rest_of_doc = content[model_req_start:]

# Add audio link to intro if not present
if 'Listen to the Algorithm' not in intro:
    intro = intro.replace(
        'This document serves as a conceptual and technical map for the data pipeline and model logic.\n\n---',
        'This document serves as a conceptual and technical map for the data pipeline and model logic.\n\n🎵 **Listen to the Algorithm:** [The Portability Formula on SoundCloud](https://soundcloud.com/orion-vale-523406667/the-portability-formula)\n\n---'
    )

# Add glossary reference after the formula variables
glossary_ref = '\n\nFor detailed definitions of all variables and technical terms, see the [Technical Glossary](GLOSSARY.md).\n'

# Find where to insert glossary reference (after the formula variables list)
formula_end = rest_of_doc.find('For a complete breakdown')
if formula_end == -1:
    # Try to find after the variable definitions
    formula_end = rest_of_doc.find('\n\n', rest_of_doc.find('Team Value Lift'))
    
if formula_end > 0 and 'Technical Glossary' not in rest_of_doc[:formula_end + 200]:
    rest_of_doc = rest_of_doc[:formula_end] + glossary_ref + rest_of_doc[formula_end:]

# Reconstruct the README
cleaned_content = intro + '\n' + song_section + '\n' + rest_of_doc

# Write back
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(cleaned_content)

print("✓ README.md cleaned up and glossary reference added!")
