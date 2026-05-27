import { useState } from "react";
import { useToast } from "@/context/toast-context";
import { getSession, setSessionUser } from "@/auth/utils/auth-session-utils";
import { useApiClient } from "@/hooks/use-api-client";

interface ProfilePhotoResponse {
  profilePhotoUrl?: string;
  profile_photo_url?: string;
}

export const useUpdateProfilePhoto = () => {
  const { apiClient } = useApiClient();
  const { success } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const updateProfilePhoto = async (image: Blob): Promise<string> => {
    setLoading(true);
    setError(null);
    console.log("[profile-photo] upload start", {
      blobSize: image.size,
      blobType: image.type,
    });

    try {
      const data = new FormData();
      data.append("file", image, "foto-perfil.png");
      const response = (await apiClient("/users/me/profile-photo", {
        method: "PUT",
        body: data,
      })) as ProfilePhotoResponse;
      console.log("[profile-photo] upload response", response);

      const profilePhotoUrl = response.profile_photo_url ?? response.profilePhotoUrl;
      if (!profilePhotoUrl) throw new Error("La API no devolvió la foto de perfil.");

      const session = getSession();
      console.log("[profile-photo] session before update", {
        profilePhoto: session?.profilePhoto,
        profilePhotoUrl: session?.profilePhotoUrl,
        profile_photo_url: session?.profile_photo_url,
      });
      setSessionUser({
        ...(session ?? {}),
        profilePhoto: profilePhotoUrl,
        profilePhotoUrl,
        profile_photo_url: profilePhotoUrl,
      });
      console.log("[profile-photo] session after update", {
        profilePhoto: profilePhotoUrl,
        profilePhotoUrl,
        profile_photo_url: profilePhotoUrl,
      });
      success("Foto actualizada", "Tu perfil ya usa la nueva imagen.");
      return profilePhotoUrl;
    } catch (e) {
      const message = e instanceof Error ? e.message : "Error al subir la foto";
      console.log("[profile-photo] upload error", e);
      setError(message);
      throw e;
    } finally {
      console.log("[profile-photo] upload end");
      setLoading(false);
    }
  };

  return { updateProfilePhoto, loading, error, clearError };
};
