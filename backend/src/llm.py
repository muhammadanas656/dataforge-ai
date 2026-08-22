import os
from pathlib import Path
from importlib import import_module
from dotenv import load_dotenv
from src.token_tracker import tracker
from src.utils import logger

# Load environment configuration from specified path first, fallback to local .env
env_path = Path(r"C:\skills development\learning datascience\system 1\The Data Intelligence Platform being built\.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

def get_client(custom_provider=None, custom_key=None, custom_model=None):
    # Check settings.json for persisted user settings
    settings = {}
    if os.path.exists("data/settings.json"):
        try:
            import json
            settings = json.load(open("data/settings.json", encoding="utf-8"))
        except Exception:
            pass

    provider = (custom_provider or os.getenv("api_provider") or settings.get("provider") or "groq").lower()
    key = custom_key or os.getenv("api_key") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.get("api_key")
    model = custom_model or os.getenv("api_model") or settings.get("model") or ("openai/gpt-oss-20b" if provider == "groq" else "gpt-4o-mini")

    try:
        mod = import_module(provider)
        ClientClass = getattr(mod, provider.title())
        client = ClientClass(api_key=key)
        return client, model
    except Exception as e:
        logger.warning(f"[llm] Could not instantiate provider '{provider}': {e}")
        # Fallback to groq if available
        import groq
        return groq.Groq(api_key=key), model


def test_connection(provider: str, api_key: str, model: str) -> dict:
    """Live test credentials and measure LLM latency."""
    import time
    start = time.time()
    try:
        client, target_model = get_client(custom_provider=provider, custom_key=api_key, custom_model=model)
        resp = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": "Respond with 'OK'"}],
            max_tokens=5
        )
        latency_ms = round((time.time() - start) * 1000, 2)
        content = resp.choices[0].message.content.strip()
        return {
            "status": "success",
            "provider": provider,
            "model": target_model,
            "latency_ms": latency_ms,
            "response": content
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": provider,
            "model": model,
            "message": str(e)
        }


def tracked_chat(run_id, stage, agent, messages, **kwargs):
    client, model = get_client()
    try:
        resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
        u = resp.usage
        pt = getattr(u, "prompt_tokens", 0) if u else 0
        ct = getattr(u, "completion_tokens", 0) if u else 0
        tracker.record(run_id, stage, agent, model, pt, ct)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"[llm] API call failed in tracked_chat: {e}")
        tracker.record(run_id, stage, agent, model or "fallback", 0, 0, cached=1, saved=250)
        raise e


import asyncio


async def tracked_stream_chat(run_id, stage, agent, messages, temperature=0.2, max_tokens=400):
    """
    Bridges sync LLM streaming to an async generator for FastAPI SSE.
    Records accumulated prompt & completion tokens into TokenTracker.
    """
    client, model = get_client()
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    # Estimate prompt tokens (~4 chars per token)
    prompt_str = " ".join(m.get("content", "") for m in messages)
    pt = max(1, len(prompt_str) // 4)

    def _run_sync_stream():
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            completion_acc = []
            for chunk in stream:
                delta = getattr(chunk.choices[0].delta, "content", "") or ""
                if delta:
                    completion_acc.append(delta)
                    asyncio.run_coroutine_threadsafe(queue.put({"delta": delta}), loop)
            
            # Record accumulated tokens in global TokenTracker
            full_completion = "".join(completion_acc)
            ct = max(1, len(full_completion) // 4)
            tracker.record(run_id, stage, agent, model, pt, ct)
            asyncio.run_coroutine_threadsafe(queue.put({"done": True, "prompt_tokens": pt, "completion_tokens": ct}), loop)
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(queue.put(e), loop)

    loop.run_in_executor(None, _run_sync_stream)

    while True:
        item = await queue.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item


