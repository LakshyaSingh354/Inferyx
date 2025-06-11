import logging
from infer import infer_batch, InferenceFailure

logging.basicConfig(level=logging.INFO)

batch = ["hello world", "this is a test", "simulating a batch of inputs", "this is another test", "this is a third test"]

try:
    result = infer_batch(batch, model_id="mock-v1")
    logging.info("RESULT: %s", result)
except InferenceFailure as e:
    logging.error("FAILURE: %s", str(e))
except MemoryError as e:
    logging.error("OOM: %s", str(e))