from typing import Optional, List

def _convert_val(target):
    if target is None:
        return None
    if isinstance(target, (int, float, str)):
        return target
    elif isinstance(target, list):
        result = []
        for item in target:
            result.append(_convert_val(item))
        return result
    elif isinstance(target, dict):
        result = {}
        for key, value in target.items():
            result[key] = _convert_val(value)
    elif isinstance(target, LspItem):
        return target.getDict()
    else:
        return None

class LspItem(object):
    def __init__(self, **_kwargs):
        pass

    @classmethod
    def fromDict(cls, param: dict):
        return cls(**param)

    def getDict(self):
        dump_dict = {}
        for key, value in vars(self).items():
            if value is not None:
                converted = _convert_val(value)
                if converted is not None:
                    dump_dict[key] = converted
        return dump_dict
        
class Position(LspItem):
    def __init__(self, line: int, character: int, **_kwargs):
        self.line: int = line
        self.character: int = character


class Range(LspItem):
    def __init__(self, start: Position, end: Position, **kwargs):
        self.start = start
        self.end = end

    @classmethod
    def fromDict(cls, param: dict):
        return cls(start=Position.fromDict(param['start']),
                end=Position.fromDict(param['end']))

class Diagnostic(LspItem):
    def __init__(self, range: Range, message: str, severity: Optional[int] = None, **kwargs):
        self.range = range
        self.message = message
        self.severity = severity

    @classmethod
    def fromDict(cls, param: dict):
        return Diagnostic(Range.fromDict(param['range']), param['message'], param['severity'])


class PublishDiagnosticParams(LspItem):
    def __init__(self, uri: str, diagnostics: List[Diagnostic],
                 **kwargs):
        self.uri = uri
        self.diagnostics = diagnostics

    @classmethod
    def fromDict(cls, param: dict):
        diags = []
        for diag_dict in param['diagnostics']:
            diags.append(Diagnostic.fromDict(diag_dict))
        return cls(uri=param['uri'], diagnostics=diags)
