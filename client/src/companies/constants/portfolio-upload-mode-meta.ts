import type { CsvUploadMode } from "../hooks/use-upload-portfolio-csv";

export const MODE_META: Record<CsvUploadMode, { title: string; description: string; buttonLabel: string }> = {
  append: {
    title: "Subir nuevos clientes",
    description: "Sube un CSV para registrar clientes nuevos y actualizar los ya existentes en esta cartera.",
    buttonLabel: "Subir clientes",
  },
  update: {
    title: "Actualizar clientes",
    description: "Reemplaza los datos de los clientes existentes en esta cartera con los del nuevo archivo.",
    buttonLabel: "Actualizar cartera",
  },
};
