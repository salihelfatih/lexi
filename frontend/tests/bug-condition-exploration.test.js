/**
 * Bug Condition Exploration Test
 *
 * **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
 *
 * Property 1: Bug Condition - Next.js Development Server Renders Application
 *
 * CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists
 *
 * This test encodes the EXPECTED behavior: the application should render correctly
 * when running `npm run dev` with standard Next.js. On the current UNFIXED code
 * (with conflicting dependencies and vite.config.mjs present), this test will FAIL,
 * proving that the bug condition exists.
 *
 * When the fix is implemented (conflicts removed, standard Next.js only), this same
 * test will PASS, confirming the bug is fixed.
 */

import { test, expect } from '@playwright/test';
import fc from 'fast-check';

const DEV_SERVER_URL = 'http://localhost:3000';
const SERVER_STARTUP_TIMEOUT = 15000; // 15 seconds - should be enough for a working server

/**
 * Property-Based Test: Application renders correctly with Next.js dev server
 *
 * This property states that for ANY valid navigation to the application,
 * the page should render correctly without displaying a blank page.
 *
 * On UNFIXED code: This will FAIL because conflicting configs cause blank page
 * On FIXED code: This will PASS because standard Next.js renders correctly
 */
test.describe('Bug Condition Exploration: Next.js Development Server', () => {
  test.setTimeout(60000); // 60 second timeout for the entire test

  test('Property 1: Application renders correctly without blank page', async ({ page }) => {
    /**
     * EXPECTED OUTCOME ON UNFIXED CODE: FAIL
     * - Browser displays blank page or times out
     * - No content visible or extremely slow loading
     * - Possible console errors about module resolution or hydration
     * - Server may panic or take minutes to compile
     *
     * EXPECTED OUTCOME ON FIXED CODE: PASS
     * - Application renders with visible content quickly
     * - All components load correctly
     * - No blank page
     */

    console.log('Navigating to application...');

    // Navigate to the application
    const response = await page.goto(DEV_SERVER_URL, {
      waitUntil: 'domcontentloaded',
      timeout: SERVER_STARTUP_TIMEOUT
    });

    // Verify the page loaded successfully
    expect(response.status()).toBe(200);
    console.log('✓ Page responded with status 200');

    // Wait for React to hydrate (reasonable time for a working app)
    await page.waitForTimeout(3000);

    // ASSERTION 1: Page should have a title (not blank)
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title).not.toBe('');
    console.log(`✓ Page title: "${title}"`);

    // ASSERTION 2: Body should have content (not blank page)
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText.trim().length).toBeGreaterThan(0);
    console.log(`✓ Body has content: ${bodyText.trim().length} characters`);

    // ASSERTION 3: Main application container should be visible
    const mainElement = page.locator('main');
    await expect(mainElement).toBeVisible({ timeout: 5000 });
    console.log('✓ Main element is visible');

    // ASSERTION 4: Key application components should be present
    // Based on the HomePage component, we expect these elements:

    // Check for application content (Lexi branding or legal-related text)
    const hasAppContent = await page.locator('text=/Lexi|Legal|Document/i').count() > 0;
    expect(hasAppContent).toBe(true);
    console.log('✓ Application content is present');

    // ASSERTION 5: Page should not be completely blank (has visible elements)
    const visibleElements = await page.locator('*:visible').count();
    expect(visibleElements).toBeGreaterThan(5); // Should have multiple visible elements
    console.log(`✓ Page has ${visibleElements} visible elements`);

    // ASSERTION 6: Check that the page actually rendered (not just HTML shell)
    // A blank page would have very few elements
    const allElements = await page.locator('*').count();
    expect(allElements).toBeGreaterThan(20); // A real app should have many elements
    console.log(`✓ Page has ${allElements} total elements (not blank)`);
  });

  test('Property 1 (Scoped PBT): Server responds consistently across multiple requests', async ({ page }) => {
    /**
     * Property-based test using fast-check to generate multiple test cases
     *
     * This tests that the application renders correctly across different
     * navigation scenarios. On unfixed code, this will fail due to timeouts
     * or blank pages.
     */

    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 3 }), // Test 1-3 navigation attempts
        async (attemptNumber) => {
          console.log(`PBT Attempt ${attemptNumber}: Navigating to application...`);

          // Navigate to the application
          const response = await page.goto(DEV_SERVER_URL, {
            waitUntil: 'domcontentloaded',
            timeout: SERVER_STARTUP_TIMEOUT
          });

          // Verify response is successful
          if (response.status() !== 200) {
            throw new Error(`Expected status 200, got ${response.status()}`);
          }

          // Wait for content to load
          await page.waitForTimeout(2000);

          // Verify page is not blank
          const bodyText = await page.textContent('body');
          if (!bodyText || bodyText.trim().length === 0) {
            throw new Error('Page body is blank');
          }

          // Verify main element is visible
          const mainElement = page.locator('main');
          const isVisible = await mainElement.isVisible();
          if (!isVisible) {
            throw new Error('Main element is not visible');
          }

          console.log(`✓ PBT Attempt ${attemptNumber}: Page rendered successfully`);
          return true;
        }
      ),
      { numRuns: 3 } // Run 3 different scenarios
    );
  });
});

/**
 * EXPECTED COUNTEREXAMPLES ON UNFIXED CODE:
 *
 * 1. Timeout Error: Navigation times out after 15 seconds (server too slow)
 * 2. Blank Page: Browser displays empty white page with no content
 * 3. Missing Elements: Main element not found or not visible
 * 4. No Text Content: Body element has no text or minimal text
 * 5. Server Panic: Console shows "thread panicked" errors from Turbopack
 * 6. Slow Compilation: Server takes minutes to compile (8+ minutes observed)
 * 7. Failed Assertions: Title is empty, visible elements count is low
 *
 * ROOT CAUSE: Conflicting build tool configurations
 * - vite.config.mjs interferes with Next.js bundler (Turbopack)
 * - Conflicting dependencies create module resolution conflicts
 * - Next.js dev server cannot properly initialize with conflicts present
 * - Turbopack panics: "Every task must have a task type"
 *
 * WHEN FIXED: All assertions will pass, confirming application renders correctly
 */
