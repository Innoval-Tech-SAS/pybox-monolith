from pydantic import Field

from base.schema_base import BaseSchema
from contact_methods.enums.contact_method_enums import ContactMethodType
from countries.enums.country_enums import UserDocumentType
from debtors.enums.debtor_enums import DebtorType


class AddressResponse(BaseSchema):
    id: int = Field(description="ID de la dirección")
    address: str = Field(description="Dirección")
    city: str = Field(description="Ciudad")
    state: str = Field(description="Departamento o estado")
    country: str = Field(description="País")
    address_type: str = Field(description="Tipo de dirección (PRIMARY, etc.)")


class ContactMethodResponse(BaseSchema):
    id: int = Field(description="ID del método de contacto")
    contact_type: ContactMethodType = Field(description="Tipo: EMAIL o PHONE")
    contact_value: str = Field(description="Valor del contacto (correo o teléfono)")


class DebtorResponse(BaseSchema):
    id: int = Field(description="ID del deudor")
    full_name: str = Field(description="Nombre completo")
    debtor_type: DebtorType = Field(description="Tipo: Titular o Co-deudor")
    document_type: UserDocumentType = Field(description="Tipo de documento de identidad")
    document_number: str = Field(description="Número de documento")


class DebtorDetailResponse(BaseSchema):
    id: int = Field(description="ID del deudor")
    full_name: str = Field(description="Nombre completo")
    debtor_type: DebtorType = Field(description="Tipo: Titular o Co-deudor")
    document_type: UserDocumentType = Field(description="Tipo de documento")
    document_number: str = Field(description="Número de documento")
    addresses: list[AddressResponse] = Field(description="Direcciones registradas")
    contact_methods: list[ContactMethodResponse] = Field(description="Métodos de contacto")


class DebtorListResponse(BaseSchema):
    items: list[DebtorResponse] = Field(description="Deudores de la página")
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")


class RelatedContactsResponse(BaseSchema):
    debtor: DebtorDetailResponse = Field(description="Deudor titular consultado")
    codebtors: list[DebtorDetailResponse] = Field(description="Co-deudores relacionados en el mismo portafolio")


class CreateDebtorRequest(BaseSchema):
    full_name: str = Field(description="Nombre completo del deudor")
    debtor_type: DebtorType = Field(description="Tipo: Titular o Co-deudor")
    document_type: UserDocumentType = Field(description="Tipo de documento de identidad")
    document_number: str = Field(description="Número de documento")


class CreateAddressRequest(BaseSchema):
    address: str = Field(description="Dirección")
    city: str = Field(description="Ciudad")
    state: str = Field(description="Departamento o estado")
    country: str = Field(description="País")
    address_type: str = Field(default="PRIMARY", description="Tipo de dirección")


class CreateContactMethodRequest(BaseSchema):
    contact_type: ContactMethodType = Field(description="Tipo: EMAIL o PHONE")
    contact_value: str = Field(description="Valor del contacto")
