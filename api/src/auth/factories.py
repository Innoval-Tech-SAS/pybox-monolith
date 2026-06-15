from sqlalchemy.ext.asyncio import AsyncSession

from auth.enums.notification_enums import VerificationChannel
from auth.services.email_verification_service import EmailVerificationService
from auth.services.sms_verification_service import SMSVerificationService
from auth.services.verification_service import VerificationService


def get_verification_service(
    channel: VerificationChannel, session: AsyncSession
) -> VerificationService:
    if channel == VerificationChannel.EMAIL:
        return EmailVerificationService(session)
    return SMSVerificationService(session)
