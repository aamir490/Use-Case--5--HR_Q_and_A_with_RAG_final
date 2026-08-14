import boto3
import json

client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

# Test 1: Titan Embeddings
print("=== Test 1: Titan Embedding Model ===")
response = client.invoke_model(
    modelId="amazon.titan-embed-text-v1",
    body=json.dumps({"inputText": "Hello AWS"}),
    contentType="application/json",
    accept="application/json"
)
result = json.loads(response["body"].read())
print("Token Count:", result["inputTextTokenCount"])
print("Embedding Length:", len(result["embedding"]))
print("First 5 values:", result["embedding"][:5])

# Test 2: Claude 3.5 Haiku (active model)
print("\n=== Test 2: Claude 3.5 Haiku LLM ===")
body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "messages": [
        {"role": "user", "content": "What is AWS Bedrock in one sentence?"}
    ]
})
response = client.invoke_model(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    body=body,
    contentType="application/json",
    accept="application/json"
)
result = json.loads(response["body"].read())
print("Response:", result["content"][0]["text"])

# python titien_model_test.py
