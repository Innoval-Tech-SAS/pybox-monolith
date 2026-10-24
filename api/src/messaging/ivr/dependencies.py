"""Dependencias de FastAPI para inyectar los servicios de IVR y sus repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.ivr.client.helena_client import HelenaClient
from messaging.ivr.config.helena_config import load_helena_config
from messaging.ivr.repository.ivr_execution_repository import IvrExecutionRepository
from messaging.ivr.repository.ivr_flow_repository import IvrFlowRepository
from messaging.ivr.repository.ivr_interaction_repository import IvrInteractionRepository
from messaging.ivr.services.ivr_event_service import (
    IvrEventService,
    make_ivr_event_service,
)
from messaging.ivr.services.ivr_execution_service import IvrExecutionService
from messaging.ivr.services.ivr_flow_service import IvrFlowService
from messaging.ivr.services.ivr_monitor_service import IvrMonitorService
from messaging.ivr.services.ivr_report_service import IvrReportService
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_ivr_flow_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> IvrFlowService:
    return IvrFlowService(
        repo=IvrFlowRepository(session),
        portfolio_repo=PortfolioRepository(session),
    )


def get_helena_client() -> HelenaClient:
    return HelenaClient(load_helena_config())


def get_ivr_event_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> IvrEventService:
    return make_ivr_event_service(session)


def get_ivr_monitor_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> IvrMonitorService:
    return IvrMonitorService(
        interaction_repo=IvrInteractionRepository(session),
        campaign_repo=CampaignRepository(session),
        portfolio_repo=PortfolioRepository(session),
    )


def get_ivr_report_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> IvrReportService:
    return IvrReportService(interaction_repo=IvrInteractionRepository(session))


def get_ivr_execution_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> IvrExecutionService:
    return IvrExecutionService(
        execution_repo=IvrExecutionRepository(session),
        campaign_repo=CampaignRepository(session),
        portfolio_repo=PortfolioRepository(session),
        helena_client=HelenaClient(load_helena_config()),
    )


IvrFlowServiceDep = Annotated[IvrFlowService, Depends(get_ivr_flow_service)]
HelenaClientDep = Annotated[HelenaClient, Depends(get_helena_client)]
IvrEventServiceDep = Annotated[IvrEventService, Depends(get_ivr_event_service)]
IvrMonitorServiceDep = Annotated[IvrMonitorService, Depends(get_ivr_monitor_service)]
IvrReportServiceDep = Annotated[IvrReportService, Depends(get_ivr_report_service)]
IvrExecutionServiceDep = Annotated[
    IvrExecutionService, Depends(get_ivr_execution_service)
]
