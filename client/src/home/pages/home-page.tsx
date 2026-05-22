import { PageMeta } from "@/ui/pages/page-meta";
import { RoleScopeHome } from "../components/role-scope-home";
import { useHomeContext } from "../hooks/use-home-context";

export const HomePage: React.FC = () => {
  const { role, scope } = useHomeContext();

  return (
    <>
      <PageMeta
        title="Dashboard"
        description="Home dinámico"
      />
      <RoleScopeHome role={role} scope={scope} />
    </>
  );
};
