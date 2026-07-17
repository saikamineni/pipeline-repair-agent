import time

import anthropic
from agent.tools import TOOLS, TOOL_IMPLS
from agent.prompts import SYSTEM

import os
from dotenv import load_dotenv   # pip install python-dotenv


load_dotenv()
client = anthropic.Anthropic(
    api_key=os.environ["PIPELINE_AGENT_ANTHROPIC_KEY"])
MODEL = "claude-sonnet-4-6"

MAX_TOOL_RESULT = 6000




def run_agent(task: str, max_iters: int = 25):
    messages = [{"role": "user", "content": task}]
    for i in range(max_iters):
        set_cache_breakpoint(messages)
        resp = client.messages.create(model=MODEL, max_tokens=2000, system=[{"type" : "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}], tools=TOOLS, messages=messages)
        # time.sleep(3)
        # print(resp.usage)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return {"done": True, "iters": i+1, "messages": messages}
        results = []
        for block in resp.content:
            # if block.type == "text" and block.text.strip():
            #     print(f"\n[iter {i+1}] THINKING: {block.text[:300]}")
            # if block.type == "tool_use":
            #     arg = str(block.input)[:120]
            #     print(f"[iter {i+1}] TOOL: {block.name}({arg})")
            if block.type == "tool_use":
                try:
                    out = TOOL_IMPLS[block.name](**block.input)
                    out = str(out)
                    if len(out) > MAX_TOOL_RESULT:
                        out = out[:MAX_TOOL_RESULT] + f"\n...[truncated from {len(out)} chars]"
                except Exception as e:
                    out = f"TOOL ERROR: {e}"
                    print("Failed with Tool error")
                except RateLimitError as e:
                    wait = int(e.response.headers.get("retry-after", 60))
                    print(f"[rate-limited] server says wait {wait}s")
                    time.sleep(min(wait, 300))
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(out)})
        messages.append({"role": "user", "content": results})
    return {"done": False, "iters": max_iters, "messages": messages}


def set_cache_breakpoint(messages):
    for m in messages:
        if isinstance(m["content"], list):
            for block in m["content"]:
                    if isinstance(block, dict):
                        block.pop("cache_control", None)
    
    last = messages[-1]

    if isinstance(last["content"], list) and last["content"]:
        last["content"][-1]["cache_control"] = {"type": "ephemeral"}