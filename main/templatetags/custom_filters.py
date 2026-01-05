# custom_filters.py
from django import template
from datetime import datetime, date, timedelta

register = template.Library()

@register.filter(name='nepali_date_format')
def nepali_date_format(value):
    # Check if value is already a date object
    if isinstance(value, date):
        # If it's a date object, use it directly
        date_object = value
    else:
        # If it's a string, convert it to a datetime object
        # date_object = datetime.strptime(value, '%b. %d, %Y'),
        # If it's a string, convert it to a datetime object
        date_object = datetime.strptime(value, '%Y-%m-%d').date()

    # Extract year, month, and day
    year = date_object.year
    month = date_object.month
    day = date_object.day

    # Format the Nepali date as 'YYYY/MM/DD'
    return f"{year:04d}/{month:02d}/{day:02d}"


@register.filter(name='parse_date')
def parse_date(value):
    if isinstance(value, str):
        return datetime.date.fromisoformat(value)
    elif isinstance(value, date):
        return value
    else:
        # Handle the case where value is neither a string nor a date
        print(f"Invalid date format: {value}")
        return None    

# @register.filter(name='bs_to_ad')
# def bs_to_ad(value):
#     # Assuming value is a tuple (bs_year, bs_month, bs_day)
#     bs_year, bs_month, bs_day = value

#     # Define the start date of the Nepali calendar
#     nepali_start_year = 1951
#     gregorian_start_date = datetime(1944, 4, 13)  # Corresponding AD date

#     # Calculate the difference in years between Nepali and Gregorian calendars
#     year_difference = bs_year - nepali_start_year

#     # Calculate the number of days to add to the start date
#     total_days = (
#         year_difference * 365 +
#         (bs_month - 1) * 30 +  # Assume 30 days per month
#         bs_day
#     )

#     # Calculate the corresponding AD date
#     ad_date = gregorian_start_date + timedelta(days=total_days)

#     return ad_date.year, ad_date.month, ad_date.day


import calendar



@register.filter(name='ad_to_bs')
def ad_to_bs(ad_year, ad_month, ad_day):
    try:
        # Define the starting AD date and the corresponding BS date
        ad_start_date = datetime(1943, 4, 18)
        bs_start_date = datetime(2000, 1, 1)

        # Calculate the difference in days between the provided AD date and the starting AD date
        ad_date = datetime(ad_year, ad_month, ad_day)
        ad_days = (ad_date - ad_start_date).days

        # Check if the provided AD date is within the range of the Nepali calendar
        if ad_days < 0:
            raise ValueError("Provided AD date is outside the range of the Nepali calendar")

        # Calculate the corresponding BS date by adding the days difference to the starting BS date
        bs_date = bs_start_date
        bs_year = bs_date.year
        bs_month = bs_date.month
        bs_day = bs_date.day

        while ad_days > 0:
            days_in_month = calendar.monthrange(bs_year, bs_month)[1]  # Get the number of days in the Nepali month

            remaining_days = days_in_month - bs_day + 1

            if ad_days >= remaining_days:
                ad_days -= remaining_days
                bs_month += 1
                if bs_month > 12:
                    bs_month = 1
                    bs_year += 1
            else:
                bs_day += ad_days
                ad_days = 0

        bs_date_obj = date(bs_year, bs_month, bs_day)
        print(f"Converted AD to BS: {ad_year}/{ad_month:02d}/{ad_day:02d} -> {bs_date_obj}")
        return bs_date_obj
    except Exception as e:
        print(f"Error in ad_to_bs: {e}")
        return None

# custom_filters.py

from django import template
import json

register = template.Library()

@register.filter
def jsonify(obj):
    return json.dumps(obj)
