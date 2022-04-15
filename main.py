from flask import Flask, render_template, url_for
from dotenv import load_dotenv

load_dotenv()
app = Flask("Elysium")


def main():
    app.run(debug=False)


if __name__ == "__main__":
    main()

