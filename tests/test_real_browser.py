"""Test the actual frontend in browser"""
import asyncio
from playwright.async_api import async_playwright

async def test_chat_with_delete():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        page = await browser.new_page()

        # Go to frontend
        await page.goto("https://frontend-ncvmuz9sl-hamdanprofessionals-projects.vercel.app/chat")
        await page.wait_for_load_state("networkidle")

        # Look for chat interface
        try:
            # Check if already logged in
            message_input = await page.wait_for_selector('textarea, input[type="text"]', timeout=5000)
            if message_input:
                print("Chat input found! Testing message...")
                await message_input.fill("Hello! Test message")

                # Find and click send button
                send_btn = await page.query_selector('button[type="submit"], button:has-text("Send")')
                if send_btn:
                    await send_btn.click()
                    print("Message sent!")
                    await asyncio.sleep(5)

                    # Check for response
                    messages = await page.query_selector_all('[data-message], .message, [class*="message"]')
                    print(f"Found {len(messages)} messages after sending")

                    # Look for delete button
                    delete_btns = await page.query_selector_all('button:has-text("Delete"), button[aria-label*="delete"], button:has-text("Clear")')
                    if delete_btns:
                        print(f"Found {len(delete_btns)} delete buttons!")
                    else:
                        print("No delete buttons found - need to add this feature")

        except Exception as e:
            print(f"Chat interface not found or error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chat_with_delete())