from urllib import parse
import re


RE_DRIVE_LETTER_PATH = re.compile(r'^\/[a-zA-Z]:')

def urlparse(uri):
    """Parse and decode the parts of a URI."""
    scheme, netloc, path, params, query, fragment = parse.urlparse(uri)
    return (
        parse.unquote(scheme),
        parse.unquote(netloc),
        parse.unquote(path),
        parse.unquote(params),
        parse.unquote(query),
        parse.unquote(fragment)
    )

def to_fs_path(uri):
    scheme, netloc, path, _params, _query, _fragment = urlparse(uri)

    if netloc and path and scheme == 'file':
        value = "//{}{}".format(netloc, path)

    elif RE_DRIVE_LETTER_PATH.match(path):
        value = path[1].lower() + path[2:]
    
    else:
        value = path

    return value