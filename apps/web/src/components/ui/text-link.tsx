import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { ComponentPropsWithoutRef } from "react";

type TextLinkProps = Omit<ComponentPropsWithoutRef<typeof Link>, "className"> & {
  children: string;
  showIcon?: boolean;
  className?: string;
};

export function TextLink({
  children,
  showIcon = true,
  className = "",
  ...props
}: TextLinkProps) {
  return (
    <Link {...props} className={`thl-text-link thl-focus-dark ${className}`}>
      <span>{children}</span>
      {showIcon ? (
        <ArrowUpRight size={16} strokeWidth={1.75} aria-hidden="true" />
      ) : null}
    </Link>
  );
}
