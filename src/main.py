from flask import Flask

from contacts.controllers.contact_controller import contact_bp
from contacts.models.contact_model import ContactModel

from database.database import db

API_PREFIX = "/api/v1"

app = Flask(__name__)

app.register_blueprint(contact_bp, url_prefix=f"{API_PREFIX}/contacts")

with app.app_context():
    db.create_tables()


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
