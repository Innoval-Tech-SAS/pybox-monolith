from flask import Blueprint, request, jsonify

from ..services.contact_services import ContactServices

contact_bp = Blueprint("contact", __name__)

service = ContactServices()


@contact_bp.route("/upload-file", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({"error": "El archivo no fue seleccionado"}), 400

    file = request.files["file"]
    filename = file.filename

    if not filename:
        return jsonify({"error": "El nombre del archivo es inválido"}), 400

    if not filename.endswith(".csv") and not filename.endswith(".xlsx"):
        return (
            jsonify(
                {"error": "Archivo no permitido. Solo se aceptan archivos .csv o .xlsx"}
            ),
            400,
        )

    file_type = filename.split(".")[-1]
    resumen = service.process_file(file, file_type)

    return (
        jsonify(
            {
                "message": f"Archivo '{file.filename}' recibido exitosamente!",
                "resumen": resumen,
            }
        ),
        200,
    )
