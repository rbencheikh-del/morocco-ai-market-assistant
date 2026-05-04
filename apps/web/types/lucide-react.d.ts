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

  export const Activity: LucideIcon;
  export const AlertTriangle: LucideIcon;
  export const BarChart3: LucideIcon;
  export const Bot: LucideIcon;
  export const BrainCircuit: LucideIcon;
  export const Building2: LucideIcon;
  export const LineChart: LucideIcon;
  export const SendHorizonal: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const Sparkles: LucideIcon;
  export const WalletCards: LucideIcon;
}
