import { useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { AdminInvoiceListTable } from "@/billing/components/admin-invoice-list-table";
import { useAdminInvoices } from "../hooks/use-admin-invoices";
import { ADMIN_INVOICE_LIST_PAGE_SIZE } from "../constants/pagination";
import EmptyState from "@/ui/components/common/empty-state";
import { Receipt } from "lucide-react";

export const BillingAdminPage: React.FC = () => {
  const navigate = useNavigate();
  const { invoices, total, loading, fetchPage } = useAdminInvoices();
  const totalPages = Math.max(1, Math.ceil(total / ADMIN_INVOICE_LIST_PAGE_SIZE));

  return (
    <>
      <PageMeta title="Facturación" description="Facturación de todas las organizaciones" />
      <ModuleBase pageTitle="Facturación" breadcrumbItems={[]} showBack>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : invoices.length === 0 ? (
          <div className="py-12">
            <EmptyState icon={Receipt} title="No hay facturas registradas" />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            <AdminInvoiceListTable
              invoices={invoices}
              onViewDetail={(id) => navigate(`/billing?invoice=${id}`)}
            />
            {totalPages > 1 && (
              <PaginationWithIcon
                totalPages={totalPages}
                onPageChange={(page) => fetchPage(page, ADMIN_INVOICE_LIST_PAGE_SIZE)}
              />
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
