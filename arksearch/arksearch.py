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
from bs4 import BeautifulSoup
import bs4


import click


import requests


from terminaltables import AsciiTable

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
              "Gecko) Chrome/47.0.2526.111 Safari/537.36")


def get_full_ark_url(prodUrl):
    full_url = "http://ark.intel.com{0}".format(prodUrl)
    return full_url


def get_cpu_html(prodUrl):
    """Connect to Intel's ark website and retrieve HTML."""
    full_url = get_full_ark_url(prodUrl)
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(full_url, headers=headers)
    return r.text


def generate_table_data(html_output):
    """Generate an ASCII table based on the HTML provided."""
    soup = BeautifulSoup(html_output, 'html.parser')

    table_data = [
    ]

    all_data = soup.select("#bladeInside > ul > li")
    for i in all_data:
        cell = ["1", "2"]
        temp_list = []
        for tag in i.children:
            if type(tag) == bs4.element.Tag:
                temp_list.append(tag)

        cell[0] = temp_list[0].get_text().strip()
        cell[1] = temp_list[1].get_text().strip()
        table_data.append(cell)
    return table_data


def quick_search(search_term):
    url = "https://ark.intel.com/libs/apps/intel/arksearch/autocomplete?" + \
        "_charset_=UTF-8" + \
        "&locale=en_us" + \
        "&currentPageUrl=https%3A%2F%2Fark.intel.com%2Fcontent%2Fwww%2Fus%2Fen%2Fark.html" + \
        "&input_query={0}"
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

    click.echo(u"Processors found: {0}".format(len(ark_json)))
    choice_dict = {}
    counter = 0
    for cpu in ark_json:
        choice_dict[counter] = cpu['prodUrl']
        click.echo(u"[{0}] {1}".format(counter, cpu['label']))
        counter += 1

    if len(ark_json) > 1:
        choice = click.prompt(u"Which processor", prompt_suffix='? ', type=int)
    else:
        choice = 0

    cpu_data = get_cpu_html(choice_dict[int(choice)])
    table_data = generate_table_data(cpu_data)
    table = AsciiTable(table_data)
    click.echo(table.table)
    ctx.exit(0)


if __name__ == '__main__':
    search()
