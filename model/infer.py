from datetime import datetime, timedelta
import json
import os
import sys
import time
import random
import logging
import dotenv

from model.FABSA import FABSA


dotenv.load_dotenv()

from caching.cache_inference import cache_inference
logging.basicConfig(
    level=logging.INFO,
    format="%(process)d %(name)s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        List[str | dict] (mocked outputs)
    """

    if model_id == "mock":
        logger.info(f"[Model] Inferring batch of {len(batch_inputs)} inputs for model {model_id}")
        # Simulate variable latency (e.g., 10-20 seconds)
        processing_time = random.uniform(10, 15)
        time.sleep(processing_time)

        # Simulate GPU-style memory limit (e.g., max 4 inputs)
        if len(batch_inputs) > 4:
            raise MemoryError("Simulated OOM: batch too large for mock model")

        # Simulate occasional model failure (10% failure chance)
        if random.random() < 0.3:
            raise InferenceFailure("Mock inference failure")

        # Mocked output: just echoing uppercase + model_id
        outputs = [f"[{model_id}] " + input_text.upper() for input_text in batch_inputs]
        return outputs
    elif model_id == "fabsa":
        outputs = []
        default_current_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        default_from_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        default_num_news = 50
        for input_text in batch_inputs:
            fabsa = FABSA(
                entity = input_text,
                api_key = os.getenv("NEWS_API"),
                from_date = default_from_date,
                to_date = default_current_date,
                num_news = default_num_news
            )
            res = fabsa.predict_sentiment()
            # stringify the dict (json)
            res_str = json.dumps(res)
            outputs.append(res_str)
        return outputs