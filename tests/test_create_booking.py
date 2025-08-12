from http.client import responses

import allure
import pytest
import requests

from core.models.booking import BookingDates
from pydantic import ValidationError

from core.models.booking import BookingResponse


@allure.feature('Create booking')
@allure.story('Positive: creating booking with custom data')
def test_creating_booking_booking_with_custom_data(api_client):
    booking_data = {
        "firstname": "Ivan",
        "lastname": "Ivanov",
        "totalprice": 113,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-12-01",
            "checkout": "2025-02-01"
        },
        "additionalneeds": "Dinner"
    }
    response = api_client.create_booking(booking_data)
    try:
        BookingResponse(**response)
    except ValidationError as e:
        raise ValidationError(f'Response validation Error: {e}')

    assert response['booking']['firstname'] == booking_data['firstname']
    assert response['booking']['lastname'] == booking_data['lastname']
    assert response['booking']['totalprice'] == booking_data['totalprice']
    assert response['booking']['depositpaid'] == booking_data['depositpaid']
    assert response['booking']['bookingdates']['checkin'] == booking_data['bookingdates']['checkin']
    assert response['booking']['bookingdates']['checkout'] == booking_data['bookingdates']['checkout']
    assert response['booking']['additionalneeds'] == booking_data['additionalneeds']


@allure.feature('Create booking')
@allure.story('Negative: creating booking without firstname fails')
def test_create_booking_without_firstname_returns_500(api_client):
    booking_data = {
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-01-01",
            "checkout": "2024-01-05"
        },
        "additionalneeds": "Breakfast"
    }

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        api_client.create_booking(booking_data)

    assert exc_info.value.response.status_code == 500


@allure.feature("Create booking")
@allure.story("Negative: creating booking without booking_data")
def test_create_booking_without_booking_data(api_client):
    booking_data = {}
    with pytest.raises(requests.exceptions.HTTPError) as e:
        api_client.create_booking(booking_data)

    assert e.value.response.status_code == 500


@allure.feature('Create booking')
@allure.story('Negative: invalid data types')
def test_create_booking_with_invalid_data_types_returns_500(api_client):
    invalid_cases = [
        {"firstname": None},
        {"firstname": 12345},
        {"bookingdates": "2025-01-01,2025-01-05"}
    ]

    for case in invalid_cases:
        booking_data = {
            "firstname": "Valid",
            "lastname": "Data",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-01",
                "checkout": "2025-01-05"
            }
        }
        booking_data.update(case)

        with pytest.raises(requests.exceptions.HTTPError) as e:
            api_client.create_booking(booking_data)

        assert e.value.response.status_code == 500