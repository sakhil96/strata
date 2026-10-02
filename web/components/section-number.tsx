interface SectionNumberProps {
  number: string;
}

export function SectionNumber({ number }: SectionNumberProps) {
  return (
    <span className="font-display text-lg font-light text-ash">{number}</span>
  );
}
