#!/usr/bin/env python3
"""Complete fix for README.md"""
import re

# Read lyrics from Lyrics.txt (lines 6-70, 0-indexed 5-69)
with open('Lyrics.txt', 'r', encoding='utf-8') as f:
    lyrics_lines = f.readlines()
song_content = ''.join(lyrics_lines[5:69]).rstrip()

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

# Step 1: Add audio link if not present
if 'Listen to the Algorithm' not in readme:
    readme = readme.replace(
        'This document serves as a conceptual and technical map for the data pipeline and model logic.\n\n---',
        'This document serves as a conceptual and technical map for the data pipeline and model logic.\n\n🎵 **Listen to the Algorithm:** [The Portability Formula on SoundCloud](https://soundcloud.com/orion-vale-523406667/the-portability-formula)\n\n---'
    )
    print("✓ Added audio link")

# Step 2: Replace song lyrics
pattern = r'(## 📊 The Portability Formula \(Algorithm\)\n\n)(.*?)(\n\n\*\*Research Context)'
updated_readme = re.sub(pattern, r'\1' + song_content + r'\3', readme, flags=re.DOTALL)

if updated_readme != readme:
    print("✓ Updated song lyrics")
else:
    print("⚠ Song lyrics unchanged (pattern may not have matched)")

# Write back
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(updated_readme)

print("✓ README.md update complete!")
