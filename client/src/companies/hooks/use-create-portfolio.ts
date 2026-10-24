import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import { openNotificationStream } from "@/utils/notification-stream";
import { useOrgModule } from "./use-org-module";

export const useCreatePortfolio = () => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const { orgId, buildOrgPath } = useOrgModule();

  const [portfolioName, setPortfolioName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedCountry, setSelectedCountry] = useState("");

  const processingKey = `portfolioProcessing_${orgId}`;
  const [showSuccessModal, setShowSuccessModal] = useState(
    () => sessionStorage.getItem(processingKey) === "true",
  );

  const formRef = useRef<HTMLFormElement>(null);

  const handleReset = useCallback(() => {
    setPortfolioName("");
    setSelectedFile(null);
    setSelectedCountry("");
    formRef.current?.reset();
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!orgId) {
      toastError("Error", "No se pudo identificar la empresa.");
      return;
    }
    if (!selectedFile) {
      toastError("Validación", "Debes adjuntar el archivo CSV.");
      return;
    }

    const data = new FormData();
    data.set("file", selectedFile);

    const params = new URLSearchParams({ portfolioName, organizationId: orgId });
    if (selectedCountry) params.set("countryId", selectedCountry);

    // El backend acepta y procesa en background, notifica por SSE al terminar
    apiClient<unknown>(`/portfolios/upload-csv?${params}`, { method: "POST", body: data })
      .then(() => {
        sessionStorage.setItem(processingKey, "true");
        setShowSuccessModal(true);
      })
      .catch((err) => {
        console.error("[portfolio] error en la petición:", err);
        toastError("Error", "No se pudo iniciar la carga. Intenta de nuevo.");
      });
  };

  useEffect(() => {
    if (!showSuccessModal || !orgId) return;
    if (!sessionStorage.getItem("user")) return;

    const es = openNotificationStream();
    es.addEventListener("notification", (e) => {
      try {
        const notif: AppNotification = JSON.parse(e.data);
        if (notif.category === "portfolio") {
          sessionStorage.removeItem(processingKey);
          navigate(buildOrgPath("/my-companies/portfolios"));
        }
      } catch {
        // malformed event
      }
    });
    es.onerror = () => {};
    return () => es.close();
  }, [showSuccessModal, orgId, processingKey, navigate, buildOrgPath]);

  const handleSuccessModalClose = useCallback(() => {
    sessionStorage.removeItem(processingKey);
    setShowSuccessModal(false);
    navigate(buildOrgPath("/my-companies/portfolios"));
  }, [navigate, buildOrgPath, processingKey]);

  return {
    showSuccessModal,
    handleSuccessModalClose,
    orgId,
    portfolioName, setPortfolioName,
    selectedFile, setSelectedFile,
    selectedCountry, setSelectedCountry,
    formRef,
    handleReset,
    handleSubmit,
  };
};
