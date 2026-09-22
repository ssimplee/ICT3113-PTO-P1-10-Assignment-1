"""Run precisely one synchronous request handler for the baseline experiment."""

from werkzeug.serving import run_simple

from . import create_app


def main():
    app = create_app()
    run_simple("0.0.0.0", app.config["PORT"], app,
               threaded=False, processes=1, use_reloader=False, use_debugger=False)


if __name__ == "__main__":
    main()
