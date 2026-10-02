import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const PAGES = [
  "/",
  "/ask",
  "/compare",
  "/before-after",
  "/glossary",
  "/lineage/otif",
  "/governance",
  "/operations",
  "/about",
  "/styleguide",
];

function watchConsole(page: Page): string[] {
  const problems: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") problems.push(m.text());
  });
  page.on("pageerror", (e) => problems.push(e.message));
  return problems;
}

for (const path of PAGES) {
  test(`${path} renders under the content security policy with no console errors and no axe violations`, async ({ page }) => {
    const problems = watchConsole(page);
    await page.emulateMedia({ reducedMotion: "reduce" });
    const response = await page.goto(path);
    expect(response?.status()).toBe(200);
    await expect(page.locator("main h1").first()).toBeVisible();
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);
    expect(problems, problems.join("\n")).toEqual([]);
    const audit = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(audit.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`)).toEqual([]);
  });
}

test("security headers are on every page", async ({ request }) => {
  for (const path of PAGES) {
    const headers = (await request.get(path)).headers();
    expect(headers["strict-transport-security"]).toContain("max-age=");
    const csp = headers["content-security-policy"];
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp.split(";").find((d) => d.trim().startsWith("script-src"))).not.toContain("unsafe-inline");
    expect(headers["x-content-type-options"]).toBe("nosniff");
  }
});
