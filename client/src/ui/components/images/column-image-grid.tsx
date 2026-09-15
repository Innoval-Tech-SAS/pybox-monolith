import { ColumnImageGridProps } from "@/types/props/column-image-grid-props";

export const ColumnImageGrid: React.FC<ColumnImageGridProps> = ({ cols, images }) => {
  return (
    <div
      className={`grid grid-cols-1 gap-5 sm:grid-cols-2 
        md:grid-cols-${cols - 2} lg:grid-cols-${cols - 1} xl:grid-cols-${cols}`}
    >
      {images.map((image, index) => (
        <div key={index}>
          <img
            src={image.src}
            alt={`grid-${index} ${image.alt}`}
            className="border border-gray-200 rounded-xl dark:border-gray-800"
          />
        </div>
      ))}
    </div>
  );
};