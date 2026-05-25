import os
import yaml

base_path = r"c:\Users\Usuario\agent-skill-registry\capabilities"
ids_cognitive = []
deprecated_info = []
all_ids = set()

for filename in os.listdir(base_path):
    if filename.endswith(".yaml"):
        file_path = os.path.join(base_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if not data or not isinstance(data, dict):
                    continue
                skill_id = data.get("id")
                if not skill_id:
                    continue
                all_ids.add(skill_id)
                
                metadata = data.get("metadata", {})
                if not isinstance(metadata, dict):
                    continue
                    
                if metadata.get("layer") == "cognitive":
                    ids_cognitive.append(skill_id)
                
                if metadata.get("status") == "deprecated":
                    deprecated_info.append((skill_id, metadata.get("replacement")))
            except Exception as e:
                # Silently skip errors or handle them
                pass

print("1) Cognitive IDs (sorted):")
for i in sorted(ids_cognitive):
    print(i)

print("\n2) Deprecated IDs and replacements:")
for i, rep in sorted(deprecated_info):
    print(f"{i}: {rep}")

targets = [
    "evaluation.framework.detect",
    "evaluation.framework.rank",
    "reasoning.problem.decompose",
    "reasoning.plan.decompose",
    "perception.language.detect",
    "memory.context.compress",
    "reasoning.output.normalize"
]
print("\n3) Target existence:")
for t in targets:
    print(f"{t}: {'Yes' if t in all_ids else 'No'}")
