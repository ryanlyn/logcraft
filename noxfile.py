import nox


PYTHON_VERSIONS = ["3.6", "3.7", "3.8"]


def install_package(session):
    session.install("--upgrade", "pip", "setuptools")
    session.install("-r", "requirements-dev.txt")
    return None


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    install_package(session)

    session.run(
        "pytest",
        "--cov=logcraft/",
        "--verbose"
    )
    return None


@nox.session(python="3.8")
def lint(session):
    install_package(session)

    session.run(
        "flake8",
        "--ignore=E501,E702",
        "--max-line-length=119",
        "--count",
        "statistics",
        "--show-source",
        "logcraft/"
    )
    return None


@nox.session(python="3.8")
def type_lint(session):
    install_package(session)

    session.run(
        "mypy",
        "logcraft/",
        "--disallow-untyped-calls",
        "--disallow-untyped-defs",
        "--disallow-incomplete-defs",
        "--warn-no-return",
        "--warn-return-any",
        "--warn-unreachable",
        "--show-error-context",
        "--ignore-missing-imports",
        "--pretty"
    )
    return None