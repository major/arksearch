from arksearch import arksearch
from click.testing import CliRunner

import json
import os
import pytest
import requests
import requests_mock


class TestArksearch(object):

    test_table = ('<table class="specs infoTable"><tr class="infoSection">'
                  '<tr id="StatusCodeText" data-disclaim="StatusCodeText">'
                  '<td class="lc">'
                  '<span>Status</span>'
                  '</td>'
                  '<td class="rc">Launched</td>'
                  '</tr>')

    test_table_tcase = (
                  '<table class="specs infoTable"><tr class="infoSection">'
                  '<tr id="TCase" class="tech">'
                  '<td class="lc">'
                  '<span class="tooltippable">T<sub>CASE</sub></span>'
                  '</td>'
                  '<td class="rc">66.8</td>'
                  '</tr>')

    test_table_newline = (
                  '<table class="specs infoTable"><tr class="infoSection">'
                  '<tr id="GraphicsModel" data-disclaim="GraphicsModel">'
                  '<td class="lc">'
                  '<span>Processor Graphics <small><sup>\xe2</sup></small></span>'
                  '</td>'
                  '<td class="rc">None</td>'
                  '</tr>')

    def test_get_full_ark_url(self):
        quickUrl = ("/products/82930/Intel-Core-i7-5960X-Processor-Extreme-"
                    "Edition-20M-Cache-up-to-3_50-GHz")
        result = arksearch.get_full_ark_url(quickUrl)
        expected_url = ("http://ark.intel.com//products/82930/Intel-Core-i7-"
                        "5960X-Processor-Extreme-Edition-20M-Cache-up-to-"
                        "3_50-GHz")
        assert result == expected_url

    @requests_mock.mock()
    def test_get_cpu_html(self, m):
        ark_baseurl = "http://ark.intel.com/"
        quickUrl = ("/products/82930/Intel-Core-i7-5960X-Processor-Extreme-"
                    "Edition-20M-Cache-up-to-3_50-GHz")
        m.get("{0}{1}".format(ark_baseurl, quickUrl), text=self.test_table)
        result = arksearch.get_cpu_html(quickUrl)
        assert result == self.test_table

    @requests_mock.mock()
    def test_quick_search_multiple_results(self, m):
        mocked_json_file = "{0}/tests/json_data/multiple_results.json".format(os.getcwd())
        with open(mocked_json_file, 'r') as handle:
            mocked_json = handle.read()

        search_term = "E3-1270"
        url = "http://ark.intel.com/search/AutoComplete?term={0}"
        m.get(url.format(search_term), text=mocked_json.decode('utf-8'))

        result = arksearch.quick_search(search_term)
        assert result == json.loads(mocked_json)

    def test_generate_table_data_normal(self):
        result = arksearch.generate_table_data(self.test_table)
        assert result == [['Parameter', 'Value'], ['Status', 'Launched']]

    def test_generate_table_data_tcase(self):
        result = arksearch.generate_table_data(self.test_table_tcase)
        assert result == [['Parameter', 'Value'], ['T(CASE)', '66.8']]

    def test_generate_table_data_newline(self):
        result = arksearch.generate_table_data(self.test_table_newline)
        assert result == [['Parameter', 'Value'],
                          ['Processor Graphics', 'None']]

    def test_search_with_multiple_results(self, monkeypatch):
        mocked_json_file = "{0}/tests/json_data/multiple_results.json".format(os.getcwd())
        with open(mocked_json_file, 'r') as handle:
            mocked_json = handle.read()
        def mockreturn(search_term):
            return json.loads(mocked_json)
        monkeypatch.setattr(arksearch, "quick_search", mockreturn)
        runner = CliRunner()
        result = runner.invoke(arksearch.search, ['E3-1270'], input="0\n")
        assert result.exit_code == 0
        assert "Found 4 processors" in result.output

    def test_search_with_no_results(self, monkeypatch):
        def mockreturn(search_term):
            return json.loads("[]")
        monkeypatch.setattr(arksearch, "quick_search", mockreturn)
        runner = CliRunner()
        result = runner.invoke(arksearch.search, ['E3-1270xxx'])
        assert result.exit_code == 0
        assert "Couldn't find any processors matching" in result.output
