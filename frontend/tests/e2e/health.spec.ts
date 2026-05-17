import { expect, test } from '@playwright/test';


test('home shell is visible', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /territory growth intelligence mas/i })).toBeVisible();
});
