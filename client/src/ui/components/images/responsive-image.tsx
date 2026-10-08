import { ImageProps } from "@/types/props/responsive-image-props";

export const Image: React.FC<ImageProps> = ({ src }) => {
  return (
    <div className="relative">
      <div className="overflow-hidden">
        <img
          src={src}
          alt="Cover"
          className="w-full border border-gray-200 rounded-xl dark:border-gray-800"
        />
      </div>
    </div>
  );
};
