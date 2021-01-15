import json
import os


from arksearch import arksearch


from click.testing import CliRunner


from httmock import HTTMock, response, urlmatch


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
        '<span>Processor Graphics <small><sup>\xe2</sup></small>'
        '</span>'
        '</td>'
        '<td class="rc">None</td>'
        '</tr>')

    def test_get_full_ark_url(self):
        prodUrl = (
            "\/content\/www\/us\/en\/ark\/products\/82930\/intel-core-i7-5960x-processor-extreme-edition-20m-cache-up-to-3-50-ghz.html")
        result = arksearch.get_full_ark_url(prodUrl)
        expected_url = ("http://ark.intel.com/"
                        "content/www/us/en/ark/products/"
                        "82930/intel-core-i7-5960x-processor-extreme-edition-20m-cache-up-to-3-50-ghz.html")
        assert result == expected_url

    def test_get_cpu_html(self,):

        @urlmatch(netloc=r'ark.intel.com')
        def ark_mock(url, request):
            return response(200, self.test_table.encode('utf-8'))

        with HTTMock(ark_mock):
            prodUrl = (
                "\/content\/www\/us\/en\/ark\/products\/82930\/intel-core-i7-5960x-processor-extreme-edition-20m-cache-up-to-3-50-ghz.html")
            result = arksearch.get_cpu_html(prodUrl)
        assert result == self.test_table

    def test_quick_search_multiple_results(self):
        mocked_json_file = ("{0}/tests/json_data/"
                            "multiple_results.json".format(os.getcwd()))
        with open(mocked_json_file, 'r') as handle:
            mocked_json = handle.read()

        @urlmatch(netloc=r'ark.intel.com')
        def ark_mock(url, request):
            return response(200, json.loads(mocked_json))

        search_term = "E3-1270"

        with HTTMock(ark_mock):
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
        mocked_json_file = ("{0}/tests/json_data/"
                            "multiple_results.json".format(os.getcwd()))
        with open(mocked_json_file, 'r') as handle:
            mocked_json = handle.read()

        def mockreturn_search_json(search_term):
            return json.loads(mocked_json)

        def mockreturn_cpu_data(search_term):
            return self.test_table

        runner = CliRunner()
        monkeypatch.setattr(arksearch, "quick_search", mockreturn_search_json)
        monkeypatch.setattr(arksearch, "get_cpu_html", mockreturn_cpu_data)
        result = runner.invoke(arksearch.search, ['E3-1270'], input="0\n")
        assert "Processors found: 4" in result.output
        assert "Processor E3-1270 v5" in result.output
        assert "Status" in result.output
        assert "Launched" in result.output

    def test_search_with_single_results(self, monkeypatch):
        mocked_json_file = ("{0}/tests/json_data/"
                            "single_result.json".format(os.getcwd()))
        with open(mocked_json_file, 'r') as handle:
            mocked_json = handle.read()

        def mockreturn_search_json(search_term):
            return json.loads(mocked_json)

        def mockreturn_cpu_data(search_term):
            return self.test_table

        runner = CliRunner()
        monkeypatch.setattr(arksearch, "quick_search", mockreturn_search_json)
        monkeypatch.setattr(arksearch, "get_cpu_html", mockreturn_cpu_data)
        result = runner.invoke(arksearch.search, ['E3-1230L'])
        assert "Processors found: 1" in result.output
        assert "Processor E3-1230L v3" in result.output
        assert "Status" in result.output
        assert "Launched" in result.output

    def test_search_with_no_results(self, monkeypatch):
        def mockreturn(search_term):
            return json.loads("[]")
        monkeypatch.setattr(arksearch, "quick_search", mockreturn)
        runner = CliRunner()
        result = runner.invoke(arksearch.search, ['E3-1270xxx'])
        assert "Couldn't find any processors matching" in result.output
