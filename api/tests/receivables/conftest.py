"""Fixtures compartidas del módulo receivables (portfolios/debtors/credits).

No hay endpoint JSON para crear un portfolio -- solo existe `POST
/portfolios/upload-csv` (multipart, con BackgroundTasks). Para los tests que
solo necesitan "un portfolio/deudor/crédito que exista" se construyen directo
por SQLAlchemy (mucho más rápido y confiable que armar un CSV real); los tests
del endpoint de upload en sí arman un CSV real por separado.
"""

import csv
import io
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from core.security.services.encrypt_service import encrypt_service
from identity.organizations.enums.organization_enums import EntitySectors, VerificationStatus
from identity.organizations.models.organization_model import OrganizationModel
from identity.users.enums.user_enums import UserRole, UserScope
from receivables.credits.models.credit_model import CreditModel
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.debtors.models.debtor_model import DebtorModel
from receivables.portfolios.constants.portfolio_csv_constants import (
    INSTALLMENT_TEMPLATE_COLUMNS,
    PORTFOLIO_TEMPLATE_COLUMNS,
)
from receivables.portfolios.models.portfolio_model import PortfolioModel
from tests.factories import get_user_by_email, register_payload, unique_document_number


def build_portfolio_csv(rows: list[dict[str, str]]) -> bytes:
    """CSV mínimo válido para `POST /portfolios/upload-csv*`: header completo
    (`PORTFOLIO_TEMPLATE_COLUMNS`, lo mismo que sirve `GET .../template`), filas con
    solo los campos que importan -- el resto queda vacío y el parser lo tolera."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=PORTFOLIO_TEMPLATE_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in PORTFOLIO_TEMPLATE_COLUMNS})
    return buf.getvalue().encode("utf-8")


def portfolio_csv_row(**overrides) -> dict[str, str]:
    row = {
        "Numero de documento": unique_document_number(),
        "Nombre del titular": "Titular de Prueba",
        "Numero de credito": f"CR-{uuid.uuid4().hex[:10]}",
        "Fecha Desembolso": "01/01/2026",
    }
    row.update(overrides)
    return row


def build_installments_csv(rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=INSTALLMENT_TEMPLATE_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in INSTALLMENT_TEMPLATE_COLUMNS})
    return buf.getvalue().encode("utf-8")


def _column_letter(index: int) -> str:
    """0-based -> letra de columna Excel (0 -> 'A', 25 -> 'Z', 26 -> 'AA', ...)."""
    letters = ""
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def build_minimal_xlsx(header: list[str], rows: list[list[str]]) -> bytes:
    """Arma un .xlsx (OOXML) minimo a mano, sin depender de xlsxwriter/openpyxl (no son
    dependencias del proyecto -- solo `fastexcel`, que es de solo lectura). Usa celdas
    `inlineStr` para evitar la tabla de `sharedStrings.xml`. Suficiente para probar la
    rama `is_xlsx` de `PortfolioFileParser.parse` con un archivo real, no un mock."""
    import zipfile
    from xml.sax.saxutils import escape

    def _row_xml(row_index: int, values: list[str]) -> str:
        cells = "".join(
            f'<c r="{_column_letter(i)}{row_index}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'
            for i, v in enumerate(values)
        )
        return f'<row r="{row_index}">{cells}</row>'

    sheet_rows = "".join(
        _row_xml(idx, values) for idx, values in enumerate([header, *rows], start=1)
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{sheet_rows}</sheetData>"
        "</worksheet>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


AUTH_BASE = "/api/v1/auth"
ORG_BASE = "/api/v1/organizations"


@pytest_asyncio.fixture
async def verified_org_id(client, db_session, auth_as, make_user_session_factory) -> str:
    """Org real, con `verification_status=APPROVED` -- requisito de
    `require_verified_org` para casi todo lo que toca portafolios."""
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    user = await get_user_by_email(db_session, payload["email"])
    global_admin = make_user_session_factory(user_id=user.id, role=UserRole.ADMIN, scope=UserScope.GLOBAL)
    authed = auth_as(global_admin)
    create = await authed.post(f"{ORG_BASE}/", json={"name": f"Org {uuid.uuid4().hex[:8]}", "sector": "FINTECH"})
    assert create.status_code == 201
    org_id = create.json()["id"]

    org = await db_session.get(OrganizationModel, uuid.UUID(org_id))
    org.verification_status = VerificationStatus.APPROVED
    await db_session.flush()
    auth_as.clear()
    # El registro real (arriba) dejó una cookie de sesión real en `client` -- sin
    # esto, un test que dependa de este fixture para armar datos y luego pruebe
    # "sin auth" en el mismo `client` compartido queda autenticado por accidente.
    client.cookies.clear()
    return org_id


@pytest_asyncio.fixture
async def real_admin_user_id(client, db_session) -> uuid.UUID:
    """Usuario real para respaldar sesiones fake cuyo endpoint graba el actor en una
    FK real (`actualizado_por`, `otorgado_por`, `creado_por`, etc.) -- con un
    `user_id` 100% inventado esas escrituras revientan con ForeignKeyViolationError."""
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    user = await get_user_by_email(db_session, payload["email"])
    return user.id


def build_organization(**overrides) -> OrganizationModel:
    """No es fixture: para tests que necesitan varias organizaciones distintas (p.
    ej. reproducir un IDOR cross-organización) sin pasar por el flujo HTTP completo
    de `verified_org_id`."""
    defaults = dict(
        name=f"Org {uuid.uuid4().hex[:8]}",
        sector=EntitySectors.FINTECH,
        verification_status=VerificationStatus.APPROVED,
    )
    defaults.update(overrides)
    return OrganizationModel(**defaults)


def build_portfolio(organization_id: uuid.UUID, **overrides) -> PortfolioModel:
    defaults = dict(
        name=f"Portafolio {uuid.uuid4().hex[:8]}",
        organization_id=organization_id,
        country="CO",
    )
    defaults.update(overrides)
    return PortfolioModel(**defaults)


@pytest_asyncio.fixture
async def real_portfolio(db_session, verified_org_id) -> PortfolioModel:
    portfolio = PortfolioModel(
        name=f"Portafolio {uuid.uuid4().hex[:8]}",
        organization_id=uuid.UUID(verified_org_id),
        country="CO",
    )
    db_session.add(portfolio)
    await db_session.flush()
    return portfolio


def build_debtor(**overrides) -> DebtorModel:
    """No es fixture: cada llamado genera un deudor con documento único, para
    poder crear varios en el mismo test (titular + codeudor, etc.)."""
    doc_number = overrides.pop("document_number_plain", unique_document_number())
    defaults = dict(
        full_name="Deudor de Prueba",
        debtor_type=DebtorType.DEBTOR,
        document_type="CC",
        document_number=encrypt_service.encrypt_to_str(doc_number),
        document_number_hash=encrypt_service.hash_document(doc_number),
    )
    defaults.update(overrides)
    return DebtorModel(**defaults)


@pytest_asyncio.fixture
async def real_debtor(db_session) -> DebtorModel:
    debtor = build_debtor()
    db_session.add(debtor)
    await db_session.flush()
    return debtor


def build_credit(portfolio_id: uuid.UUID, debtor_id: uuid.UUID, **overrides) -> CreditModel:
    defaults = dict(
        credit_number=f"CR-{uuid.uuid4().hex[:10]}",
        disbursed_date=datetime.now(timezone.utc),
        initial_term=12,
        portfolio_id=portfolio_id,
        debtor_id=debtor_id,
    )
    defaults.update(overrides)
    return CreditModel(**defaults)


@pytest_asyncio.fixture
async def real_credit(db_session, real_portfolio, real_debtor) -> CreditModel:
    credit = build_credit(real_portfolio.id, real_debtor.id)
    db_session.add(credit)
    await db_session.flush()
    return credit
