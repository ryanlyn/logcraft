import tokenize
import inspect
from io import StringIO
from enum import Enum
from typing import Optional, Callable


class CallType(Enum):
    CALLABLE = 1
    CRITICAL = 2
    DEBUG = 3
    ERROR = 4
    FATAL = 5
    INFO = 6
    WARNING = 7
    NONE = 8


CALL_SIGNATURES = {
    "#:": CallType.CALLABLE,
    "#c:": CallType.CRITICAL,
    "#d:": CallType.DEBUG,
    "#e:": CallType.ERROR,
    "#f:": CallType.FATAL,
    "#i:": CallType.INFO
}


class DecoratorOrderException(Exception):
    pass


def log(obj: Optional[object] = None,
        *,
        logger: Optional[object] = None,
        custom_callable: Optional[Callable] = None,
        debug: bool = False) -> object:

    factory = LogFactory(
        logger=logger, custom_callable=custom_callable, debug=debug)
    if obj is None:
        return factory
    else:
        return factory(obj)


class LogFactory:
    def __init__(self,
                 logger: Optional[object] = None,
                 custom_callable: Optional[Callable] = None,
                 debug: bool = False):
        self.logger_name = logger.__name__ if logger else "logging"
        self.callable_name = custom_callable.__name__ if custom_callable else "print"
        self.debug = debug

    def __call__(self, obj: object) -> object:
        obj_src = inspect.getsource(obj)
        if self.debug:
            print("Original source:")
            print(obj_src)

        first_decorator, obj_src = obj_src.split("\n", 1)
        first_decorator = first_decorator.strip()[:5]
        if first_decorator != "@log(":
            if not ((len(first_decorator) == 4) and (first_decorator == "@log")):
                raise DecoratorOrderException()

        updated_src = update_object_src(
            obj_src=obj_src,
            logger_name=self.logger_name,
            callable_name=self.callable_name
        )

        if self.debug:
            print("Updated source:")
            print(updated_src)

        updated_obj = exec_object(object_src=updated_src)
        return updated_obj


def get_call_type(token_value: str) -> CallType:
    token_value = token_value.lstrip()

    max_signature_length = len(max(CALL_SIGNATURES.keys()))
    token_start = token_value[0:max_signature_length].rstrip()

    try:
        return CALL_SIGNATURES[token_start]
    except KeyError:
        return CallType.NONE


def update_object_src(obj_src: str,
                      logger_name: str = "logging",
                      callable_name: str = "print") -> str:
    new_tokens = []
    comment_stack = []

    previous_begin = None
    previous_call_type = CallType.NONE
    for token_spec in tokenize.generate_tokens(StringIO(obj_src).readline):
        token_type, token_string, begin, end, line = token_spec

        call_type = get_call_type(token_value=token_string)
        is_continuation = call_type == previous_call_type
        is_call = call_type != CallType.NONE
        is_newline = token_type == tokenize.NL

        if (not is_continuation) and (previous_call_type != CallType.NONE):
            if is_newline:
                continue

            call_tokens = create_call_tokens(
                comments=comment_stack,
                method=previous_call_type,
                logger_name=logger_name,
                callable_name=callable_name,
                begin=previous_begin
            )

            new_tokens += call_tokens

            if not is_call:
                new_tokens.append((token_type, token_string, begin, end, line))
                comment_stack = []
            else:
                comment_stack = [token_string]
        elif is_call:
            comment_stack.append(token_string)
        else:
            new_tokens.append((token_type, token_string, begin, end, line))

        previous_begin = begin
        previous_call_type = call_type

    new_tokens = remove_indent(tokens=new_tokens)
    updated_src = tokenize.untokenize(new_tokens)
    return updated_src


def clean_comment(comment: str) -> str:
    for signature in CALL_SIGNATURES.keys():
        comment = comment.replace(signature, "").strip()
    return comment


def create_call_tokens(comments: list,
                       method: CallType,
                       begin: tuple,
                       logger_name: str = "logging",
                       callable_name: str = "print") -> list:
    if method == CallType.NONE:
        return []

    comments = " ".join(map(lambda s: clean_comment(s), comments))

    if ("{" in comments) and ("}" in comments):
        call_var = f"""{'f"' + comments + '"'}"""
    else:
        call_var = '"' + comments + '"'

    call_strings = {
        CallType.CALLABLE: f"{callable_name}({call_var})",
        CallType.CRITICAL: f"{logger_name}.critical({call_var})",
        CallType.DEBUG: f"{logger_name}.debug({call_var})",
        CallType.ERROR: f"{logger_name}.error({call_var})",
        CallType.FATAL: f"{logger_name}.fatal({call_var})",
        CallType.INFO: f"{logger_name}.info({call_var})",
        CallType.WARNING: f"{logger_name}.warn({call_var})"
    }

    call_string = call_strings[method] + "\n"

    tokens = list(tokenize.generate_tokens(
        StringIO(call_string).readline))[:-1]

    updated_tokens = []
    for token_type, token_string, _begin, _end, line in tokens:
        updated_token = (
            token_type,
            token_string,
            (begin[0], begin[1] + _begin[1]),
            (begin[0], begin[1] + _end[1]),
            line
        )
        updated_tokens.append(updated_token)

    return updated_tokens


def remove_indent(tokens: list) -> list:
    first_token_type, *_, first_token_end, _ = tokens[0]
    if first_token_type == tokenize.INDENT:
        indent_position = first_token_end[1]

        new_tokens = []
        for token in tokens:
            token_type, token_value, begin, end, line = token

            is_dedent_at_begining = (token_type == tokenize.DEDENT) and (
                begin[1] == end[1] == 0)

            if token_type == tokenize.INDENT:
                token_value = token_value[indent_position:]
                end = (end[0], end[1] - indent_position)
            elif not ((token_type in (tokenize.NL, tokenize.ENDMARKER)) or is_dedent_at_begining):
                begin = (begin[0], begin[1] - indent_position)
                end = (end[0], end[1] - indent_position)

            new_token = (
                token_type,
                token_value,
                begin,
                end,
                line
            )
            new_tokens.append(new_token)
        return new_tokens
    else:
        return tokens


def exec_object(object_src: str) -> object:
    _namespace = {}
    exec(object_src, _namespace)
    (obj_name,) = (_namespace.keys() - set(["__builtins__"]))

    code = compile(object_src, "<string>", "exec")
    g = globals().copy()
    exec(code, g)
    return g[obj_name]
