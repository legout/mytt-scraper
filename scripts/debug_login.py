#!/usr/bin/env python3
"""
Debug script to inspect the login process in detail.
Run this in headed mode to see exactly what's happening.
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def debug_login():
    import getpass

    print("=== Debug Login Script ===\n")
    print("This script will open a browser window and show you the login process step by step.\n")

    username = input("Username (email): ").strip()
    password = getpass.getpass("Password: ").strip()

    if not username or not password:
        print("Error: Username and password are required!")
        return

    async with async_playwright() as p:
        # Launch in headed mode so we can see everything
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox'],
            slow_mo=500  # Slow down actions for visibility
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='de-DE',
        )

        page = await context.new_page()

        # Set up console logging
        def log_console(msg):
            print(f"  [Console {msg.type}]: {msg.text}")

        page.on('console', log_console)

        # Set up request/response logging
        def log_request(request):
            print(f"  [Request]: {request.method} {request.url}")

        def log_response(response):
            print(f"  [Response]: {response.status} {response.url}")

        page.on('request', log_request)
        page.on('response', log_response)

        try:
            # Step 1: Navigate to login page
            print("\n[1/5] Navigating to login page...")
            await page.goto("https://www.mytischtennis.de/login", wait_until='networkidle')
            print(f"  Current URL: {page.url}")
            print(f"  Page title: {await page.title()}")

            # Step 2: Inspect the page
            print("\n[2/5] Inspecting login form...")

            # Look for form elements
            email_input = page.locator('input[name="email"], input[type="email"]').first
            password_input = page.locator('input[name="password"], input[type="password"]').first

            if await email_input.is_visible():
                print("  ✓ Email input found")
            else:
                print("  ✗ Email input NOT found")

            if await password_input.is_visible():
                print("  ✓ Password input found")
            else:
                print("  ✗ Password input NOT found")

            # Check for captcha
            print("\n  Checking for captcha elements...")
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="captcha"]',
                '.g-recaptcha',
                '#captcha',
                '[class*="captcha"]',
            ]

            captcha_found = False
            for selector in captcha_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        print(f"  ✓ Captcha found: {selector}")
                        captcha_found = True
                        break
                except:
                    pass

            if not captcha_found:
                print("  - No visible captcha iframe found (may be checkbox type)")

            # Step 3: Fill in credentials
            print("\n[3/5] Filling in credentials...")
            await email_input.fill(username)
            print(f"  ✓ Email filled: {username[:3]}***")
            await password_input.fill(password)
            print(f"  ✓ Password filled (hidden)")

            # Step 4: Check for checkbox captcha
            print("\n[4/5] Handling captcha...")
            try:
                # Look for checkbox (reCAPTCHA v2 checkbox)
                checkbox_selectors = [
                    '.recaptcha-checkbox',
                    'input[type="checkbox"]',
                    '[role="checkbox"]',
                ]

                for selector in checkbox_selectors:
                    try:
                        checkbox = page.locator(selector).first
                        if await checkbox.is_visible(timeout=2000):
                            print(f"  ✓ Found checkbox, clicking...")
                            await checkbox.click()
                            await asyncio.sleep(3)  # Wait for verification
                            print(f"  ✓ Checkbox clicked, waiting for verification...")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"  - No checkbox captcha to handle: {e}")

            # Step 5: Submit login
            print("\n[5/5] Submitting login form...")

            # Try to find and click submit button
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("Einloggen")',
                'button:has-text("Login")',
                'button:has-text("Anmelden")',
                'input[type="submit"]',
            ]

            login_clicked = False
            for selector in login_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        print(f"  ✓ Found login button: {selector}")
                        await button.click()
                        login_clicked = True
                        break
                except:
                    continue

            if not login_clicked:
                print("  - Login button not found, trying Enter key...")
                await page.keyboard.press('Enter')

            # Wait for navigation
            print("\nWaiting for navigation...")
            await page.wait_for_load_state('networkidle', timeout=15000)

            print(f"\nFinal URL: {page.url}")
            print(f"Final title: {await page.title()}")

            # Extract cookies
            cookies = await context.cookies()
            print(f"\nExtracted {len(cookies)} cookies:")
            for cookie in cookies:
                print(f"  - {cookie['name']}: {cookie['value'][:30]}{'...' if len(cookie['value']) > 30 else ''}")

            # Save cookies to file for inspection
            with open('debug_cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            print("\nCookies saved to debug_cookies.json")

            # Check if login was successful
            success = 'community' in page.url or page.url.endswith('/') or 'dashboard' in page.url
            print(f"\n{'✓ Login appears successful!' if success else '✗ Login may have failed'}")

            print("\nPress Enter to close the browser...")
            input()

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            print("\nPress Enter to close the browser...")
            input()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_login())
