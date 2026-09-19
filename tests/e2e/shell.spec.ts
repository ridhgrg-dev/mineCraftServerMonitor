import { expect, test } from "@playwright/test";
test("workspace navigation and health view", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Your workspace starts here" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Check system health" }).click();
  await expect(
    page.getByRole("heading", { name: "Application health" }),
  ).toBeVisible();
  await expect(page.getByText("API process", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Workspace", exact: true }).click();
  await expect(page).toHaveURL("/");
});
test("404 provides recovery", async ({ page }) => {
  const response = await page.goto("/does-not-exist");
  expect(response?.status()).toBe(404);
  await page.getByRole("link", { name: "Return to workspace" }).click();
  await expect(page).toHaveURL("/");
});
