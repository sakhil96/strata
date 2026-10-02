import type { ReactNode } from "react";

export function Section({
  numeral,
  title,
  lede,
  children,
  id,
}: {
  numeral: string;
  title: string;
  lede?: ReactNode;
  children?: ReactNode;
  id?: string;
}) {
  return (
    <section id={id} aria-labelledby={`${id ?? numeral}-title`} className="rule grid grid-cols-12 gap-x-3 pt-4">
      <p className="col-span-12 font-display text-xl font-light text-ash md:col-span-2" aria-hidden>
        {numeral}
      </p>
      <div className="col-span-12 md:col-span-10">
        <h2 id={`${id ?? numeral}-title`} className="font-display text-2xl font-light text-bone">
          {title}
        </h2>
        {lede ? <div className="mt-1 max-w-measure text-base text-ash">{lede}</div> : null}
        {children ? <div className="mt-4">{children}</div> : null}
      </div>
    </section>
  );
}

export function PageHead({
  numeral,
  kicker,
  title,
  lede,
}: {
  numeral: string;
  kicker: string;
  title: ReactNode;
  lede?: ReactNode;
}) {
  return (
    <header className="grid grid-cols-12 gap-x-3 pb-6 pt-8">
      <p className="col-span-12 font-display text-xl font-light text-ash md:col-span-2" aria-hidden>
        {numeral}
      </p>
      <div className="col-span-12 md:col-span-9">
        <p className="micro">{kicker}</p>
        <h1 className="mt-1 font-display text-3xl font-light text-bone">{title}</h1>
        {lede ? <div className="mt-2 max-w-measure text-lg text-ash">{lede}</div> : null}
      </div>
    </header>
  );
}
