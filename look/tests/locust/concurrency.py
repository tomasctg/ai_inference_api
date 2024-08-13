from locust import HttpUser, task

class OpenAIMockTest(HttpUser):
    @task
    def load(self):
        # Equivalent to your curl command
        payload = {
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
            ],
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        with self.client.post("/v1/chat/completions", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code {response.status_code}")
