from sqlalchemy.ext.asyncio import AsyncSession

from messaging.enums.notification_enums import VerificationChannel
from messaging.services.email_verification_service import EmailVerificationService
from messaging.services.sms_verification_service import SMSVerificationService
from messaging.services.verification_service import VerificationService


def get_verification_service(
    channel: VerificationChannel, session: AsyncSession
) -> VerificationService:
    if channel == VerificationChannel.EMAIL:
        return EmailVerificationService(session)
    return SMSVerificationService(session)
