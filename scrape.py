#!/usr/bin/python

"""
Python Script Template

A simple python 2.7 script template with argument parsing.

Author: Derek Jobst
Email: contact@derekjobst.com


References:
'Python 2.7 Docs: argparse'
https://docs.python.org/2/library/argparse.html
"""

import argparse
import requests
import dateparser as dp
from datetime import timedelta
import pytz

from bs4 import BeautifulSoup
from ics import Calendar, Event

def setup():
    ''' Setup argument parser and CLI '''

    parser = argparse.ArgumentParser(
        description='Scrape Penn FebClub Website'
    )

    return parser.parse_args()


def main(args):
    pp = pprint.PrettyPrinter(indent=4)
    res = requests.get('http://www.febclub2017.com/events')
    print "Encoding: {}".format(res.encoding)
    soup = BeautifulSoup(res.text, 'html.parser')

    cal = Calendar()

    for link in soup.find_all("div", { "class" : "detail" }):
        # Parse and format data
        paragraphs = [p.text for p in link.find_all('p')]
        date = paragraphs[2].split('\n')

        start_date = dp.parse("{} {}".format(date[0], date[1].split('-')[0].strip()))
        end_date = dp.parse("{} {}".format(date[0], date[1].split('-')[1].strip()))

        if end_date < start_date:
            end_date = end_date + timedelta(days=1)

        start_date = pytz.timezone('US/Eastern').localize(start_date)
        end_date = pytz.timezone('US/Eastern').localize(end_date)

        description = paragraphs[1].encode('ascii', errors='backslashreplace')

        event = Event()
        event.name = link.h1.text
        event.begin = start_date.isoformat()
        event.end = end_date.isoformat()
        event.description = u"{}\n{}\n\n{}".format(paragraphs[0], paragraphs[4], description)
        event.location = paragraphs[3]

        cal.events.append(event)
        print "Added event {}".format(link.h1.text)

    with open('febclub.ics', 'w') as f:
        f.writelines(cal)

if __name__ == '__main__':
    main(setup())
