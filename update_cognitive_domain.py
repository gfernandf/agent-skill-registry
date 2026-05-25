import os
import yaml
import re
from collections import Counter

directory = 'capabilities'
files = [f for f in os.listdir(directory) if f.endswith('.yaml') and f != '_index.yaml']

counts = Counter()
changed_count = 0

for filename in files:
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        data = yaml.safe_load(content)
    except Exception as e:
        continue
    
    if not data or 'metadata' not in data or data['metadata'].get('layer') != 'cognitive':
        continue
    
    id_val = str(data.get('id', ''))
    role = str(data.get('cognitive_hints', {}).get('role', ''))
    
    if id_val.startswith(('provenance.', 'ops.trace.')):
        expected_domain = 'evidence'
    elif id_val.startswith('memory.'):
        expected_domain = 'memory'
    elif role == 'perceive':
        expected_domain = 'perception'
    elif role in ('synthesize', 'analyze'):
        expected_domain = 'reasoning'
    elif role in ('evaluate', 'reflect'):
        expected_domain = 'evaluation'
    elif role == 'decide':
        expected_domain = 'decision'
    else:
        expected_domain = 'reasoning'
    
    counts[expected_domain] += 1
    
    metadata_match = re.search(r'^metadata:', content, re.MULTILINE)
    if not metadata_match:
        continue

    metadata_start = metadata_match.start()
    next_top_level = re.search(r'^\S', content[metadata_start+1:], re.MULTILINE)
    if next_top_level:
        metadata_end = metadata_start + 1 + next_top_level.start()
    else:
        metadata_end = len(content)
    
    metadata_block = content[metadata_start:metadata_end]
    
    new_line = f'  cognitive_domain: {expected_domain}'
    modified = False
    if 'cognitive_domain:' in metadata_block:
        pattern = r'(^[ \t]+cognitive_domain:)\s*.*'
        match = re.search(pattern, metadata_block, re.MULTILINE)
        if match:
            old_line = match.group(0)
            if old_line.strip() != new_line.strip():
                new_metadata_block = re.sub(pattern, rf'\1 {expected_domain}', metadata_block, flags=re.MULTILINE)
                modified = True
            else:
                new_metadata_block = metadata_block
        else:
            new_metadata_block = metadata_block
    else:
        # Insert after metadata: line
        new_metadata_block = metadata_block.replace('metadata:', f'metadata:\n{new_line}', 1)
        modified = True
    
    if modified:
        new_content = content[:metadata_start] + new_metadata_block + content[metadata_end:]
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(new_content)
        changed_count += 1

print(f"Changed files: {changed_count}")
print("Final distribution counts:")
for dom in sorted(counts.keys()):
    print(f"{dom}: {counts[dom]}")
