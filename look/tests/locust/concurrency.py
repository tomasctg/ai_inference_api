from locust import HttpUser, task

class OpenAIMockTest(HttpUser):
    @task
    def load(self):
        # Equivalent to your curl command
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Send the POST request
        response = self.client.post("/v1/chat/completions", json=payload, headers=headers)
        
        print(response.text)
        # Optionally, print the response or perform assertions
        assert response.status_code == 200