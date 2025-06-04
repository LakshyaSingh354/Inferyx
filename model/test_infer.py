from infer import infer_batch, InferenceFailure

batch = ["hello world", "this is a test", "simulating a batch of inputs", "this is another test", "this is a third test"]

try:
    result = infer_batch(batch, model_id="mock-v1")
    print("RESULT:", result)
except InferenceFailure as e:
    print("FAILURE:", str(e))
except MemoryError as e:
    print("OOM:", str(e))