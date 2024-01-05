"""Module defining a set of useful tasks for CI/CD.
"""
import platform
from invoke import task

SRC_FOLDER = "src"


def get_activate_venv_cmd():
    """Get the venv activation command depending on the OS.
    """
    if platform.system() == "Windows":
        return ".\.env\Scripts\\activate"
    else:
        return "source .env/bin/activate"


@task
def install_package(c, extra="", proxy="", editable=False, build_isolation=False):
    """Install the Python package.

    Args:
        extra (str, optional): The extra packages to install.
            Defaults to not installing any. If you want to install CIP package,
            set it to cip.
        proxy (str, optional): The proxy to use for installation.
            Defaults to no proxy.
        editable (bool, optional): Whether or not the package should be 
            installed in development mode. Defaults to False.
        build_isolation (bool, optional): Whether or not the installation 
            should be isolated from the rest of the environment. Defaults to False.
    """
    install_extra = f"[{extra}]" if extra else ""
    install_through_proxies = f" --proxy {proxy}" if proxy else ""
    build_isolation_cmd = " --no-build-isolation" if not build_isolation else ""
    install_package_cmd = "pip install -e ." if editable else "pip install ."

    # Upgrade setuptools
    c.run("pip install --upgrade pip setuptools virtualenv wheel build" + install_through_proxies)
    # Install package
    c.run(install_package_cmd + install_extra + install_through_proxies + build_isolation_cmd)


@task
def install(c, extra="", proxy="", editable=False, build_isolation=False, venv=False):
    """Install the Python package, optionally in a venv.

    Args:
        extra (str, optional): The extra packages to install.
            Defaults to not installing any. If you want to install CIP package,
            set it to cip.
        proxy (str, optional): The proxy to use for installation.
            Defaults to no proxy.
        editable (bool, optional): Whether or not the package should be 
            installed in development mode. Defaults to False.
        build_isolation (bool, optional): Whether or not the installation 
            should be isolated from the rest of the environment. Defaults to False.
        venv (bool, optional): Whether or not the install should be done in 
            a virtualenv, with a name .env. Defaults to False.
    """
    if venv:
        venv_cmd = "python -m venv .env"
        c.run(venv_cmd)
        activate_cmd = get_activate_venv_cmd()
        with c.prefix(activate_cmd):
            install_package(c, extra=extra, proxy=proxy, editable=editable,
                            build_isolation=build_isolation)
    else:
        install_package(c, extra=extra, proxy=proxy, editable=editable,
                        build_isolation=build_isolation)


@task
def test(c, coverage=True, venv=False, report=""):
    """Run the unit tests of the package. The package should have been 
    installed in cip mode.

    Args:
        coverage (bool, optional): Whether or not to output the coverage.
            Defaults to True.
        venv (bool, optional): Whether or not to run the tests in a venv. You 
            need to have installed the package in venv mode beforehand.
            Defaults to True.
        report (str, optional): The path to the coverage report, if coverage is set to True.
            Defaults to an empty path.
    """
    cov = f"--cov={SRC_FOLDER}" if coverage else ""
    report_cmd = f" --cov-report {report} " if report else ""
    test_cmd = f"pytest {cov}{report_cmd} --cov-report term-missing {SRC_FOLDER}/tests"
    if venv:
        activate_cmd = get_activate_venv_cmd()
        with c.prefix(activate_cmd):
            c.run(test_cmd)
    else:
        c.run(test_cmd)


@task
def lint(c, rc_file="", output_file="", venv=False):
    """Lint the package using pylint.
    The package should be installed in cip mode.

    Args:
        rc_file (str, optional): The configuration to use for linting.
            Defaults to the pylint standard configuration.
        output_file (str, optional): The path to the output of the pylint 
            command. Defaults to no file.
        venv (bool, optional): Whether or not the command should be run in 
            the venv. Defaults to True. The package needs to have been 
            installed in a venv beforehand.
    """
    rc_cmd = f" --rcfile={rc_file}" if rc_file else ""
    output_file_cmd = f" > {output_file}" if output_file else ""
    lint_cmd = "pylint --recursive=y --exit-zero --output-format=parseable --reports=no "\
        f"{SRC_FOLDER} {rc_cmd} {output_file_cmd}"
    if venv:
        activate_cmd = get_activate_venv_cmd()
        with c.prefix(activate_cmd):
            c.run(lint_cmd)
    else:
        c.run(lint_cmd)


@task
def build(c, proxy="", outdir=""):
    """Bundle the Python code into a wheel.

    Args:
        proxy (str, optional): The proxy to use for installation.
            Defaults to not using any proxy.
        outdir (str, optional): The path to the folder to store the wheel.
            Defaults to dist.
    """
    outdir_cmd = f" --outdir {outdir}" if outdir else ""
    install_through_proxies = f" --proxy {proxy}" if proxy else ""
    # Create Python venv and activate
    c.run("python -m venv .env")
    activate_cmd = get_activate_venv_cmd()
    with c.prefix(activate_cmd):
        c.run("pip install --upgrade build pip setuptools" + install_through_proxies)
        build_cmd = "python -m build --no-isolation" + outdir_cmd
        c.run(build_cmd)


@task
def build_docs(c, output_dir="docs"):
    """Build the documentation using mkdocs.

    Args:
        output_dir (str, optional): The directory to store the documentation.
            Defaults to "docs".
    """
    c.run(f"python -m mkdocs build -d {output_dir}")
