from aiohttp import web

from config import load_config
from interface.web_app import create_app


def main():
    config = load_config()
    app = create_app(config)
    web.run_app(app, port=config.port)


if __name__ == "__main__":
    main()
