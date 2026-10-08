import { useCallback, useEffect, useState } from "react";
import {
  loadGoogleScript,
  renderGoogleButton,
} from "@/auth/utils/google-script-utils";

export const useGoogleAuth = () => {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let mounted = true;
    loadGoogleScript()
      .then(() => {
        if (mounted) setReady(true);
      })
      .catch(() => {
        if (mounted) setReady(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const renderButtonToContainer = useCallback(
    (container: HTMLElement, width: number, onToken: (token: string) => void) => {
      renderGoogleButton(container, width, onToken);
    },
    [],
  );

  return { renderButtonToContainer, ready };
};
