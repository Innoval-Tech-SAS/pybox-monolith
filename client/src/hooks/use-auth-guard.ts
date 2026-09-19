import { useEffect } from "react";
import { useNavigate } from "react-router";

export const useAuthGuard = (redirectTo: string = "/admin/sign-in") => {
    const navigate = useNavigate();
    useEffect(() => {
        const userLogged = sessionStorage.getItem("user");
        if (!userLogged) {
            sessionStorage.clear();
            navigate(redirectTo, { replace: true });
        }
    }, [navigate, redirectTo]);
};
