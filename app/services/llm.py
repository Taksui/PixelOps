import random
import time

def fake_llm(query: str):
    time.sleep(random.uniform(0.1, 0.5))

    if random.random() < 0.3:
        return {"temp": 32}  # wrong format

    return {"temperature": 32}