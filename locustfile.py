from locust import HttpUser, between, task

file_path = "/home/****/****/img/test.png"

payload = {
    "reference_id": "456ad8",
    "resize_width": "50",
    "company_name": "frslabs",
    "quality_check": "true",
    "image_format": "jpg",
}


class QuickstartUser(HttpUser):
    wait_time = between(5, 50)

    @task
    def shutil_save(self):
        files = {"image_file": ("image_file", open(file_path, "rb"), "image/jpeg")}
        result = self.client.post("/test", data=payload, files=files)

        http_code = result.status_code
        # print(f"status: {http_code}")
        # print(result.text)
        print(f"status: {result.status_code}")
        if http_code > 300:
            print(f"status: {http_code}")
            print(result.text)
