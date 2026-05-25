import json

with open('catalog/capabilities.json', 'r') as f:
    capabilities = json.load(f)

debatable = []
cog_domains = ['agent', 'analysis', 'decision', 'eval', 'model', 'text', 'provenance', 'ops.trace']
read_verbs = ['read', 'get', 'list', 'fetch', 'search', 'retrieve', 'inspect', 'analyze']
sec_domains = ['policy', 'security', 'identity', 'task']

for cap in capabilities:
    cid = cap.get('id', '')
    domain = cid.split('.')[0] if '.' in cid else cid
    if cid.startswith('ops.trace'): domain = 'ops.trace'
    
    props = cap.get('properties', {})
    side_effects = props.get('side_effects', False)
    state_access = props.get('state_access', 'none')
    audit_level = props.get('audit_level', 'basic')
    cog_hints = cap.get('cognitive_hints')
    
    entry = {
        'capability_id': cid,
        'domain': domain,
        'side_effects': side_effects,
        'state_access': state_access,
        'audit_level': audit_level
    }
    
    reason = None
    suggested = None
    severity = None

    if domain in cog_domains and audit_level == 'basic':
        severity = 'High'
        reason = 'Cognitive domain with basic audit'
        suggested = 'Upgrade to standard or strict'
    elif cog_hints and audit_level == 'basic':
        severity = 'Medium'
        reason = 'Has cognitive hints but basic audit'
        suggested = 'Upgrade to standard'
    elif domain in sec_domains and audit_level == 'standard':
        severity = 'Medium'
        reason = 'Security-sensitive domain with standard audit'
        suggested = 'Consider upgrade to strict'
    else:
        has_read_verb = any(v in cid.split('.')[-1] for v in read_verbs)
        if has_read_verb and state_access == 'none':
            severity = 'Low'
            reason = 'Read verb but state_access=none'
            suggested = 'Verify if state_access should be read'

    if severity:
        entry.update({'severity': severity, 'why_debatable': reason, 'suggested_change': suggested})
        debatable.append(entry)

debatable.sort(key=lambda x: ['High', 'Medium', 'Low'].index(x['severity']))
subset = debatable[:35]

print('| severity | capability_id | domain | side_effects | state_access | audit_level | why_debatable | suggested_change |')
print('|---|---|---|---|---|---|---|---|')
for row in subset:
    vals = [str(row[k]) for k in ['severity', 'capability_id', 'domain', 'side_effects', 'state_access', 'audit_level', 'why_debatable', 'suggested_change']]
    print(f"| {' | '.join(vals)} |")
