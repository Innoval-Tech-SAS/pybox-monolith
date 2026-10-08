import { Link } from "react-router";
import { CircleDollarSign, HelpCircle, Link2 } from "lucide-react";

/** Acceso a pagos en línea, en la columna del resumen. */
export const SelfPayCard: React.FC = () => (
  <section className="rounded-2xl border border-brand-100 bg-brand-50 p-5 dark:border-brand-500/20 dark:bg-brand-500/10">
    <div className="flex items-start gap-3">
      <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-brand-500 text-white">
        <Link2 size={20} />
      </span>
      <div>
        <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">
          Paga fácil y seguro
        </h2>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          Realiza tus pagos en línea de manera rápida y segura.
        </p>
      </div>
    </div>
    <Link
      to="/my-credits"
      className="mt-4 inline-flex rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
    >
      Ir a pagos
    </Link>
  </section>
);

/** Par de tarjetas informativas del pie del home. */
export const SelfHomeTips: React.FC = () => (
  <section className="grid gap-4 lg:grid-cols-2">
    <article className="flex items-start gap-4 rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/3">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-blue-light-50 text-blue-light-600 dark:bg-blue-light-500/15 dark:text-blue-light-400">
        <CircleDollarSign size={22} />
      </span>
      <div>
        <h3 className="text-base font-semibold text-gray-800 dark:text-white/90">
          Mantente al día
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Pagar tus obligaciones a tiempo mejora tu historial crediticio y te abre puertas a
          nuevas oportunidades.
        </p>
      </div>
    </article>

    <article className="flex items-start gap-4 rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-900">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-white text-gray-500 dark:bg-gray-800 dark:text-gray-400">
        <HelpCircle size={22} />
      </span>
      <div>
        <h3 className="text-base font-semibold text-gray-800 dark:text-white/90">
          ¿Tienes dudas sobre tu estado?
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Consulta el detalle de tus obligaciones o comunícate con nuestros asesores.
        </p>
        {/* El mockup pone aquí un botón "Contáctanos", pero el titular no tiene todavía
            una ruta de soporte propia (/cs/tickets es del lado de Atención al Cliente).
            Se enlaza al detalle de obligaciones, desde donde sí puede abrir tickets de
            reprogramación y validación de pago. */}
        <Link
          to="/my-credits"
          className="mt-3 inline-flex rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
        >
          Ver mis obligaciones
        </Link>
      </div>
    </article>
  </section>
);
