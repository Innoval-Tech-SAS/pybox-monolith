import { useEffect } from "react";
import { useNavigate } from "react-router";

export const useAuthGuard = (redirectTo: string = "/admin/sign-in") => {
    const navigate = useNavigate();
    useEffect(() => {
        const token = sessionStorage.getItem("accessToken");
        const userLogged = sessionStorage.getItem("user")
        if (!token || !userLogged) {
            sessionStorage.clear();
            navigate(redirectTo, { replace: true });
        }
    }, [navigate, redirectTo]);
};
