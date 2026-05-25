import os
import re
import json
import pathlib

def migrate():
    base_path = pathlib.Path(".")
    capabilities_path = base_path / "capabilities"
    
    mapping = {}
    cognitive_files = []
    
    # 1. Read capabilities/*.yaml excluding _index.yaml
    for yaml_file in capabilities_path.glob("*.yaml"):
        if yaml_file.name == "_index.yaml":
            continue
            
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
            
        # 2. Check for metadata.layer == cognitive
        layer_match = re.search(r"layer:\s*cognitive", content)
        domain_match = re.search(r"cognitive_domain:\s*(\w+)", content)
        id_match = re.search(r"^id:\s*([\w\.]+)", content, re.MULTILINE)
        
        if layer_match and domain_match and id_match:
            old_id = id_match.group(1)
            domain = domain_match.group(1)
            
            # id tail (everything after first segment)
            parts = old_id.split(".")
            tail = ".".join(parts[1:]) if len(parts) > 1 else old_id
            new_id = f"{domain}.{tail}"
            
            mapping[old_id] = new_id
            cognitive_files.append((yaml_file, old_id, new_id, domain))

    # 3. Rename capability files, update id field, and remove cognitive_domain
    for yaml_file, old_id, new_id, domain in cognitive_files:
        with open(yaml_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Update id:
        content = re.sub(r"^id:\s*" + re.escape(old_id), f"id: {new_id}", content, flags=re.MULTILINE)
        
        # Remove cognitive_domain line (and following newline)
        content = re.sub(r"^\s*cognitive_domain:.*\n?", "", content, flags=re.MULTILINE)
        
        # Write back
        new_file_path = capabilities_path / f"{new_id}.yaml"
        
        with open(new_file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
            
        if new_file_path.resolve() != yaml_file.resolve():
            yaml_file.unlink()

    if not mapping:
        print("No cognitive capabilities found or already processed.")
        # We still want to check vocabulary and maybe references if mapping was found in a previous run?
        # But if it's already processed, the mapping is gone.
        # Let's assume we need to run it once.
    else:
        # 4. Update text references old_id -> new_id across paths
        search_paths = ["capabilities", "skills", "docs", "tools", "vocabulary"]
        root_files = ["README.md", "CHANGELOG.md"]
        skip_dirs = {".venv", "catalog", "artifacts", "test_results"}
        
        sorted_mapping = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)
        
        def update_references(text):
            for old, new in sorted_mapping:
                text = text.replace(old, new)
            return text

        for p in search_paths:
            path_obj = base_path / p
            if not path_obj.exists(): continue
            for root, dirs, files in os.walk(path_obj):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                for file in files:
                    fpath = pathlib.Path(root) / file
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                        new_content = update_references(content)
                        if new_content != content:
                            with open(fpath, "w", encoding="utf-8", newline="\n") as f:
                                f.write(new_content)
                    except (UnicodeDecodeError, PermissionError):
                        continue

        for rf in root_files:
            rf_path = base_path / rf
            if rf_path.exists():
                try:
                    with open(rf_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    new_content = update_references(content)
                    if new_content != content:
                        with open(rf_path, "w", encoding="utf-8", newline="\n") as f:
                            f.write(new_content)
                except Exception:
                    pass

    # 5. Update vocabulary/vocabulary.json
    vocab_path = base_path / "vocabulary" / "vocabulary.json"
    if vocab_path.exists():
        with open(vocab_path, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        
        if "domains" not in vocab:
            vocab["domains"] = {}
        
        # Ensure it's a dict
        if isinstance(vocab["domains"], list):
             # Convert if it was a list for some reason, though we saw it's a dict
             vocab["domains"] = {d: d.capitalize() for d in vocab["domains"]}

        required_domains = ["perception", "reasoning", "evaluation", "decision", "evidence", "memory"]
        for d in required_domains:
            if d not in vocab["domains"]:
                vocab["domains"][d] = d.capitalize()
        
        with open(vocab_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(vocab, f, indent=2)

    # 6. Summary
    print(f"Cognitive capabilities processed: {len(cognitive_files)}")
    print(f"Number renamed: {sum(1 for f, oid, nid, d in cognitive_files if oid != nid)}")
    if mapping:
        print("First 20 mappings:")
        for old, new in list(mapping.items())[:20]:
            print(f"  {old} -> {new}")

if __name__ == "__main__":
    migrate()
