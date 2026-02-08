"""Authentication utilities for mytt_scraper"""

import asyncio
from typing import Dict, Any
from playwright.async_api import async_playwright

from ..config import (
    BROWSER_CONTEXT,
    BROWSER_ARGS,
    LOGIN_URL,
    LOGIN_SELECTORS,
    LOGIN_BUTTON_SELECTORS,
)


async def login_with_playwright(
    username: str,
    password: str,
    headless: bool = True,
    session_cookies: Dict[str, Any] = None
) -> bool:
    """
    Login to mytischtennis.de using Playwright.

    Args:
        username: Email/username for login
        password: Password for login
        headless: Whether to run browser in headless mode
        session_cookies: Optional existing session cookies dict

    Returns:
        True if login successful, False otherwise
    """
    print(f"Logging in as {username}...")
    if headless:
        print("Running in headless mode (captcha will be handled automatically)")
    else:
        print("Running in headed mode - you'll see the browser window")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=headless,
            args=BROWSER_ARGS if not headless else []
        )

        # Create a new browser context with realistic user agent
        context = await browser.new_context(**BROWSER_CONTEXT)

        page = await context.new_page()

        try:
            # Navigate to login page
            print(f"Navigating to {LOGIN_URL}...")
            await page.goto(LOGIN_URL, wait_until='networkidle', timeout=30000)

            print("Page loaded, waiting for login form...")

            # Wait for email input field
            await page.wait_for_selector(LOGIN_SELECTORS[0], timeout=10000)

            # Fill in credentials
            print("Filling in credentials...")
            await page.fill(LOGIN_SELECTORS[0], username)
            await page.fill(LOGIN_SELECTORS[1], password)

            # Wait a moment to simulate human behavior
            await asyncio.sleep(1)

            # Handle checkbox captcha if present
            try:
                print("Checking for captcha checkbox...")
                captcha_checkbox = page.locator('input[type="checkbox"], .captcha-checkbox, [role="checkbox"]').first
                if await captcha_checkbox.is_visible(timeout=2000):
                    print("Found captcha checkbox, clicking it...")
                    await captcha_checkbox.click()
                    await asyncio.sleep(2)  # Wait for verification
            except Exception as e:
                print(f"No captcha checkbox found or already verified: {e}")

            # Find and click the login/submit button
            print("Looking for login button...")
            login_clicked = False

            for selector in LOGIN_BUTTON_SELECTORS:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        print(f"Clicking login button with selector: {selector}")
                        await button.click()
                        login_clicked = True
                        break
                except:
                    continue

            if not login_clicked:
                print("Warning: Could not find login button, trying Enter key...")
                await page.keyboard.press('Enter')

            # Wait for navigation after login
            print("Waiting for login to complete...")
            await page.wait_for_load_state('networkidle', timeout=15000)

            # Check current URL to verify login success
            current_url = page.url
            print(f"Current URL after login: {current_url}")

            # Wait a bit more to ensure cookies are set
            await asyncio.sleep(2)

            # Extract all cookies from the browser session
            cookies = await context.cookies()
            print(f"Extracted {len(cookies)} cookies")

            # Update session cookies dict if provided
            if session_cookies is not None:
                for cookie in cookies:
                    session_cookies[cookie['name']] = cookie['value']

            await browser.close()

            # Verify login by checking if we have auth cookies
            auth_cookies = [c for c in cookies if any(key in c['name'].lower() for key in ['session', 'auth', 'token', 'xsrf'])]
            print(f"Found {len(auth_cookies)} authentication-related cookies")

            if len(cookies) > 0:
                print("✓ Login appears successful!")
                return True
            else:
                print("✗ Login may have failed - no cookies extracted")
                return False

        except Exception as e:
            print(f"✗ Error during login: {e}")
            await browser.close()
            return False


def login(username: str, password: str, headless: bool = True, session_cookies: Dict[str, Any] = None) -> bool:
    """
    Synchronous wrapper for async login.

    Args:
        username: Email/username for login
        password: Password for login
        headless: Whether to run browser in headless mode
        session_cookies: Optional existing session cookies dict

    Returns:
        True if login successful, False otherwise
    """
    return asyncio.run(login_with_playwright(username, password, headless, session_cookies))
