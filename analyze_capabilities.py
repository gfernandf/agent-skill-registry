import yaml
import glob
import os
from collections import defaultdict

files = glob.glob("capabilities/*.yaml")
cognitive_skills = []

for file in files:
    if os.path.basename(file) == "_index.yaml":
        continue
    with open(file, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
            if data and data.get("metadata", {}).get("layer") == "cognitive":
                cognitive_skills.append(data)
        except Exception as e:
            print(f"Error parsing {file}: {e}")

grouped = defaultdict(list)
for skill in cognitive_skills:
    skill_id = skill.get("id", "")
    domain = skill_id.split(".")[0] if "." in skill_id else skill_id
    grouped[domain].append(skill_id)

total_count = len(cognitive_skills)
print(f"Total cognitive count: {total_count}")
print("\nCounts by domain:")
for domain in sorted(grouped.keys()):
    print(f"{domain}: {len(grouped[domain])}")

print("\nSorted IDs per domain:")
for domain in sorted(grouped.keys()):
    print(f"\n{domain}:")
    for skill_id in sorted(grouped[domain]):
        print(f"  - {skill_id}")
