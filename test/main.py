# from nkiri import Thenkiri
# from playwright.sync_api import TimeoutError

# def get_download(page, locator, timeout_ms=3000):
#     try:
#         with page.expect_download(timeout=timeout_ms) as info:
#             locator.click()
#         return info.value
#     except TimeoutError:
#         return None

# if __name__ == "__main__":

#     try:
#         with Thenkiri() as site:
#             search_term = "stranger"

#             page = site.nkiri

#             # search for series
#             search = site.page.get_by_role("searchbox", name="Search Here")
#             search.fill(search_term)
#             site.page.keyboard.press("Enter")

#             post_link2 = page.post_link2
#             post_link2.first.wait_for()

#             # locate the search from the result
#             for i in range(post_link2.count()):
#                 if search_term in post_link2.nth(i).inner_text().lower(): # match text partially
#                     post_link2.nth(i).click()
#                     break

#             dwld_page = site.page.url

#             # get all downloadlinks
#             dwld_links = page.dwld_links
#             dwld_links.first.wait_for(state="attached")
#             total_links = dwld_links.count()

#             print(f"Total download links found: {total_links-2}")

#             # Ignore first two download links (TO DO: Remove this flaw)
#             for i in range(2, total_links):

#                 current_link = page.dwld_links.nth(i)
#                 current_link.wait_for(state="visible")

#                 download = get_download(site.page, current_link)
            
#                 if not download:
#                     print("Direct link failed. Checking alternative buttons...")
#                     page.dwld_btn.wait_for(state="visible")
#                     page.dwld_btn.click()

#                     page.dwld_btn_cls.wait_for(state="visible")                    
#                     download = get_download(site.page, page.dwld_btn_cls)

#                 downloaded = not download.cancel() if download else None

#                 # 4. Terminate data pipeline stream immediately if successfully caught
#                 if download:
#                     download.cancel()
#                     print("Success: Download event captured and aborted.")
#                 else:
#                     print(f"Warning: Link index {i} did not trigger a download.")

#                 # 5. Return to the target overview page
#                 print("Navigating back to main download listing page...")
#                 site.page.goto(dwld_page)
                
#                 # CRITICAL GUARD: Pause execution until the table of links re-attaches completely
#                 # This prevents the next iteration from trying to click an empty or unfinished DOM
#                 page.dwld_links.first.wait_for(state="attached")

#             print("Program completed")

#     except Exception as e:
#         print(e)


from test.nkiri import Thenkiri
from playwright.sync_api import TimeoutError
import time

# def get_download(page, locator, timeout_ms=4000):
#     try:
#         # Attempt 1: Forced click (Fast 4-second timeout)
#         with page.expect_download(timeout=timeout_ms) as info:
#             locator.click(force=True)
#         return info.value
#     except TimeoutError:
#         print("Forced click timed out. Trying direct JavaScript evaluation...")
#         try:
#             # First, check if the element even exists right now without waiting
#             # state="attached" with a strict, tiny timeout (e.g., 500ms)
#             locator.wait_for(state="attached", timeout=500)
            
#             # Attempt 2: Programmatic JS click using locator.evaluate()
#             # This completely avoids the slow 30-second element_handle() trap!
#             with page.expect_download(timeout=timeout_ms) as info:
#                 locator.evaluate("element => element.click()")
#             return info.value
#         except Exception:
#             # If the element is missing or JS execution fails, exit immediately
#             return None

WAIT_TIMEOUT_MS = 2000
def get_download(page, locator, timeout_ms=4000):
    try:
        locator.wait_for(state="attached", timeout=WAIT_TIMEOUT_MS)
        # Fast-track: Use JS evaluation immediately to bypass ad lag entirely
        with page.expect_download(timeout=timeout_ms) as info:
            locator.evaluate("element => element.click()")
        return info.value
    except TimeoutError:
        try:
            # Fallback: Try a forced physical click if JS execution is blocked
            with page.expect_download(timeout=timeout_ms) as info:
                locator.click(force=True)
            return info.value
        except Exception:
            return None


if __name__ == "__main__":
    try:
        with Thenkiri() as site:
            start = time.time()

            site.page.set_default_timeout(10000)
            search_term = "vincenzo"
            page = site.nkiri

            # 1. Search and Navigate to the series page
            search = site.page.get_by_role("searchbox", name="Search Here")
            search.fill(search_term)
            site.page.keyboard.press("Enter")

            post_link2 = page.post_link2
            post_link2.first.wait_for()

            for i in range(post_link2.count()):
                if search_term in post_link2.nth(i).inner_text().lower():
                    post_link2.nth(i).click()
                    break

            # Cache current movie landing URL anchor
            movie_page_url = site.page.url
            
            page.dwld_links.first.wait_for(state="attached")
            total_links = page.dwld_links.count()
            print(f"Total download links found: {total_links}")

            # 2. Main Action Loop
            for i in range(2, total_links):
                print(f"\nProcessing link {i + 1} of {total_links}...")
                
                # Re-verify dynamic DOM elements are stable
                current_link = page.dwld_links.nth(i)
                current_link.wait_for(state="attached")
                
                # Use programmatic execution or force-clicking on the navigation link too
                try:
                    current_link.click(force=True)
                except Exception:
                    # Defensive fallback if the initial link list gets hit with popups
                    site.page.evaluate("element => element.click()", current_link.element_handle())
                
                # 3. Handle target landing panel                
                download = get_download(site.page, page.dwld_btn)

                # Fallback handler logic using forced parameters
                if not download:
                    print("Direct landing button missed or intercepted. Checking state...")
                    if page.dwld_btn_cls.is_visible():
                        download = get_download(site.page, page.dwld_btn_cls)
                
                # 4. Handle stream cancellation
                if download:
                    download.cancel()
                    print(f"Success: Download event caught and canceled on index {i}.")
                else:
                    print(f"Warning: Link index {i} failed to capture stream context.")

                # 5. Return to home anchor state cleanly
                print("Returning to the main movie page...")
                site.page.goto(movie_page_url)
                page.dwld_links.first.wait_for(state="attached")

            end = time.time()

            print(f"\nProgram finished execution successfully in T-{(end-start):.2f}s")

    except Exception as e:
        print(f"Execution failed: {e}")
