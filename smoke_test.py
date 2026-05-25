import asyncio
import json
import time
import sys
import os

# Ensure the clean paths are in sys.path
# Although PYTHONPATH is set, we can be explicit if needed.

try:
    from official_mcp_servers.server import call_tool
except ImportError as e:
    print(f"Error importing official_mcp_servers: {e}")
    sys.exit(1)

async def poll_run(run):
    start_time = time.time()
    timeout = 300
    while time.time() - start_time < timeout:
        status = getattr(run, "status", None)
        if status is None and isinstance(run, dict):
            status = run.get("status")
        
        if status in ["completed", "failed", "cancelled", "success", "error"]:
            return run
        
        await asyncio.sleep(2)
        
        # If it is a dict, we likely need to fetch the updated state
        if isinstance(run, dict) and "id" in run:
            run = await call_tool("skill.runtime.get_run", {"run_id": run["id"]})
        elif hasattr(run, "refresh"):
            await run.refresh()
            
    return run

async def main():
    # decision.make usually requires a 'goal' or 'objective'. 
    # I'll provide a dummy one if it complains, but let's try with just the requested flags first.
    # Actually, most decision tools need a "plan" or "context". 
    # Given it's a smoke test, I'll use a simple goal.
    args = {
        "goal": "Smoke test execution",
        "_async": True,
        "_include_diagnostics": True
    }
    
    try:
        run = await call_tool("skill.decision.make", args)
        final_run = await poll_run(run)
        
        # Extract data
        # Required: status, fallback_used, fallback_steps_count, confidence_score, 
        # confidence_level, outputs_summary confidence fields, and recommendation present boolean.
        
        # Handle both object and dict
        def get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        res = get_val(final_run, "result", {})
        diag = get_val(final_run, "diagnostics", {})
        
        # The prompt asks for "outputs_summary confidence fields" - 
        # usually these are in the result or diagnostics.
        
        output = {
            "status": get_val(final_run, "status"),
            "fallback_used": get_val(res, "fallback_used"),
            "fallback_steps_count": get_val(res, "fallback_steps_count"),
            "confidence_score": get_val(res, "confidence_score"),
            "confidence_level": get_val(res, "confidence_level"),
            "outputs_summary_confidence": get_val(res, "outputs_summary", {}).get("confidence"), # heuristic
            "recommendation_present": get_val(res, "recommendation") is not None
        }
        
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
