interface Images {
  src: string;
  alt: string;
}

export interface ColumnImageGridProps {
  cols: number;
  images: Images[];
}
