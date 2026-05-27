import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import { useTour } from "@/hooks/use-tour";
import { PROFILE_PHOTO_TOUR_KEY, PROFILE_PHOTO_TOUR_STEPS } from "../constants/profile-photo-tour";

export const useProfilePhotoTour = (ready: boolean) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();

  useTour(ready && !loading, PROFILE_PHOTO_TOUR_KEY, PROFILE_PHOTO_TOUR_STEPS, {
    dismissed: isDismissed(PROFILE_PHOTO_TOUR_KEY),
    dismissBtnText: "Omitir tour",
    onPermanentDismiss: () => dismiss(PROFILE_PHOTO_TOUR_KEY),
    showPermanentDismissOnEveryStep: true,
  });
};
