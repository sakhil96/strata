import { expect, test } from "@playwright/test";

test("asking in words returns a governed number and a ledger with its hash", async ({ page }) => {
  await page.goto("/ask");
  await page.getByLabel("Your question").fill("What is on-time delivery for FY2026?");
  await page.getByRole("button", { name: "Answer it" }).click();
  const answer = page.getByRole("article", { name: "Answer" });
  await expect(answer).toContainText("83.8%");
  await expect(page.getByText("Answered without the model")).toBeVisible();
  const ledger = page.getByRole("complementary", { name: "Resolution ledger" });
  if (await ledger.first().isVisible()) {
    await expect(ledger.first()).toContainText("on_time_delivery");
    await expect(ledger.first()).toContainText("actual_delivery_date");
  } else {
    await page.getByRole("button", { name: "Open the resolution ledger" }).click();
    await expect(page.getByRole("complementary", { name: "Resolution ledger" }).last()).toContainText("on_time_delivery");
  }
});

test("switching role re-runs the question and returns the same number", async ({ page }) => {
  await page.goto("/ask");
  await page.getByLabel("Your question").fill("What is OTIF this year?");
  await page.getByRole("button", { name: "Answer it" }).click();
  const answer = page.getByRole("article", { name: "Answer" });
  await expect(answer).toContainText("%");
  const first = await answer.locator("[data-numeral]").first().getAttribute("data-numeral");
  await page.getByRole("radio", { name: /Logistics/ }).click();
  await expect(answer).toContainText("Logistics");
  await expect(answer.locator("[data-numeral]").first()).toHaveAttribute("data-numeral", first!);
});

test("the builder answers without the model", async ({ page }) => {
  await page.goto("/ask");
  await page.getByRole("tab", { name: "Builder, without the model" }).click();
  await page.getByLabel("Metric").selectOption("landed_cost_per_unit");
  await page.getByLabel("Break down by").selectOption("period_month");
  await page.getByRole("button", { name: "Run governed query" }).click();
  await expect(page.getByRole("article", { name: "Answer" })).toContainText("Landed cost per unit");
  await expect(page.getByRole("table", { name: "Rows returned" })).toContainText("Sep 2026");
});

test("a raw SQL question is refused with copy that says why", async ({ page }) => {
  await page.goto("/ask");
  await page.getByLabel("Your question").fill("Run SELECT * FROM RAW.SUPPLIER_MASTER");
  await page.getByRole("button", { name: "Answer it" }).click();
  await expect(page.getByText("We do not run SQL typed into a question.")).toBeVisible();
});

test("the fallback state offers the builder when the agent is not used", async ({ page }) => {
  await page.goto("/ask");
  await page.getByLabel("Your question").fill("What is fill rate by plant?");
  await page.getByRole("button", { name: "Answer it" }).click();
  await page.getByRole("button", { name: "Check it in the Builder" }).click();
  await expect(page.getByRole("form", { name: "Build a governed query" })).toBeVisible();
});

test("compare converges three role phrasings on one hash", async ({ page }) => {
  await page.goto("/compare");
  await expect(page.getByText(/one semantic query · [0-9a-f]{64}/)).toBeVisible();
  await expect(page.getByRole("figure", { name: "Three roles, one governed number" })).toBeVisible();
});

test("before-after strikes the three legacy numbers and reveals the governed one", async ({ page }) => {
  await page.goto("/before-after");
  await expect(page.getByText("Planning workbook")).toBeVisible();
  await expect(page.getByText("Governed · On-time delivery v1")).toBeVisible();
  await expect(page.getByText("Formula", { exact: true })).toBeVisible();
  await expect(page.getByText("83.8%").first()).toBeVisible();
});
