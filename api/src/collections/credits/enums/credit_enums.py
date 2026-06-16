from enum import Enum


class CreditTypes(str, Enum):
    FINANCIAL_ENTITY = "Entidad financiera"
    FINTECH = "Fintech"
    SERVICES = "Servicios"
    PRODUCTS = "Productos"
    FASHION = "Moda"
    RETAIL = "Retail"
    PYMES = "Pymes"
    OTHERS = "Otros"
