type Props = {
  subtitle: string;
  title: string;
};

export function MaroqLogo({ subtitle, title }: Props) {
  return (
    <div className="brand">
      <svg className="brand-logo" viewBox="0 0 64 64" role="img" aria-label={`${title} logo`}>
        <rect x="6" y="6" width="52" height="52" rx="14" />
        <path d="M18 43V21l14 15 14-15v22" />
        <path d="M20 45h24" />
        <circle cx="46" cy="18" r="3" />
      </svg>
      <div>
        <strong>{title}</strong>
        <span>{subtitle}</span>
      </div>
    </div>
  );
}
