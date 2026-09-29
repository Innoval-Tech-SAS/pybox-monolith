"""Catálogo de claves de permisos granulares usadas por la UI y las policies."""

# Org card permissions — activan módulos al entrar a una organización
ORG_PORTFOLIOS = "org.portfolios"
ORG_PAYMENT_METHODS = "org.payment_methods"
ORG_REPORTS = "org.reports"
ORG_USERS = "org.users"
ORG_CAMPAIGNS = "org.campaigns"
ORG_TEMPLATES = "org.templates"
ORG_BILLING = "org.billing"


# Portfolio card permissions — activan módulos al entrar a un portafolio
PORTFOLIO_CLIENTS = "portfolio.clients"
PORTFOLIO_UPLOAD_NEW = "portfolio.upload_new"
PORTFOLIO_UPLOAD_UPDATE = "portfolio.upload_update"
PORTFOLIO_COMMUNICATIONS = "portfolio.communications"
# Emitir notificaciones judiciales sobre un crédito. Va aparte de portfolio.clients
# porque es un acto con peso legal: ver los datos del deudor no debería habilitarlo.
PORTFOLIO_JUDICIAL = "portfolio.judicial"

# Otorgado individualmente a usuarios USER/ORGANIZATION que operan la bandeja de
# WhatsApp ("agentes de WhatsApp") — no es un rol nuevo, solo un permiso suelto (ver
# PermissionAssignmentModel).
MANAGE_WHATSAPP_CHATS = "org.manage_whatsapp_chats"
