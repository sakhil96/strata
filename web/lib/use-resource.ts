"use client";

import { useEffect, useState } from "react";

import { ApiProblem } from "./api";

export type Resource<T> =
  | { state: "loading" }
  | { state: "ready"; value: T }
  | { state: "failed"; problem: ApiProblem };

export function useResource<T>(load: () => Promise<T>, deps: unknown[]): Resource<T> {
  const [resource, setResource] = useState<Resource<T>>({ state: "loading" });
  useEffect(() => {
    let live = true;
    setResource({ state: "loading" });
    load()
      .then((value) => live && setResource({ state: "ready", value }))
      .catch((err: unknown) => {
        const problem = err instanceof ApiProblem ? err : new ApiProblem({ error: "failed", message: String(err) }, 0);
        if (live) setResource({ state: "failed", problem });
      });
    return () => {
      live = false;
    };
  }, deps);
  return resource;
}
