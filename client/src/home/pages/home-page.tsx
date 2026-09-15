import { PageMeta } from "@/ui/pages/page-meta";
import { Loader } from "@/ui/components/loader/loader";
import { RoleScopeHome } from "../components/role-scope-home";
import { useHomeContext } from "../hooks/use-home-context";

export const HomePage: React.FC = () => {
  const { role, scope, status } = useHomeContext();

  return (
    <>
      <PageMeta
        title="Dashboard"
        description="Home dinámico"
      />
      {status === "loading" ? (
        <div className="flex items-center justify-center w-full h-[60vh]">
          <Loader />
        </div>
      ) : (
        <RoleScopeHome role={role} scope={scope} />
      )}
    </>
  );
};
