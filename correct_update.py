#!/usr/bin/env python3
"""Correct update to README.md with lyrics from Lyrics.txt"""

# Read lyrics
with open('Lyrics.txt', 'r', encoding='utf-8') as f:
    lyrics_lines = f.readlines()

# Get song content (lines 6-70, 0-indexed 5-69)
song_content = ''.join(lyrics_lines[5:69]).rstrip()

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

# Find and replace the song section
# Pattern: from after "## 📊 The Portability Formula (Algorithm)\n\n" to before "\n\n**Research Context"
import re

pattern = r'(## 📊 The Portability Formula \(Algorithm\)\n\n)(.*?)(\n\n\*\*Research Context)'
replacement = r'\1' + song_content + r'\3'

updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

# Write back
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(updated_readme)

print("✓ README.md updated with correct lyrics from Lyrics.txt!")
