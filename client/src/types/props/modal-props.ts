/**
 * Props para el componente Modal.
 * @property isOpen - Indica si el modal está abierto o no.
 * @property onClose - Función que se ejecuta al cerrar el modal.
 * @property className - Clases adicionales para personalizar el modal.
 * @property children - Contenido a renderizar dentro del modal.
 * @property showCloseButton - Muestra un botón de cierre en la esquina superior.
 * @property isFullscreen - Define si el modal ocupa toda la pantalla.
 */
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
  children: React.ReactNode;
  showCloseButton?: boolean;
  isFullscreen?: boolean;
}
