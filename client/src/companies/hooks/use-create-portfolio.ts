import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient, API_URL } from "@/hooks/use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import type { CreatePortfolioResult } from "@/types/companies/company-types";

export const useCreatePortfolio = () => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";

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
    console.log("[portfolio] submit disparado");

    if (!orgId) {
      console.log("[portfolio] ERROR: orgId vacío — falta ?org= en la URL");
      toastError("Error", "No se pudo identificar la organización.");
      return;
    }
    if (!selectedFile) {
      console.log("[portfolio] ERROR: no hay archivo seleccionado");
      toastError("Validación", "Debes adjuntar el archivo CSV.");
      return;
    }

    console.log("[portfolio] orgId:", orgId, "| archivo:", selectedFile.name, "| nombre:", portfolioName);

    const data = new FormData();
    data.set("file", selectedFile);

    const params = new URLSearchParams({ portfolioName, tenantId: orgId });
    if (selectedCountry) params.set("countryId", selectedCountry);

    console.log("[portfolio] disparando request a /portfolios/upload-csv?" + params.toString());

    // Fire-and-forget: backend acepta y procesa en background, notifica por SSE al terminar
    apiClient(`/portfolios/upload-csv?${params}`, { method: "POST", body: data })
      .then(() => console.log("[portfolio] backend aceptó la petición"))
      .catch((err) => console.error("[portfolio] error en la petición:", err));

    sessionStorage.setItem(processingKey, "true");
    setShowSuccessModal(true);
  };

  useEffect(() => {
    if (!showSuccessModal || !orgId) return;
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const es = new EventSource(`${API_URL}/notifications/stream?token=${encodeURIComponent(token)}`);
    es.addEventListener("notification", (e) => {
      try {
        const notif: AppNotification = JSON.parse(e.data);
        if (notif.category === "portfolio") {
          sessionStorage.removeItem(processingKey);
          navigate(`/my-companies/portfolios?org=${orgId}`);
        }
      } catch {
        // malformed event
      }
    });
    es.onerror = () => es.close();
    return () => es.close();
  }, [showSuccessModal, orgId, processingKey, navigate]);

  const handleSuccessModalClose = useCallback(() => {
    sessionStorage.removeItem(processingKey);
    setShowSuccessModal(false);
    navigate(`/my-companies/portfolios?org=${orgId}`);
  }, [navigate, orgId, processingKey]);

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
