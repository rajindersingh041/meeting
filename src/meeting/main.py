import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random

users = [
    "Vishal Kabra",
    "Pavan Patel",
    "Laxman Gorana",
    "Tycoon",
    "Kunal",
    "Mahaveer Jain",
    "Rajeev Kumar",
    "Vix G",
    "Sir",
    "Vikas",
    "Kallicharan",
    "KSMG (16×2=JAA8 VAIDIK)",
    "Aaryan bishnoi.",
    "Kulwant CA",
    "Abhishek",
    "Rage",
    "Ujjwal",
    "Satish Yadav",
    "OT",
    "rohit",
    "Arvind",
    "Ommo",
    "Beast",
    "suresh",
    "Ram Kumar",
    "Tejas Save",
    "QQQ",
    "Sanket",
    "Sanjay Thakkar",
]

# ────────────────────── CONFIGURATION ──────────────────────
MEET_LINK = "https://meet.google.com/aqy-dnyh-qqd"  # ← YOUR OPEN LINK
NUM_USERS = 5
# USER_NAMES = [f"AAAA {i}" for i in range(1, NUM_USERS + 1)]
USER_NAMES = random.sample(users, NUM_USERS)
PAGE_LOAD_WAIT = 10  # Wait after page load
JOIN_TIMEOUT = 60  # Increased for stability
STAY_IN_MEETING = 1800  # 30 minutes (in seconds)

# ────── PERMISSION MODE ──────
# Choose one: "BLOCK" or "FAKE"
# BLOCK: Automatically denies camera/mic permissions (no devices at all)
# FAKE: Auto-accepts permissions but uses fake video/audio streams
PERMISSION_MODE = "BLOCK"  # ← Change to "FAKE" if you prefer fake streams
# ─────────────────────────────────────────────────────────────


def join_meet(user_name: str):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # ────── PERMISSION HANDLING ──────
    if PERMISSION_MODE == "BLOCK":
        print(f"[{user_name}] Mode: BLOCK permissions (no devices)")
        # Block all media permissions - no prompts will appear
        prefs = {
            "profile.default_content_setting_values.media_stream_mic": 2,  # 2=Block
            "profile.default_content_setting_values.media_stream_camera": 2,  # 2=Block
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.notifications": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

    elif PERMISSION_MODE == "FAKE":
        print(f"[{user_name}] Mode: FAKE devices (auto-accept with fake streams)")
        # Auto-accept permissions with fake audio/video
        chrome_options.add_argument(
            "--use-fake-ui-for-media-stream"
        )  # Auto-accept prompts
        chrome_options.add_argument(
            "--use-fake-device-for-media-stream"
        )  # Use fake devices

        # Optional: Allow permissions via prefs (belt-and-suspenders approach)
        prefs = {
            "profile.default_content_setting_values.media_stream_mic": 1,  # 1=Allow
            "profile.default_content_setting_values.media_stream_camera": 1,  # 1=Allow
            "profile.default_content_setting_values.notifications": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
    else:
        raise ValueError(
            f"Invalid PERMISSION_MODE: {PERMISSION_MODE}. Use 'BLOCK' or 'FAKE'"
        )

    # Optional: Run headless (hides browser window)
    # chrome_options.add_argument("--headless=new")

    # Optional: Suppress logging
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    try:
        print(f"[{user_name}] Opening {MEET_LINK}")
        driver.get(MEET_LINK)

        # ────── WAIT FOR UI TO LOAD ──────
        print(f"[{user_name}] Waiting {PAGE_LOAD_WAIT} sec for page...")
        time.sleep(PAGE_LOAD_WAIT)

        # ────── ENTER NAME ──────
        print(f"[{user_name}] Entering name...")
        name_input = WebDriverWait(driver, JOIN_TIMEOUT).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@placeholder='Your name' or contains(@aria-label, 'name')]",
                )
            )
        )
        name_input.clear()
        name_input.send_keys(user_name)

        # ────── CLICK "Continue without microphone and camera" if present ──────
        # This button appears when permissions are blocked
        try:
            continue_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[.//span[contains(text(), 'Continue without') or contains(text(), 'continue without')]]",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", continue_btn)
            print(f"[{user_name}] Clicked 'Continue without mic/camera'")
            time.sleep(1)
        except TimeoutException:
            print(f"[{user_name}] No 'Continue without' button found (proceeding)")

        # ────── CLICK JOIN BUTTON ──────
        print(f"[{user_name}] Looking for Join button...")
        join_button = WebDriverWait(driver, JOIN_TIMEOUT).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[.//span[contains(text(), 'Join now') or contains(text(), 'Ask to join')]]",
                )
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", join_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", join_button)
        print(f"[{user_name}] Join button clicked!")

        # ────── WAIT FOR MEETING TO LOAD ──────
        print(f"[{user_name}] Waiting to enter meeting...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@data-tooltip, 'microphone') or contains(@data-tooltip, 'camera') or contains(@aria-label, 'meeting')]",
                )
            )
        )

        # ────── ENSURE MIC & CAMERA ARE OFF ──────
        def ensure_muted(tooltip_substring, device_name):
            """Ensures a device is muted (only if it's currently ON)"""
            try:
                # Look for button that would turn it OFF (meaning it's currently ON)
                btn = driver.find_element(
                    By.XPATH,
                    f"//div[contains(@data-tooltip, '{tooltip_substring}') and contains(@data-tooltip, 'Turn off')]",
                )
                driver.execute_script("arguments[0].click();", btn)
                print(f"[{user_name}] {device_name} was ON → turned OFF")
                return True
            except NoSuchElementException:
                # Already off or not found
                print(f"[{user_name}] {device_name} already OFF or not available")
                return False

        time.sleep(2)  # Let UI settle
        ensure_muted("microphone", "Microphone")
        ensure_muted("camera", "Camera")

        print(
            f"[{user_name}] ✓ IN MEETING (muted). Staying for {STAY_IN_MEETING // 60} min..."
        )
        time.sleep(STAY_IN_MEETING)

    except TimeoutException as e:
        print(f"[{user_name}] ⚠ TIMEOUT: {e}")
        driver.save_screenshot(f"timeout_{user_name}.png")
    except Exception as e:
        print(f"[{user_name}] ⚠ ERROR: {e}")
        driver.save_screenshot(f"error_{user_name}.png")
    finally:
        driver.quit()
        print(f"[{user_name}] ← Left meeting.")


# ────────────────────── LAUNCH ALL USERS ──────────────────────
if __name__ == "__main__":
    print(f"\n{'=' * 60}")
    print(f"  Google Meet Auto-Join Bot")
    print(f"  Mode: {PERMISSION_MODE}")
    print(f"  Users: {NUM_USERS}")
    print(f"  Duration: {STAY_IN_MEETING // 60} minutes")
    print(f"{'=' * 60}\n")

    threads = []
    for name in USER_NAMES:
        t = threading.Thread(target=join_meet, args=(name,))
        t.start()
        threads.append(t)
        time.sleep(3)  # Stagger to avoid rate-limiting

    print(f"\n[MAIN] All {NUM_USERS} users launched. Waiting for completion...\n")

    for t in threads:
        t.join()

    print(f"\n{'=' * 60}")
    print("  All users have left the meeting.")
    print(f"{'=' * 60}\n")
