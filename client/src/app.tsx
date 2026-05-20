import { BrowserRouter, Routes, Route } from "react-router";
import { SignInLayout } from "./ui/layouts/sign-in-layout";
import { noAuthRouter } from "./router";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignInLayout />}>
          <Route
            path="/"
            element={
              <div className="flex items-center justify-center">
                <p className="text-lg font-semibold">Welcome to the App</p>
              </div>
            }
          />
        </Route>

        {noAuthRouter.map((route, index) => {
          return (
            <Route key={index} path={route.path} element={route.element} />
          );
        })}
      </Routes>
    </BrowserRouter>
  );
};
