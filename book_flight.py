#!/usr/bin/env python

import requests
from datetime import datetime, timedelta
from optparse import OptionParser, OptionGroup

FLIGHTS_REQUEST_HTTP = 'https://api.skypicker.com/flights?'
BOOKING_REQUEST_HTTP = 'http://37.139.6.125:8080/booking'

def build_request_query(fly_from,
                        fly_to,
                        date_from,
                        days_of_stay=None, # Don't use spaces around the = sign when used to indicate a keyword argument or a default parameter value.
                        sort='price',
                        ascending=True,
                        flights_url='https://api.skypicker.com/flights?'):
    """Returns a concatenated string based on input values as a request query."""

    datetime_from = datetime.strptime(date_from, '%Y-%m-%d')
    correct_format_date_from = '&dateFrom=' + datetime_from.strftime('%d/%m/%Y')
    # Calculate date of return from length of stay
    if days_of_stay is None:
        correct_format_date_to = ''
    else:
        datetime_to = datetime_from + timedelta(days = days_of_stay)
        correct_format_date_to = '&dateTo=' + datetime_to.strftime('%d/%m/%Y')
        
    request_tail = ''.join(['&booking_token=hashed%20data&offset=0&limit=5&sort=', sort,
                            '&asc=', int(ascending)])
    # Build final query as a string
    full_request_query = ''.join([flights_url,
                                  'flyFrom=' + fly_from,
                                  '&to=' +  fly_to,
                                  correct_format_date_from,
                                  correct_format_date_to,
                                  request_tail])
    
    return(full_request_query)

def get_booking_token(request_query):
    """Returns booking token from Kiwi flights API after successful response."""
    flights_request = requests.get(request_query)
    assert flights_request.status_code == 200, flights_request.reason
    flights_json = flights_request.json()
    assert flights_json['_results'] > 0, 'No results found for specified parameters.'
    booking_token = flights_json['data'][0]['booking_token']
    return(booking_token)

def book_flight(book_token, book_url = 'http://37.139.6.125:8080/booking'):
    """Returns pnr as a confirmation number of a successful booking."""
    book_request = requests.post(url = book_url, 
                                 json = {'currency': 'EUR', 
                                         'booking_token': book_token,
                                         'passengers': [{'birthday': '1987-12-31',
                                                         'documentID': 'dummyID321',
                                                         'email': 'dummy@email.com',
                                                         'firstName': 'Dummy',
                                                         'lastName': 'Don',
                                                         'title': 'Mr'}]})
    assert book_request.status_code == 200, book_request.reason
    return(book_request.json()['pnr'])
 
# parse command line arguments into build_request_query function values   
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--date', action = 'store', dest = 'date_from')
    parser.add_option('--from', action = 'store', dest = 'fly_from')
    parser.add_option('--to', action = 'store', dest = 'to')
    parser.add_option('--return', action = 'store', type = 'int', dest = 'return_in_days')
    # Add a group for sorting purposes in flights search response
    sort_group = OptionGroup(parser, "Sort results by category")
    sort_group.add_option('--cheapest', action = 'store_const', const = 'price', dest = 'sort')
    sort_group.add_option('--shortest', action = 'store_const', const = 'duration', dest = 'sort')
    sort_group.add_option('--best', action = 'store_const', const = 'quality', dest = 'sort')
    sort_group.add_option('--closest', action = 'store_const', const = 'date', dest = 'sort')
    parser.add_option_group(sort_group)
    # Add a group for descending order of flights search response
    order_group = OptionGroup(parser, 'Order by ascending')
    order_group.add_option('--expensive', action = 'store_false', dest = 'ascending')
    order_group.add_option('--longest', action = 'store_false', dest = 'ascending')
    order_group.add_option('--worst', action = 'store_false', dest = 'ascending')
    order_group.add_option('--furthest', action = 'store_false', dest = 'ascending')
    parser.add_option_group(order_group)
    # Specify default values for some parameters
    parser.set_defaults(return_in_days = None, sort = 'price', ascending = True)
    (options, args) = parser.parse_args()
    
    # Insert arguments as values into function call
    request_query = build_request_query(fly_from=options.fly_from,
                                        fly_to=options.to,
                                        date_from=options.date_from,
                                        days_of_stay=options.days_of_stay, 
                                        sort=options.sort,
                                        ascending=options.ascending,
                                        flights_url=FLIGHTS_REQUEST_HTTP)
    
    book_token = get_booking_token(request_query)
    
    pnr_confirmation = book_flight(book_token, book_url=BOOKING_REQUEST_HTTP)
    print(pnr_confirmation)