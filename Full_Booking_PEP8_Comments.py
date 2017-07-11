#!/usr/bin/env python

# Imports should be grouped in the following order:

# standard library imports
# related third party imports
# local application/library specific imports
# You should put a blank line between each group of imports.

import requests
from datetime import datetime, timedelta
from optparse import OptionParser, OptionGroup

# Constants are usually defined on a module level and written in all capital letters with underscores separating words. 
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
    # For triple-quoted strings, always use double quote characters to be consistent with the docstring convention in PEP 257 .

    datetime_from = datetime.strptime(date_from, '%Y-%m-%d')
    correct_format_date_from = '&dateFrom=' + datetime_from.strftime('%d/%m/%Y')
    
    # Comments should be complete sentences. If a comment is a phrase or sentence, 
    # its first word should be capitalized, 
    # unless it is an identifier that begins with a lower case letter (never alter the case of identifiers!).

    # If a comment is short, the period at the end can be omitted. 
    # Block comments generally consist of one or more paragraphs built out of complete sentences, 
    # and each sentence should end in a period.
    
    # Calculate date of return from length of stay
    # Don't compare boolean values to True or False using == .
    if days_of_stay is None:
        correct_format_date_to = ''
    else:
        datetime_to = datetime_from + timedelta(days = days_of_stay)
        correct_format_date_to = '&dateTo=' + datetime_to.strftime('%d/%m/%Y')
        
    request_tail = ''.join(['&booking_token=hashed%20data&offset=0&limit=5&sort=', sort,
                            '&asc=', str(ascending)])
    
    # Build final query as a string
    full_request_query = ''.join([flights_url,
                                  'flyFrom=' + fly_from,
                                  '&to=' +  fly_to,
                                  correct_format_date_from,
                                  correct_format_date_to,
                                  request_tail])
    
    return(full_request_query)

# Function names should be lowercase, with words separated by underscores as necessary to improve readability.
def get_booking_token(request_query):
    """Returns booking token from Kiwi flights API after successful response."""
    flights_request = requests.get(request_query)
    # Don't compare boolean values to True or False using == .
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
    parser.add_option('--one-way', action = 'store_const', const = None, dest = 'return_in_days')

    # Add group for one-way or return ticket
    #return_group = OptionGroup(parser, "One way or return ticket")
    #return_group.add_option('--return', action = 'store', type = 'int', dest = 'return_in_days')
    #return_group.add_option('--one-way', action = 'store_const', const = None, dest = 'return_in_days')
    #parser.add_option_group(return_group)
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
                                        days_of_stay=options.return_in_days, 
                                        sort=options.sort,
                                        ascending=options.ascending,
                                        flights_url=FLIGHTS_REQUEST_HTTP)
    
    book_token = get_booking_token(request_query)
    
    pnr_confirmation = book_flight(book_token, book_url=BOOKING_REQUEST_HTTP)
    print(pnr_confirmation)