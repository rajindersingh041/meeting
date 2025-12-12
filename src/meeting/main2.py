from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

# List of random names
RANDOM_NAMES = [
    "Alex Smith",
    "Jordan Lee",
    "Taylor Brown",
    "Morgan Davis",
    "Casey Wilson",
    "Riley Johnson",
    "Parker Martinez",
    "Quinn Anderson",
]


def setup_driver():
    """Configure Chrome driver with media completely disabled"""
    chrome_options = Options()

    # Disable all permissions and media access
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,  # 1=allow, 2=block
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Additional arguments to block media
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-media-stream")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")

    # Block all permission requests
    chrome_options.add_argument("--deny-permission-prompts")

    # Disable automation detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Start maximized
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)

    # Execute CDP command to block permissions at browser level
    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": "https://meet.google.com",
            "permissions": [],  # Empty = no permissions granted
        },
    )

    return driver


def join_meet(meet_link, participant_name=None):
    """
    Join a Google Meet with audio/video disabled and random name

    Args:
        meet_link: Full Google Meet URL
        participant_name: Optional name, random if not provided
    """
    driver = setup_driver()

    try:
        # Choose random name if not provided
        if not participant_name:
            participant_name = random.choice(RANDOM_NAMES)

        print(f"Joining meet as: {participant_name}")
        print("Audio and video are BLOCKED by browser settings")

        # Navigate to meet link
        driver.get(meet_link)
        time.sleep(4)

        # Wait for page to load
        wait = WebDriverWait(driver, 20)

        # Find and disable camera if button exists
        try:
            # Look for camera button (multiple possible states)
            camera_selectors = [
                "//button[@aria-label='Turn off camera']",
                "//button[contains(@aria-label, 'camera')]",
                "//div[@data-tooltip='Turn off camera']//button",
            ]

            for selector in camera_selectors:
                try:
                    camera_btn = driver.find_element(By.XPATH, selector)
                    if camera_btn and camera_btn.is_displayed():
                        # Check if camera is on (by aria-label or class)
                        aria_label = camera_btn.get_attribute("aria-label") or ""
                        if "off" not in aria_label.lower():
                            camera_btn.click()
                            print("Camera turned off")
                            time.sleep(0.5)
                        break
                except:
                    continue
        except Exception as e:
            print(f"Camera control: {e}")

        # Find and disable microphone if button exists
        try:
            mic_selectors = [
                "//button[@aria-label='Turn off microphone']",
                "//button[contains(@aria-label, 'microphone')]",
                "//div[@data-tooltip='Turn off microphone']//button",
            ]

            for selector in mic_selectors:
                try:
                    mic_btn = driver.find_element(By.XPATH, selector)
                    if mic_btn and mic_btn.is_displayed():
                        aria_label = mic_btn.get_attribute("aria-label") or ""
                        if "off" not in aria_label.lower():
                            mic_btn.click()
                            print("Microphone turned off")
                            time.sleep(0.5)
                        break
                except:
                    continue
        except Exception as e:
            print(f"Microphone control: {e}")

        # Enter name in the text field
        try:
            name_input_selectors = [
                "//input[@placeholder='Your name']",
                "//input[@aria-label='Your name']",
                "//input[@type='text' and contains(@placeholder, 'name')]",
            ]

            name_entered = False
            for selector in name_input_selectors:
                try:
                    name_input = driver.find_element(By.XPATH, selector)
                    if name_input and name_input.is_displayed():
                        name_input.clear()
                        name_input.send_keys(participant_name)
                        print(f"Name entered: {participant_name}")
                        name_entered = True
                        time.sleep(1)
                        break
                except:
                    continue

            if not name_entered:
                print("Name field not found - might be using Google account name")

        except Exception as e:
            print(f"Name entry: {e}")

        # Click "Ask to join" button
        try:
            join_button_selectors = [
                "//button[contains(., 'Ask to join')]",
                "//button[contains(@aria-label, 'Ask to join')]",
                "//span[text()='Ask to join']/parent::button",
                "//button[contains(., 'Join')]",
            ]

            joined = False
            for selector in join_button_selectors:
                try:
                    join_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if join_button:
                        join_button.click()
                        print("✓ Clicked 'Ask to join' button")
                        joined = True
                        break
                except:
                    continue

            if not joined:
                print("Could not find join button")
                return

            # Wait for confirmation
            time.sleep(3)
            print("Waiting for host to admit you...")

            # Keep session alive for 2 minutes
            print("Session will remain active for 120 seconds...")
            time.sleep(120)

        except Exception as e:
            print(f"Error during join process: {e}")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close browser
        print("\nClosing browser...")
        driver.quit()
        print("Done!")


# Example usage
if __name__ == "__main__":
    # Replace with your actual meet link
    MEET_LINK = "https://meet.google.com/aqy-dnyh-qqd"

    print("=" * 60)
    print("Google Meet Auto-Join Script")
    print("=" * 60)
    print("\n⚠️  IMPORTANT:")
    print("- Audio/Video permissions are BLOCKED")
    print("- Only join meetings you have permission to attend")
    print("- Misuse may violate ToS and laws\n")
    print("=" * 60 + "\n")

    # Join with random name
    join_meet(MEET_LINK)

    # Or specify a custom name:
    # join_meet(MEET_LINK, "Test User")
