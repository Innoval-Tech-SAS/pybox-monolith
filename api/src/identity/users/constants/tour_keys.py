# Tours guiados de la interfaz — deben coincidir con las claves del frontend
# (client/src/**/constants/*-tour.ts). Solo estas claves pueden persistirse
# como descartadas.
ORG_MODULES_TOUR = "org-modules-tour-seen"
PORTFOLIOS_LIST_TOUR = "portfolios-list-tour-seen"
PORTFOLIO_MODULES_TOUR = "portfolio-modules-tour-seen"
COMMUNICATIONS_MODULES_TOUR = "communications-modules-tour-seen"
PROFILE_PHOTO_TOUR = "profile-photo-tour-seen"

TOUR_KEYS = frozenset(
    {
        ORG_MODULES_TOUR,
        PORTFOLIOS_LIST_TOUR,
        PORTFOLIO_MODULES_TOUR,
        COMMUNICATIONS_MODULES_TOUR,
        PROFILE_PHOTO_TOUR,
    }
)
