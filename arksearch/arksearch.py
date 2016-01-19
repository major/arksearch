#!/usr/bin/env python
#
# Copyright 2016 Major Hayden
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Searches Intel's ARK site and returns data about various processors.

TOTALLY UNOFFICIAL. ;)
"""
import sys


from bs4 import BeautifulSoup


import click


import requests


from terminaltables import AsciiTable

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
              "Gecko) Chrome/47.0.2526.111 Safari/537.36")


def get_full_ark_url(quickurl):
    full_url = "http://ark.intel.com{0}".format(quickurl)
    return full_url


def get_cpu_html(quickurl):
    """Connect to Intel's ark website and retrieve HTML."""
    full_url = get_full_ark_url(quickurl)
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(full_url, headers=headers)
    return r.text


def generate_table_data(html_output):
    """Generate an ASCII table based on the HTML provided."""
    soup = BeautifulSoup(html_output, 'html.parser')

    table_data = [
        ['Parameter', 'Value']
    ]

    for table in soup.select('table.specs'):
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = [cell.get_text("\n", strip=True)
                     for cell in row.find_all('td')]

            if cells[0] == 'T\nCASE':
                cells[0] = 'T(CASE)'
            if "\n" in cells[0]:
                cells[0] = cells[0][:cells[0].index("\n")]

            table_data.append(cells)

    return table_data


def quick_search(search_term):
    url = "http://ark.intel.com/search/AutoComplete?term={0}"
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(url.format(search_term, headers=headers))
    return r.json()


@click.command()
@click.argument('search_term')
@click.pass_context
def search(ctx, search_term):
    """Main function of the script."""
    ark_json = quick_search(search_term)

    if len(ark_json) < 1:
        click.echo("Couldn't find any processors matching "
                   "{0}".format(search_term))
        ctx.exit(0)

    click.echo("Found {0} processors...".format(len(ark_json)))
    choice_dict = {}
    counter = 0
    for cpu in ark_json:
        choice_dict[counter] = cpu['quickUrl']
        sys.stdout.write(u"[{0}] {1}\n".format(counter, cpu['value']))
        counter += 1
    choice = input("Which processor? ")

    cpu_data = get_cpu_html(choice_dict[int(choice)])
    table_data = generate_table_data(cpu_data)
    table = AsciiTable(table_data)
    click.echo(table.table)

if __name__ == '__main__':
    search()
