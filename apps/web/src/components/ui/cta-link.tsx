import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";

type Variant = "primary" | "outline" | "header-compact";

type CtaLinkProps = Omit<ComponentPropsWithoutRef<typeof Link>, "className"> & {
  variant: Variant;
  children: ReactNode;
  className?: string;
  icon?: ReactNode;
};

const variantClass: Record<Variant, string> = {
  primary: "thl-btn-primary thl-focus-primary",
  outline: "thl-btn-outline thl-focus-dark",
  "header-compact": "thl-btn-header-compact thl-focus-dark",
};

export function CtaLink({
  variant,
  children,
  className = "",
  icon,
  ...props
}: CtaLinkProps) {
  return (
    <Link
      {...props}
      data-thl-cta={variant === "primary" ? "primary-red" : variant}
      className={`${variantClass[variant]} ${className}`.trim()}
    >
      {children}
      {icon}
    </Link>
  );
}
