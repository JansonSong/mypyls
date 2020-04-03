import os
import io
import uris
import logging
import lsp
from text import PublishDiagnosticParams


log = logging.getLogger(__name__)



class Document(object):

    def __init__(self, uri, source=None, version=None):
        self.uri = uri
        self.version = version
        self.filename = os.path.basename(self.uri)
        self.path = uris.to_fs_path(uri)
        log.info("self.path: %s", self.path)
        self._source = source

    @property
    def lines(self):
        return self.source.splitlines(True)

    @property
    def source(self):
        if self._source is None:
            with io.open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._source

    def apply_change(self, change):
        text = change['text']
        change_range = change.get('range')

        if not change_range:
            self._source = text
            return

        start_line = change_range['start']['line']
        start_col = change_range['start']['character']
        end_line = change_range['end']['line']
        end_col = change_range['end']['character']

        if start_line == len(self.lines):
            self._source = self._source + text
            return

        new = io.StringIO()

        for i, line in enumerate(self.lines):
            if i < start_line:
                new.write(line)
                continue
            if i > end_line:
                new.write(line)
                continue

            if i == start_line:
                new.write(line[:start_col])
                new.write(text)

            if i == end_line:
                new.write(line[end_col:])

        self._source = new.getvalue()

class WorkSpace(object):

    def __init__(self, rootUri, endpoint):
        self.rootUri = rootUri
        self.root_path = uris.to_fs_path(self.rootUri)
        self._endpoint = endpoint
        self._docs = {}

    def publish_diagnostics(self, doc_uri, diagnostics):
        self._endpoint.notify(lsp.Capability.M_PUBLISH_DIAGNOSTICS, params={'uri': doc_uri, 'diagnostics': diagnostics})

    def show_message(self, message, msg_type=lsp.MessageType.Info):
        self._endpoint.notify(lsp.Capability.M_SHOW_MESSAGE, params={'type': msg_type, 'message': message})

    def put_document(self, doc_uri, source, version=None):
        self._docs[doc_uri] = self._create_document(doc_uri, source=source, version=version)

    def update_document(self, doc_uri, change, version=None):
        self._docs[doc_uri].apply_change(change)
        self._docs[doc_uri].version = version
    
    def _create_document(self, doc_uri, source=None, version=None):
        return Document(doc_uri, source=source, version=version)