from mypy.version import __version__
from mypy.options import Options
from mypy.dmypy_server import Server
from mypy.dmypy_util import DEFAULT_STATUS_FILE
from text import Position, Range, Diagnostic
import logging
import re
import lsp

line_pattern = r'([^:]+):(?:(\d+):)?(?:(\d+):)? (\w+): (.*)'

log = logging.getLogger(__name__)

settings = None
mypy_version = __version__


options = Options()
options.check_untyped_defs = True
options.follow_imports = 'error'
options.use_fine_grained_cache = True
options.show_column_numbers = True

def is_patched_mypy():
    return 'langserver' in mypy_version

def parse_mypy_out(output: str):
    lines = output.splitlines()
    diags = []
    for line in lines:
        result = re.match(line_pattern, line)
        if result is None:
            break
        path, lineno, offset, serverity, msg = result.groups()
        
        diag_range = Range(Position(int(lineno)-1, int(offset) - 1),
                           Position(int(lineno)-1, int(offset)))
        diag_sev = lsp.DiagnosticSeverity.Error if serverity == 'error' else lsp.DiagnosticSeverity.Information
        diag = Diagnostic(diag_range, msg, diag_sev)
        diags.append(diag)
    log.info(len(diags))
    return diags

def mypy_check(workspace, config):
    if not workspace.root_path:
        return

    if settings is None:
        return

    log.info('Checking mypy ...')