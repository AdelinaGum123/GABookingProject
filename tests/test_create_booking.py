from http.client import responses

import allure
import pytest

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
@allure.story('Negative: non existent month')
def test_non_existent_month(api_client, booking_dates):
    year = booking_dates["checkin"][:4]
    booking_data = {
        "checkin": f"{year}-13-01",  # не существующий месяц
        "checkout": f"{year}-02-01"
    }

    with pytest.raises(ValidationError) as e:
        BookingDates(**booking_data)
    assert "month value is outside expected range of 1-12" in str(e.value)


@allure.feature('Create booking')
@allure.story('Negative: invalid leap year date')
def test_invalid_leap_year_date(api_client):
    booking_data = {
        "checkin": "2025-02-29", # не существующий день в не високосном году 
        "checkout": "2025-03-01"
    }

    with pytest.raises(ValidationError) as e:
        BookingDates(**booking_data)
    assert "day value is outside expected range" in str(e.value)


@allure.feature('Create booking')
@allure.story('Negative: invalid day in april')
def test_invalid_day_in_april(api_client, booking_dates):
    year = booking_dates["checkin"][:4]
    booking_data = {
        "checkin": f"{year}-04-31",  # не существующий день в апреле
        "checkout": f"{year}-05-15"
    }

    with pytest.raises(ValidationError) as e:
        BookingDates(**booking_data)
    assert "day value is outside expected range" in str(e.value)
