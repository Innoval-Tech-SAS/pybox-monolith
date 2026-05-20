from flask import Flask, jsonify

from config.error_handlers import register_error_handlers
from auth.controllers.auth_controller import auth_bp
from contacts.controllers.contact_controller import contact_bp
from users.models.user_model import UserModel
from organizations.models.organization_model import OrganizationModel
from organizations.models.organization_membership_model import (
    OrganizationMembershipModel,
)
from contacts.models.contact_model import ContactModel


from database.database import db

API_PREFIX = "/api/v1"

app = Flask(__name__)

register_error_handlers(app)

app.register_blueprint(auth_bp, url_prefix=f"{API_PREFIX}/auth")
app.register_blueprint(contact_bp, url_prefix=f"{API_PREFIX}/contacts")


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the Contacts API!"})


with app.app_context():
    db.create_tables()


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
