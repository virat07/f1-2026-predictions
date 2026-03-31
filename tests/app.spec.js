import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/F1 2026 Predictions/);
});

test('hero section is visible', async ({ page }) => {
  await page.goto('/');
  const hero = page.locator('section#hero');
  await expect(hero).toBeVisible();
  await expect(page.getByText(/NEW ERA OF RACING/i)).toBeVisible();
});

test('all major sections load', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('section#drivers')).toBeVisible();
  await expect(page.locator('section#constructors')).toBeVisible();
  await expect(page.locator('section#calendar')).toBeVisible();
  await expect(page.locator('section#leaderboard')).toBeVisible();
  await expect(page.locator('section#regulations')).toBeVisible();
  await expect(page.locator('section#hot-takes')).toBeVisible();
});

test('can scroll and update navbar active state', async ({ page }) => {
  await page.goto('/');
  const calendarSection = page.locator('section#calendar');
  await calendarSection.scrollIntoViewIfNeeded();
  
  // Wait for intersection observer / debounce
  await page.waitForTimeout(1000);
  
  // Check if calendar is active in nav
  const activeLink = page.locator('nav .nav-link.active');
  await expect(activeLink).toHaveAttribute('href', '#calendar');
});
test('race calendar displays actual results', async ({ page }) => {
  await page.goto('/');
  const calendarSection = page.locator('section#calendar');
  await calendarSection.scrollIntoViewIfNeeded();

  // Wait for data to fetch
  await page.waitForTimeout(2000);

  // Check if at least one race result block is present (for completed rounds)
  const results = page.locator('.rc-result');
  const count = await results.count();
  console.log(`Found ${count} completed race results`);
  
  if (count > 0) {
    await expect(results.first()).toBeVisible();
    await expect(results.first().locator('.rc-result-val').first()).not.toBeEmpty();
  }
});
