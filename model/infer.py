import time
import random
import logging

from caching.cache_inference import cache_inference

logger = logging.getLogger(__name__)

class InferenceFailure(Exception):
    pass

@cache_inference
def infer_batch(batch_inputs, model_id="mock"):
    """
    Simulates batch inference with latency and occasional failures.

    Args:
        batch_inputs (List[str])
        model_id (str)

    Returns:
        List[str] (mocked outputs)
    """
    logger.info(f"[Model] Inferring batch of {len(batch_inputs)} inputs")
    # Simulate variable latency (e.g., 10-20 seconds)
    processing_time = random.uniform(2, 5)
    time.sleep(processing_time)

    # Simulate GPU-style memory limit (e.g., max 4 inputs)
    if len(batch_inputs) > 4:
        raise MemoryError("Simulated OOM: batch too large for mock model")

    # Simulate occasional model failure (10% failure chance)
    if random.random() < 0.1:
        raise InferenceFailure("Mock inference failure")

    # Mocked output: just echoing uppercase + model_id
    outputs = [f"[{model_id}] " + input_text.upper() for input_text in batch_inputs]
    return outputs