# -*- coding: utf-8 -*-
import sys
import os
import json
import time
import asyncio

# Set environment
os.environ['PYTHONPATH'] = r'c:/Users/Usuario/_clean/agent-skills'
os.environ['AGENT_SKILLS_RUNTIME_ROOT'] = r'c:/Users/Usuario/_clean/agent-skills'
os.environ['AGENT_SKILLS_HOST_ROOT'] = r'c:/Users/Usuario/_clean/agent-skills'
os.environ['AGENT_SKILLS_REGISTRY_ROOT'] = r'c:/Users/Usuario/_clean/agent-skill-registry'

sys.path.append(os.environ['PYTHONPATH'])

try:
    from official_mcp_servers.server import call_tool
except ImportError as e:
    print(json.dumps({"error": f"ImportError: {e}"}))
    sys.exit(1)

async def run_execution(run_idx):
    start_time = time.time()
    goal = 'Necesito decidir si debemos lanzar un nuevo producto SaaS para equipos legales en Espa\u00f1a durante los pr\u00f3ximos 12 meses.'
    context_items = [
        'Presupuesto disponible: 600000 EUR',
        'Equipo disponible: 5 personas',
        'Opciones a evaluar: construir producto completo, lanzar piloto/MVP, posponer',
        'Tenemos experiencia en SaaS B2B',
        'No tenemos experiencia en legaltech',
        'Existe competencia establecida',
        'Mercado objetivo: Espa\u00f1a',
        'Horizonte temporal: pr\u00f3ximos 12 meses'
    ]
    flags = {'_async': True, '_include_diagnostics': True}

    result = {
        "run": run_idx,
        "status": "failed",
        "run_id": None,
        "initial_shape": None,
        "duration_s": 0,
        "fallback_used": False,
        "fallback_steps_count": 0,
        "confidence_score": 0.0,
        "confidence_level": "N/A",
        "summary_confidence_score": 0.0,
        "summary_confidence_level": "N/A",
        "recommendation_present": False
    }

    try:
        args_dict = {'goal': goal, 'context_items': context_items, 'flags': flags}
        response = await call_tool('skill.decision.make', args_dict)
        
        # Determine if response is a tool result (often has 'content' or is a specific object)
        # We need to handle the case where response might be an object with .content or a dict
        
        resp_obj = response
        if hasattr(response, 'model_dump'):
            resp_obj = response.model_dump()
        
        result["initial_shape"] = str(resp_obj)[:500]
        
        def find_run_id(obj):
            if isinstance(obj, dict):
                if 'run_id' in obj: return obj['run_id']
                if '_run' in obj and 'run_id' in obj['_run']: return obj['_run']['run_id']
                for v in obj.values():
                    res = find_run_id(v)
                    if res: return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_run_id(item)
                    if res: return res
            return None
        
        run_id = find_run_id(resp_obj)
        result["run_id"] = run_id
        final_response = resp_obj
        
        if run_id:
            poll_count = 0
            while poll_count < 100:
                await asyncio.sleep(2)
                poll_count += 1
                status_resp = await call_tool('run.status', {'run_id': run_id})
                
                s_resp_obj = status_resp
                if hasattr(status_resp, 'model_dump'):
                    s_resp_obj = status_resp.model_dump()
                
                status = 'unknown'
                # Check for status field
                if isinstance(s_resp_obj, dict):
                    status = s_resp_obj.get('status', 'running')
                    if 'content' in s_resp_obj:
                         for c in s_resp_obj['content']:
                            if isinstance(c, dict) and 'text' in c:
                                try:
                                    t_data = json.loads(c['text'])
                                    if 'status' in t_data: status = t_data['status']
                                except: pass
                
                if status in ['completed', 'failed', 'canceled']:
                    final_response = s_resp_obj
                    result["status"] = status
                    break
        else:
            result["status"] = "completed"
            final_response = resp_obj

        def extract_all(obj):
            found_data = {}
            if isinstance(obj, dict):
                found_data.update(obj)
                for v in obj.values():
                    found_data.update(extract_all(v))
            elif isinstance(obj, list):
                for item in obj:
                    found_data.update(extract_all(item))
            elif isinstance(obj, str):
                try:
                    d = json.loads(obj)
                    found_data.update(extract_all(d))
                except: pass
            return found_data

        all_extracted = extract_all(final_response)
        
        result['confidence_score'] = all_extracted.get('confidence_score', 0.0)
        result['confidence_level'] = all_extracted.get('confidence_level', "N/A")
        result['summary_confidence_score'] = all_extracted.get('summary_confidence_score', 0.0)
        result['summary_confidence_level'] = all_extracted.get('summary_confidence_level', "N/A")
        result['recommendation_present'] = any(k in all_extracted for k in ['recommendation', 'output', 'decision', 'analysis'])
        result['fallback_used'] = all_extracted.get('fallback_used', False)
        result['fallback_steps_count'] = all_extracted.get('fallback_steps_count', 0)

    except Exception as e:
        result["status"] = f"error: {str(e)}"
    
    result["duration_s"] = time.time() - start_time
    return result

async def main():
    results = []
    for i in range(1, 4):
        res = await run_execution(i)
        results.append(res)
        print(json.dumps(res))

    durations = sorted([r['duration_s'] for r in results])
    aggregate = {
        "completed_count": sum(1 for r in results if r['status'] == 'completed'),
        "total_runs": 3,
        "fallback_count": sum(1 for r in results if r['fallback_used']),
        "fallback_rate": sum(1 for r in results if r['fallback_used'])/3.0,
        "p50_duration_s": durations[1] if len(durations)>1 else (durations[0] if durations else 0),
        "p95_duration_s": durations[-1] if durations else 0,
        "confidence_levels": [r['confidence_level'] for r in results]
    }
    print(json.dumps(aggregate))

if __name__ == "__main__":
    asyncio.run(main())
