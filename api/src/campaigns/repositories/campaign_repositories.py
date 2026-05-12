from base.repository_base import RepositoryBase
from database.database import db
from campaigns.models.campaign_model import CampaignModel


class CampaignRepository(RepositoryBase[CampaignModel]):
    def __init__(self):
        super().__init__(db, CampaignModel)
