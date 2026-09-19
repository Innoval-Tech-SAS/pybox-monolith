from dataclasses import dataclass

from dotenv import load_dotenv

from core.tools.config_tools import get_or_throw

load_dotenv()


@dataclass
class SeedAdminConfig:
    firstname: str = get_or_throw("SEED_ADMIN_FIRSTNAME")
    lastname: str = get_or_throw("SEED_ADMIN_LASTNAME")
    email: str = get_or_throw("SEED_ADMIN_EMAIL")
    password: str = get_or_throw("SEED_ADMIN_PASSWORD")
    phone: str = get_or_throw("SEED_ADMIN_PHONE")
    nationality: str = get_or_throw("SEED_ADMIN_NATIONALITY")
    doc_type: str = get_or_throw("SEED_ADMIN_DOC_TYPE")
    doc_number: str = get_or_throw("SEED_ADMIN_DOC_NUMBER")
