
import requests
import allure
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from core.settings.environments import Environment
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts


load_dotenv()
class APIClient:
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f"Unsupported environment value: {environment_str}")

        self.base_url = self.get_base_url(environment)
        self.session = requests.session()


    def get_base_url(self, environment: Environment) -> str:
        if environment.value == Environment.TEST.value:
            return os.getenv('TEST_BASE_URL')
        elif environment.value == Environment.PROD.value:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    def ping(self):
        with allure.step('Ping api client'):
            url = f"{self.base_url}{Endpoints.PING_ENDPOINT.value}"
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 201, f'Expected status 201 but got {response.status_code}'
        return response.status_code

    def auth(self):
        with allure.step('Getting authenticate'):
            url = f"{self.base_url}{Endpoints.AUTH_ENDPOINT.value}"
            payload = {"username": Users.USERNAME.value, "password": Users.PASSWORD.value}
            response = self.session.post(url, json=payload, timeout=Timeouts.TIMEOUT.value)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        token = response.json().get("token")
        with allure.step('Updating header with authorization'):
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_booking_by_id(self, booking_id: int):

        with allure.step(f'Get booking by id {booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.get(url, timeout=Timeouts.TIMEOUT.value)
            response.raise_for_status()
        with allure.step('Check status code is 200'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def delete_booking(self, booking_id):
        with allure.step('Delete booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.delete(url, auth=HTTPBasicAuth(Users.USERNAME.value, Users.PASSWORD.value))
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 201, f"Expected status code 201 but got {response.status_code}"
        return response.status_code == 201

    def create_booking(self, booking_data, expected_status_code=None):
        with allure.step('Creating booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=booking_data, headers=headers)

            if expected_status_code is not None:
                with allure.step(f'Checking status code (expected {expected_status_code})'):
                    assert response.status_code == expected_status_code, (
                        f"Expected status code {expected_status_code}, but got {response.status_code}. "
                        f"Response: {response.text}"
                    )
            else:
                response.raise_for_status()
            try:
                    return response.json()
            except ValueError:
                    return response.text

    def get_booking_ids(self, params=None):
        with allure.step('Getting object with booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status code 201 but got {response.status_code}"
        return response.status_code == 200

    def update_booking(self, booking_id, booking_data):
        with allure.step('Update booking with id'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.put(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status code 201 but got {response.status_code}"
        return response.json()

    def partial_update_booking(self, booking_id, booking_data):
        with allure.step('Update booking Partial'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.patch(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status code 201 but got {response.status_code}"
        return response.json()