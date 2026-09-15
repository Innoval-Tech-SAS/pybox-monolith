import { AvatarProps } from "@/types/props/avatar-props";

import {
  sizeClasses,
  statusSizeClasses,
  statusColorClasses,
} from "@/ui/utils/avatar-utils";

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = "User Avatar",
  size = "medium",
  status = "none",
}) => {
  return (
    <div className={`relative  rounded-full ${sizeClasses[size]}`}>
      <img src={src} alt={alt} className="object-cover rounded-full" />
      {status !== "none" && (
        <span
          className={`absolute bottom-0 right-0 rounded-full border-[1.5px] border-white dark:border-gray-900 ${
            statusSizeClasses[size]
          } ${statusColorClasses[status] || ""}`}
        ></span>
      )}
    </div>
  );
};
