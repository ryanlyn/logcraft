import ast

import pytest

from logcraft.macro import (
    DecoratorFactory, 
    DecoratorOrderException, 
    log, 
    _update_object_src
)


def declare(src: str) -> str:
    return src.strip("\n ")


def parse(src: str) -> str:
    return ast.dump(ast.parse(src), annotate_fields=True)


def assert_parsed_ast(decorated: str, 
                      expected: str, 
                      expected_logger_name: str = "logging",
                      expected_callable_name: str = "print") -> None:
    updated: str = _update_object_src(
        obj_src=decorated,
        logger_name="logging",
        callable_name="print"
    )

    assert parse(updated) == parse(expected)
    return None


class TestDecoratorRaises:

    def test_raises_decorator_order_exception_basic(self):
        decorated = declare(
            """
            @some_other_decorator
            @log
            def f():
                return None
            """
        )

        with pytest.raises(DecoratorOrderException):
            _update_object_src(obj_src=decorated)

    def test_raises_decorator_order_exception_name_other_logging(self):
        decorated = declare(
            """
            @log_me
            @log
            def f():
                return None
            """
        )

        with pytest.raises(DecoratorOrderException):
            _update_object_src(obj_src=decorated)


class TestFunctionDeclaration:

    def test_basic(self):
        decorated = declare(
            """
            @log
            def f():
                #: print this
                return 1
            """
        )
        expected = declare(
            """
            def f():
                print("print this")
                return 1
            """
        )
        assert_parsed_ast(decorated, expected)
        

    def test_logging(self):
        decorated = declare(
            """
            @log
            def f():
                #c: test critical
                #d: test debug
                #e: test error
                #f: test fatal
                #i: test info
                #w: test warn
                return None
            """
        )

        expected = declare(
            """
            def f():
                logging.critical("test critical")
                logging.debug("test debug")
                logging.error("test error")
                logging.fatal("test fatal")
                logging.info("test info")
                logging.warn("test warn")
                return None
            """
        )
        assert_parsed_ast(decorated, expected)
