from app import create_app

# TODO: Consider setting "entrypoint" in app.yaml instead of this file
app = create_app()

if __name__ == '__main__':
    app.run()
