import uuid

from app_platform.countries.enums.country_enums import Nationality
from core.config.logger import logger
from app_platform.notifications.services.notification_service import NotificationService
from receivables.portfolios.services.portfolio_csv_service import PortfolioCsvService

uploading_orgs: set[uuid.UUID] = set()


async def process_and_notify(
    file_bytes: bytes,
    filename: str,
    organization_id: uuid.UUID,
    portfolio_name: str | None,
    country: Nationality | None,
    user_id: uuid.UUID,
    service: PortfolioCsvService,
    notification_service: NotificationService,
) -> None:
    logger.info("[portfolio] background task iniciado | org=%s nombre=%s", organization_id, portfolio_name)
    try:
        result = await service.process_csv(
            file_bytes=file_bytes,
            filename=filename,
            organization_id=organization_id,
            portfolio_name=portfolio_name,
            country=country,
        )
        logger.info("[portfolio] process_csv terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Portafolio listo",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={result.portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
        logger.info("[portfolio] notificación enviada al usuario %s", user_id)
    except Exception:
        logger.exception("[portfolio] error en background task | org=%s", organization_id)
    finally:
        uploading_orgs.discard(organization_id)
        logger.info("[portfolio] org liberada del set activo | org=%s", organization_id)


async def append_and_notify(
    file_bytes: bytes,
    filename: str,
    portfolio_id: uuid.UUID,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    service: PortfolioCsvService,
    notification_service: NotificationService,
) -> None:
    logger.info("[portfolio-append] background task iniciado | portfolio=%s", portfolio_id)
    try:
        result = await service.append_csv(portfolio_id, file_bytes, filename)
        logger.info("[portfolio-append] terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Datos agregados al portafolio",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
    except Exception:
        logger.exception("[portfolio-append] error | portfolio=%s", portfolio_id)
    finally:
        uploading_orgs.discard(organization_id)


async def update_and_notify(
    file_bytes: bytes,
    filename: str,
    portfolio_id: uuid.UUID,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    service: PortfolioCsvService,
    notification_service: NotificationService,
) -> None:
    logger.info("[portfolio-update] background task iniciado | portfolio=%s", portfolio_id)
    try:
        result = await service.update_csv(portfolio_id, file_bytes, filename)
        logger.info("[portfolio-update] terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Portafolio actualizado",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
    except Exception:
        logger.exception("[portfolio-update] error | portfolio=%s", portfolio_id)
    finally:
        uploading_orgs.discard(organization_id)
