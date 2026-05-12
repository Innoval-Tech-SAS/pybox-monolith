class DuplicateContactError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.suggestion = (
            "Revisa el archivo y elimina los contactos duplicados antes de volver a cargarlo."
        )
