import hashlib
from functools import wraps

from job_queue.redis_client import get_redis_client

r = get_redis_client()


def make_cache_key(input_text, model_id):
    raw = f"{model_id}:{input_text}"
    return "inference_cache:" + hashlib.sha256(raw.encode()).hexdigest()

def cache_inference(fn):
    @wraps(fn)
    def wrapper(batch_inputs, model_id="mock"):
        result_map = {}
        to_infer_inputs = []
        to_infer_indices = []
        cache_keys = []

        for idx, input_text in enumerate(batch_inputs):
            key = make_cache_key(input_text, model_id)
            cached_result = r.get(key)
            if cached_result:
                result_map[idx] = cached_result.decode()
            else:
                to_infer_inputs.append(input_text)
                to_infer_indices.append(idx)
                cache_keys.append(key)

        if to_infer_inputs:
            new_outputs = fn(to_infer_inputs, model_id)
            for idx, key, output in zip(to_infer_indices, cache_keys, new_outputs):
                r.set(key, output, ex=3600)
                result_map[idx] = output

        # Return ordered list of outputs
        return [result_map[i] for i in range(len(batch_inputs))]
    return wrapper