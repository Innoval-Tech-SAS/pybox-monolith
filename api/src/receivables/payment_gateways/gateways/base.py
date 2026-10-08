"""Protocol común de las pasarelas de cobro de receivables (Wompi, Bold, ...)."""

from dataclasses import dataclass
from typing import Any, Protocol, Union


@dataclass(frozen=True)
class AcceptanceTokens:
    """Tokens firmados por la pasarela con vigencia corta (ver skill `wompi-gateway`,
    Paso 3) — se piden antes de CADA cobro, nunca se cachean a largo plazo. El
    `permalink` de cada uno se le debe mostrar al deudor para que confirme que los leyó
    antes de pagar (requisito legal, Ley 1581 Habeas Data, no solo de UI)."""

    acceptance_token: str
    acceptance_permalink: str
    personal_data_token: str
    personal_data_permalink: str


@dataclass(frozen=True)
class CardPaymentMethod:
    """Datos crudos de la tarjeta -- `WompiGateway.create_transaction` la tokeniza
    server-to-server (mismo mecanismo ya usado por `PaymentSourceService`, con la
    `public_key` de la organización ya descifrada en el backend) antes de cobrar.
    Ningún frontend necesita la `public_key` ni el widget de Wompi para esto."""

    number: str
    cvc: str
    exp_month: str
    exp_year: str
    card_holder: str
    installments: int = 1


@dataclass(frozen=True)
class PsePaymentMethod:
    """PSE no tiene fuente de pago reutilizable en Wompi — solo aplica a un cobro
    `CHECKOUT` puntual, nunca a `AUTOMATIC_3RI`."""

    user_type: int  # 0 = persona natural, 1 = persona juridica
    user_legal_id_type: str
    user_legal_id: str
    financial_institution_code: str
    payment_description: str


@dataclass(frozen=True)
class NequiPaymentMethod:
    phone_number: str


@dataclass(frozen=True)
class BancolombiaTransferPaymentMethod:
    """Tampoco tiene fuente de pago reutilizable en Wompi — mismo alcance que PSE, solo
    `CHECKOUT`."""

    payment_description: str


PaymentMethodInput = Union[
    CardPaymentMethod,
    PsePaymentMethod,
    NequiPaymentMethod,
    BancolombiaTransferPaymentMethod,
]


@dataclass(frozen=True)
class BrowserInfo:
    """Fingerprint del navegador exigido por Wompi para 3D Secure v2 (challenge_v2) en
    transacciones CARD -- ver skill `wompi-gateway`, Paso 6. Nombres en snake_case
    porque viajan tal cual dentro de `customer_data.browser_info` del body de
    `POST /transactions`."""

    browser_color_depth: str
    browser_screen_height: str
    browser_screen_width: str
    browser_language: str
    browser_user_agent: str
    browser_tz: str


@dataclass(frozen=True)
class ThreeDsChallenge:
    """Reto 3DS pendiente de resolver (ver `WompiGateway._to_transaction`). El HTML del
    iframe ya llega decodificado (la API de Wompi lo entrega escapado)."""

    current_step: str
    current_step_status: str
    challenge_html: str


@dataclass(frozen=True)
class WompiTransaction:
    id: str
    status: str
    amount_in_cents: int
    currency: str
    reference: str
    payment_method_type: str
    raw: dict[str, Any]
    three_ds_challenge: ThreeDsChallenge | None = None


@dataclass(frozen=True)
class WompiPaymentSource:
    id: str
    status: str
    type: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class WompiFinancialInstitution:
    financial_institution_code: str
    financial_institution_name: str


class ReceivablesPaymentGateway(Protocol):
    """Protocolo propio de `receivables` (NO el `PaymentGateway` de `billing/gateways/`
    — ver discusión de arquitectura: mismo patrón, interfaces deliberadamente separadas
    porque resuelven credenciales por clave distinta y tienen obligaciones de
    cumplimiento distintas). Una instancia ya trae las credenciales de UNA organización
    resueltas (ver `resolver.py`)."""

    name: str

    async def get_acceptance_tokens(self) -> AcceptanceTokens: ...

    async def create_transaction(
        self,
        reference: str,
        amount_in_cents: int,
        currency: str,
        payment_method: PaymentMethodInput | None,
        acceptance_token: str,
        accept_personal_auth: str,
        customer_email: str,
        payment_source_id: str | None = None,
        browser_info: BrowserInfo | None = None,
    ) -> WompiTransaction:
        """`payment_method` es obligatorio salvo cuando se cobra contra una fuente de
        pago guardada (`payment_source_id` presente, ver Paso 5.3 de la skill) — en ese
        caso Wompi ignora `payment_method` y este se pasa en `None`. `browser_info` se
        exige para CARD (3DS v2, Paso 6) y no aplica a los demás métodos."""
        ...

    async def tokenize_card(
        self, number: str, cvc: str, exp_month: str, exp_year: str, card_holder: str
    ) -> str: ...

    async def tokenize_nequi(self, phone_number: str) -> str: ...

    async def create_payment_source(
        self,
        type: str,
        token: str,
        customer_email: str,
        acceptance_token: str,
        accept_personal_auth: str,
    ) -> WompiPaymentSource: ...

    async def list_pse_financial_institutions(
        self,
    ) -> list[WompiFinancialInstitution]: ...

    async def get_transaction(self, transaction_id: str) -> WompiTransaction: ...

    def verify_webhook_signature(self, event_body: dict[str, Any]) -> bool: ...

    def supports_automatic_charge(self) -> bool:
        """Si esta organización tiene la activación de fraude de Wompi para cobro 3RI
        (skill `wompi-gateway`, Paso 6) — condición necesaria pero no suficiente: la
        fuente de pago también debe cumplir `three_ds_enrolled` y ser Mastercard."""
        ...
