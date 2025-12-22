"""Test frontend with Playwright"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_frontend():
    print("=" * 70)
    print("TESTING FRONTEND WITH PLAYWRIGHT")
    print("=" * 70)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Go to frontend
            url = "https://frontend-gmdr4s6rk-hamdanprofessionals-projects.vercel.app/chat"
            print(f"\n1. Opening {url}")

            # Wait for page to load
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"   Status: {response.status}")

            # Take screenshot
            await page.screenshot(path="frontend_screenshot.png")
            print("   ✓ Screenshot saved: frontend_screenshot.png")

            # Check page title
            title = await page.title()
            print(f"   Title: {title}")

            # Check for errors
            errors = []

            # Listen for console errors
            page.on("console", lambda msg: print(f"   Console [{msg.type}]: {msg.text[:100]}"))
            page.on("pageerror", lambda err: errors.append(err))

            # Check for common elements
            try:
                # Check if login form exists
                login_form = await page.query_selector("form")
                if login_form:
                    print("   ✓ Login form found")

                    # Check for email input
                    email_input = await page.query_selector('input[type="email"], input[name="email"]')
                    if email_input:
                        print("   ✓ Email input found")
                        await email_input.fill("test1@test.com")

                        # Check for password input
                        password_input = await page.query_selector('input[type="password"], input[name="password"]')
                        if password_input:
                            print("   ✓ Password input found")
                            await password_input.fill("Test1234")

                            # Look for submit button
                            submit_btn = await page.query_selector('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
                            if submit_btn:
                                print("   ✓ Login button found")

                                # Click login
                                await submit_btn.click()
                                print("   ✓ Login clicked")

                                # Wait for navigation to chat
                                await page.wait_for_url("**/chat", timeout=10000)
                                print("   ✓ Redirected to chat")

                                # Look for chat interface
                                await asyncio.sleep(2)  # Wait for chat to load

                                # Check for message input
                                message_input = await page.query_selector('input[type="text"], textarea, [contenteditable="true"]')
                                if message_input:
                                    print("   ✓ Chat input found")
                                    await message_input.fill("Hello! Testing with Playwright")

                                    # Look for send button
                                    send_btn = await page.query_selector('button:has-text("Send"), button[aria-label*="send"], button[type="submit"]')
                                    if send_btn:
                                        print("   ✓ Send button found")
                                        await send_btn.click()
                                        print("   ✓ Message sent")

                                        # Wait for response
                                        await asyncio.sleep(5)

                                        # Check for response
                                        messages = await page.query_selector_all('[data-testid*="message"], .message, [class*="message"]')
                                        print(f"   ✓ Found {len(messages)} message elements")

                                        # Check for AI response
                                        page_content = await page.content()
                                        if "Hello" in page_content or "task" in page_content.lower() or "help" in page_content.lower():
                                            print("   ✓ AI response detected")
                                        else:
                                            print("   ⚠ No clear AI response found")
                                    else:
                                        print("   ✗ Send button not found")
                                else:
                                    print("   ✗ Chat input not found")
                            else:
                                print("   ✗ Submit button not found")
                        else:
                            print("   ✗ Password input not found")
                    else:
                        print("   ✗ Email input not found")
                else:
                    print("   ✗ No login form found")

                    # Maybe already logged in - check for chat interface
                    print("\n   Checking if already logged in...")
                    chat_input = await page.query_selector('input[type="text"], textarea')
                    if chat_input:
                        print("   ✓ Already logged in - chat interface found")
                        await chat_input.fill("Hello from Playwright!")
                        send_btn = await page.query_selector('button[type="submit"]')
                        if send_btn:
                            await send_btn.click()
                            print("   ✓ Message sent")
                            await asyncio.sleep(5)
                            messages = await page.query_selector_all('[class*="message"]')
                            print(f"   ✓ Found {len(messages)} message elements")

            except Exception as e:
                print(f"   ✗ Error during interaction: {e}")
                errors.append(e)

            # Print any errors
            if errors:
                print("\n   ERRORS FOUND:")
                for err in errors:
                    print(f"   - {err}")

            # Final check - check network requests
            print("\n2. Checking network requests...")

            # Check if API calls are being made
            api_requests = []

            def capture_request(request):
                if "api" in request.url or "backend" in request.url:
                    api_requests.append({
                        "url": request.url,
                        "method": request.method,
                        "status": None
                    })

            def capture_response(response):
                if "api" in response.url or "backend" in response.url:
                    for req in api_requests:
                        if req["url"] == response.url:
                            req["status"] = response.status
                            break

            page.on("request", capture_request)
            page.on("response", capture_response)

            # Refresh to capture network calls
            await page.reload(wait_until="networkidle")
            await asyncio.sleep(3)

            print(f"   API requests made: {len(api_requests)}")
            for req in api_requests:
                status_text = f"({req['status']})" if req['status'] else "(pending)"
                print(f"   - {req['method']} {req['url']} {status_text}")

                if req['status'] and req['status'] >= 400:
                    print(f"     ✗ HTTP ERROR {req['status']}")

        except Exception as e:
            print(f"   ✗ Test failed: {e}")

        finally:
            await browser.close()
            print("\n" + "=" * 70)
            print("TEST COMPLETE")
            print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_frontend())