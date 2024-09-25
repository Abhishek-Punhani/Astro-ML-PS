import React from "react";
import { cn } from "../../utils/cn";


interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  className,
  ...props
}) => {
  const baseClasses = "py-2 px-4 rounded text-white font-medium focus:outline-none";
  
  const variantClasses = {
    primary: "bg-blue-600 hover:bg-blue-700",
    secondary: "bg-gray-600 hover:bg-gray-700",
    danger: "bg-red-600 hover:bg-red-700",
  };

  const buttonClass = cn(baseClasses, variantClasses[variant], className);

  return (
    <button className={buttonClass} {...props}>
      {children}
    </button>
  );
};
