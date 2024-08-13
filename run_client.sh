curl http://127.0.0.1:8000/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
