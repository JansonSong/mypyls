from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter
from pyls_jsonrpc.endpoint import Endpoint
from pyls_jsonrpc.dispatchers import MethodDispatcher
from workspace import WorkSpace, PublishDiagnosticParams
import mypy_server
import logging
from urllib import parse
import lsp
import sys
import uris

log = logging.getLogger(__name__)

class PythonLanguageServer(MethodDispatcher):

    def __init__(self, reader, writer):
        self._jsonrpcstreamReader = JsonRpcStreamReader(reader)
        self._jsonrpcstreamWriter = JsonRpcStreamWriter(writer)
        self._endpoint = Endpoint(self, self._jsonrpcstreamWriter.write)
        self.isrunning = True
        self.workspace = None
        self.config = None

    def run(self):
       self._jsonrpcstreamReader.listen(self._endpoint.consume)

    def m_shutdown(self):
        self.isrunning = False

    def m_exit(self):
        self._jsonrpcstreamReader.close()
        self._jsonrpcstreamWriter.close()
        self._endpoint.shutdown()
        self.workspace = None
    
    def __getitem__(self, item):
        log.info(item)
        return super(PythonLanguageServer, self).__getitem__(item)

    def capablilities(self):
        import mypy_server
        is_patched_mypy = mypy_server.is_patched_mypy()
        if not is_patched_mypy:
            log.info('Using non-patched mypy, rich language features not available.')
        python_38 = sys.version_info >= (3, 8)
        if not python_38:
            log.info('Using Python before 3.8, rich language features not available.')
        rich_analysis_available = is_patched_mypy and python_38

        # 这三个功能不知道是干嘛用的
        server_capabilities = {
            "textDocumentSync": lsp.TextDocumentSyncKind.FULL,  # full document text
            'definitionProvider': rich_analysis_available,
            'hoverProvider': rich_analysis_available
        }
        return server_capabilities

    def m_initialize(self, processId=None, rootUri=None, rootPath=None, initializationOptions=None, **_kwargs):
        log.info('Language server initialized with %s %s %s %s', processId, rootUri, rootPath, initializationOptions)

        self.workspace = WorkSpace(rootUri, self._endpoint)
        try:
            import mypy
        except ImportError:
            log.error('Do not install mypy module!')
            self.workspace.show_message('Mypy is not installed.', lsp.MessageType.Warning)
            return {'capablilities': None}
        self.mypyserver = mypy_server.Server(mypy_server.options, mypy_server.DEFAULT_STATUS_FILE)
        return {"capabilities": self.capablilities()}

    def m_initialized(self, **_kwargs):
        pass

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.put_document(textDocument['uri'], textDocument['text'], version=textDocument.get('version'))

    def m_text_document__did_change(self, contentChanges=None, textDocument=None, **_kwargs):
        log.info(contentChanges)
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )
        log.info(self.workspace._docs.items())
        to_check = []
        for uri, doc in self.workspace._docs.items():
            fspath = uris.to_fs_path(uri)
            to_check.append(fspath)
            if mypy_server.mypy_version > "0.720":
                result = self.mypyserver.cmd_check(to_check, False, 80)
            else:
                result = self.mypyserver.cmd_check(to_check)
            diags = mypy_server.parse_mypy_out(result['out'])
            diagsparams = PublishDiagnosticParams(uri, diags).getDict()
            log.info(diagsparams)
            self.workspace.publish_diagnostics(diagsparams['uri'], diagsparams['diagnostics'])



    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        import mypy_server
        mypy_server.mypy_check(self.workspace, self.config)







    

    
    