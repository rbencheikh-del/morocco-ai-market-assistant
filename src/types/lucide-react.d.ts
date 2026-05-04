declare module "lucide-react" {
  import type { ForwardRefExoticComponent, RefAttributes, SVGProps } from "react";

  export interface LucideProps extends SVGProps<SVGSVGElement> {
    size?: string | number;
    strokeWidth?: string | number;
    absoluteStrokeWidth?: boolean;
  }

  export type LucideIcon = ForwardRefExoticComponent<
    Omit<LucideProps, "ref"> & RefAttributes<SVGSVGElement>
  >;

  export const Bell: LucideIcon;
  export const LineChart: LucideIcon;
  export const RefreshCw: LucideIcon;
  export const Search: LucideIcon;
  export const Send: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const SlidersHorizontal: LucideIcon;
}
