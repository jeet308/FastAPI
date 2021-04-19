from locust import HttpUser, task, between
import os
import random

file_path = 'test2.jpg'


class QuickstartUser(HttpUser):
    wait_time = between(3, 10)

    @task
    def test_api(self):
        files = {'image_file':  open(file_path, 'rb')}
        data = {"reference_id": "bbbb22",
                "company_name": "frslabs",
                "resize_width": 75,
                "resize_height": None,
                "image_format": "png",
                "quality_check": True}
        #result = self.client.post("/test/normal",files=files,data=data)
        #result = self.client.post("/test/shutil",files=files,data=data)
        result = self.client.post("/test/aiof",files=files,data=data)

        print(result.text)
        print(f"status: {result.status_code}")
