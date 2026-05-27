import type { TourStep } from "@/hooks/use-tour";

export const PROFILE_PHOTO_TOUR_KEY = "profile-photo-tour-seen";

export const PROFILE_PHOTO_TOUR_STEPS: TourStep[] = [
  {
    id: "tour-photo-select",
    title: "Elige una foto",
    description: "Selecciona una imagen JPG, PNG o WebP desde tu equipo.",
    side: "bottom",
    align: "start",
  },
  {
    id: "tour-photo-editor",
    title: "Recorta el encuadre",
    description: "Arrastra la imagen dentro del marco para ajustar rostro y hombros antes de guardar.",
    side: "right",
  },
  {
    id: "tour-photo-zoom",
    title: "Ajusta el zoom",
    description: "Usa el control para acercar o alejar la imagen sin perder el formato recomendado.",
    side: "top",
  },
  {
    id: "tour-photo-upload",
    title: "Guarda la foto",
    description: "La imagen se recorta a 512 x 512 px y se sube como tu nueva foto de perfil.",
    side: "top",
    align: "end",
  },
];
