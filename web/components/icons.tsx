// A small hand-drawn hairline set; 1px strokes on a 16px grid, coloured by currentColor.
type IconProps = { title?: string; className?: string };

function Glyph({ title, className, children }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 16 16"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1"
      strokeLinecap="square"
      className={className}
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : true}
    >
      {title ? <title>{title}</title> : null}
      {children}
    </svg>
  );
}

export const ArrowRight = (p: IconProps) => (
  <Glyph {...p}>
    <path d="M2.5 8h11M9.5 4l4 4-4 4" />
  </Glyph>
);
export const Mark = (p: IconProps) => (
  <Glyph {...p}>
    <path d="M3 8.5l3 3 7-7" />
  </Glyph>
);
export const Cross = (p: IconProps) => (
  <Glyph {...p}>
    <path d="M4 4l8 8M12 4l-8 8" />
  </Glyph>
);
export const Strike = (p: IconProps) => (
  <Glyph {...p}>
    <path d="M1.5 8h13" />
  </Glyph>
);
export const Bore = (p: IconProps) => (
  <Glyph {...p}>
    <path d="M8 1.5v13M5 4.5h6M5 8h6M5 11.5h6" />
  </Glyph>
);
