import { useState } from "react";
import { Link } from "react-router";
import { Input } from "../../ui/components/inputs/input";
import { Label } from "../../ui/components/inputs/label";
import { EyeCloseIcon, EyeIcon } from "../../ui/icons";

export const AuthForm: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className="flex flex-col flex-1">
      <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
        <div>
          <div className="mb-5 sm:mb-8">
            <h1 className="mb-2 font-semibold text-gray-800 text-title-sm dark:text-white/90 sm:text-title-md">
              Ingresa a tu cuenta
            </h1>
          </div>
          <div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-6">
                <div>
                  <Label className="text-gray-500">
                    Usuario <span className="text-error-500">*</span>{" "}
                  </Label>
                  <Input placeholder="Usuario" name="user" />
                </div>
                <div>
                  <Label className="text-gray-500">
                    Contraseña <span className="text-error-500">*</span>{" "}
                  </Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Ingresa tu contraseña"
                      name="password"
                    />
                    <span
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute z-30 -translate-y-1/2 cursor-pointer right-4 top-1/2"
                    >
                      {showPassword ? (
                        <EyeIcon className="fill-gray-500 dark:fill-gray-400 size-5" />
                      ) : (
                        <EyeCloseIcon className="fill-gray-500 dark:fill-gray-400 size-5" />
                      )}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between"></div>
                <div>
                  <button
                    type="submit"
                    className="w-full border border-gray-500 p-2 rounded-2xl  hover:bg-gray-400/50"
                  >
                    Iniciar Sesión
                  </button>
                </div>
              </div>
            </form>

            <div className="mt-5">
              <p className="text-sm font-normal text-center text-gray-700 dark:text-gray-400 sm:text-start">
                No tienes cuenta? {""}
                <Link
                  to=""
                  className="text-brand-500 hover:text-brand-600 dark:text-brand-400"
                >
                  Solicita Aquí
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
