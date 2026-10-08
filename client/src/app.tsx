import { Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router";
import { ProtectedRoute } from "./ui/routes/protected-route";
import { noAuthRouter, authRouter } from "./router";
import { ToastProvider } from "./context/toast-context";
import { ToastContainer } from "./ui/components/notification/toast-container";
import { Loader } from "./ui/components/loader/loader";
import { ErrorBoundary } from "./ui/components/error-boundary";

export const App: React.FC = () => {
  return (
    <ToastProvider>
      <BrowserRouter>
        <ErrorBoundary>
          <Suspense fallback={<Loader variant="page" />}>
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
          </Suspense>
        </ErrorBoundary>
      </BrowserRouter>
      <ToastContainer />
    </ToastProvider>
  );
};
