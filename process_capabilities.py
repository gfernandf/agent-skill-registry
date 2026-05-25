import os
import yaml
from collections import Counter

directory = 'capabilities'
cognitive_counts = Counter()
total_cognitive = 0

for filename in os.listdir(directory):
    if filename.endswith('.yaml') and filename != '_index.yaml':
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'metadata' in data:
                    metadata = data['metadata']
                    if metadata.get('layer') == 'cognitive':
                        total_cognitive += 1
                        domain = metadata.get('cognitive_domain', 'unknown')
                        cognitive_counts[domain] += 1
        except Exception as e:
            # Silently skip errors or print them if needed
            pass

print("Counts by metadata.cognitive_domain:")
for domain, count in sorted(cognitive_counts.items()):
    print(f"{domain}: {count}")

print(f"\nTotal cognitive count: {total_cognitive}")
