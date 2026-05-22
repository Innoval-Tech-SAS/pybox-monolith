import { BrowserRouter, Routes, Route } from "react-router";
import { ProtectedRoute } from "./ui/routes/protected-route";
import { noAuthRouter, authRouter } from "./router";
import { ToastProvider } from "./context/toast-context";
import { ToastContainer } from "./ui/components/notification/toast-container";

export const App: React.FC = () => {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          {noAuthRouter.map((route, index) => (
            <Route key={index} path={route.path} element={route.element} />
          ))}

          <Route element={<ProtectedRoute />}>
            {authRouter.map((route, index) => (
              <Route key={index} path={route.path} element={route.element} />
            ))}
          </Route>
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </ToastProvider>
  );
};
