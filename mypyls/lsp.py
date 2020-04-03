
class Capability:
    M_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'
    M_APPLY_EDIT = 'workspace/applyEdit'
    M_SHOW_MESSAGE = 'window/showMessage'
    M_REPORT_PROGRESS = 'mypyls/reportProgress'
    M_CONFIGURATION = 'workspace/configuration'

class MessageType:
    Error = 1
    Warning = 2
    Info = 3
    Log = 4

class TextDocumentSyncKind(object):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2

class DiagnosticSeverity(object):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4