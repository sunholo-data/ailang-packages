"""Public single-document check, intentionally insufficient for cross-document ownership."""
def passes(response):
    return response.get('schema') == 'maintenance.resource-ownership/1' and len(response.get('results', [])) == 2 and response['results'][0].get('ok') is True and response['results'][1] == {'ok': True, 'bytes': ['AP8A']}
