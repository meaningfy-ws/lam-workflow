INPUT_MIME_TYPES = {
    'rdf': 'application/rdf+xml',
    'trix': 'application/xml',
    'nq': 'application/n-quads',
    'nt': 'application/n-triples',
    'jsonld': 'application/ld+json',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
}
HTML_EXTENSION = 'html'
JSON_EXTENSION = 'json'
TTL_EXTENSION = 'ttl'
ZIP_EXTENSION = 'zip'
REPORT_EXTENSIONS = [TTL_EXTENSION, HTML_EXTENSION, JSON_EXTENSION, ZIP_EXTENSION]
DEFAULT_REPORT_EXTENSION = REPORT_EXTENSIONS[0]
EXTENSION_TO_FILETYPE = {
    HTML_EXTENSION: 'custom_html_report',
    JSON_EXTENSION: 'custom_json_report',
    TTL_EXTENSION: 'ttl_report',
    ZIP_EXTENSION: 'zip_report'
}