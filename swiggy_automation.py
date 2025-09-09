import os
import sys
import time
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

try:
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
	pass


def create_driver() -> webdriver.Chrome:
	chrome_options = ChromeOptions()
	chrome_options.add_argument("--start-maximized")
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_argument("--disable-logging")
	chrome_options.add_argument("--log-level=3")
	chrome_options.add_experimental_option("excludeSwitches", ["enable-automation","enable-logging"])
	chrome_options.add_experimental_option('useAutomationExtension', False)
	service = ChromeService(ChromeDriverManager().install())
	return webdriver.Chrome(service=service, options=chrome_options)


def wait_for_element(driver: webdriver.Chrome, by: By, value: str, timeout: int = 20):
	return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


def wait_for_clickable(driver: webdriver.Chrome, by: By, value: str, timeout: int = 20):
	return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))


def safe_click(driver: webdriver.Chrome, by: By, value: str, timeout: int = 20):
	el = wait_for_clickable(driver, by, value, timeout)
	try:
		el.click()
	except ElementClickInterceptedException:
		driver.execute_script("arguments[0].click();", el)
	return el


def take_screenshot(driver: webdriver.Chrome, name: str):
	screens_dir = os.path.join(os.getcwd(), "screenshots")
	os.makedirs(screens_dir, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	path = os.path.join(screens_dir, f"{timestamp}_{name}.png")
	driver.save_screenshot(path)
	print(f"[screenshot] {path}")


def log(msg: str):
	print(f"[log] {msg}")


def ensure_env(var_name: str) -> str:
	val = os.getenv(var_name, "").strip()
	if not val:
		print(f"Environment variable {var_name} is required. Create a .env file with {var_name}=...")
		sys.exit(1)
	return val


def main():
	phone_number = ensure_env("SWIGGY_PHONE")
	city_name = os.getenv("SWIGGY_CITY", "Bengaluru").strip() or "Bengaluru"
	restaurant_query = os.getenv("SWIGGY_RESTAURANT", "Domino's Pizza")

	driver = create_driver()
	wait = WebDriverWait(driver, 25)
	try:
		
		driver.get("https://www.swiggy.com/")
		try:
			wait.until(lambda d: d.title and len(d.title) > 0)
		except TimeoutException:
			pass

		print(f"Page Title: {driver.title}")
		print(f"Current URL: {driver.current_url}")

		
		try:
			login_btn = wait_for_clickable(driver, By.XPATH, "//span[contains(text(),'Sign In') or contains(text(),'Login')]")
			login_btn.click()
		except Exception:
			try:
				safe_click(driver, By.XPATH, "//a[contains(@href,'login') or contains(text(),'Sign In') or contains(text(),'Login')]")
			except Exception:
				pass

		
		try:
			phone_input = wait_for_element(driver, By.NAME, "mobile")
		except TimeoutException:
			phone_input = wait_for_element(driver, By.XPATH, "//input[@type='tel' or @name='mobile']")
		phone_input.clear()
		phone_input.send_keys(phone_number)

		
		try:
			continue_btn = wait_for_clickable(driver, By.XPATH, "//span[contains(text(),'CONTINUE')]/ancestor::button | //button[.\//span[contains(text(),'Continue')]] | //button[contains(.,'Continue')]")
			continue_btn.click()
		except Exception:
			phone_input.send_keys(Keys.ENTER)

		log("Waiting 35 seconds for manual OTP entry...")
		time.sleep(35)

		try:
			wait.until_not(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Sign In') or contains(text(),'Login')]")))
		except TimeoutException:
			log("Login not confirmed, proceeding anyway. If blocked, rerun after successful OTP.")

		
		try:
			location_input = wait_for_clickable(driver, By.XPATH, "//input[contains(@placeholder,'delivery location') or contains(@aria-label,'location') or contains(@placeholder,'Enter your delivery location')]")
		except TimeoutException:
			safe_click(driver, By.XPATH, "//div[contains(.,'Enter your delivery location') or contains(.,'delivery location')]")
			location_input = wait_for_clickable(driver, By.XPATH, "//input[@type='text' and (contains(@placeholder,'location') or contains(@aria-label,'location'))]")

		location_input.clear()
		location_input.send_keys(city_name)
		try:
			suggestion = wait_for_clickable(driver, By.XPATH, f"//div[contains(@role,'option') or contains(@class,'_3lmRa') or contains(@class,'_2dS-v')][.//span[contains(.,'{city_name.split()[0]}')] or contains(.,'{city_name.split()[0]}')]")
			suggestion.click()
		except TimeoutException:
			location_input.send_keys(Keys.ENTER)
			time.sleep(2)

		
		try:
			search_entry = wait_for_clickable(driver, By.XPATH, "//input[contains(@placeholder,'Search') and @type='text']")
			exists_inline = True
		except TimeoutException:
			exists_inline = False

		if not exists_inline:
			try:
				safe_click(driver, By.XPATH, "//span[contains(text(),'Search')]/ancestor::button | //button[contains(.,'Search')] | //div[@role='button' and contains(.,'Search')] | //img[contains(@alt,'search')]/ancestor::button")
				search_entry = wait_for_clickable(driver, By.XPATH, "//input[contains(@placeholder,'Search') and @type='text']")
			except Exception:
				driver.find_element(By.TAG_NAME, "body").send_keys("/")
				search_entry = wait_for_clickable(driver, By.XPATH, "//input[contains(@placeholder,'Search') and @type='text']")

		search_entry.clear()
		search_entry.send_keys(restaurant_query)
		search_entry.send_keys(Keys.ENTER)

		restaurant_name_text = None
		try:
			first_result = wait_for_clickable(driver, By.XPATH, "(//a[contains(@href,'restaurant') or contains(@href,'restaurants')][.//h3 or .//h4 or .//div])[1]")
			try:
				name_el = first_result.find_element(By.XPATH, ".//h3 | .//h4 | .//div[contains(@class,'restaurant-name')]")
				restaurant_name_text = name_el.text.strip()
			except NoSuchElementException:
				pass
			first_result.click()
		except TimeoutException:
			first_result = wait_for_clickable(driver, By.XPATH, "(//a[contains(@href,'restaurant')])[1]")
			first_result.click()

		
		try:
			wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'_1RPOp') or contains(@class,'_2wg_t') or contains(@data-testid,'menu-item')]")))
		except TimeoutException:
			pass

		add_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(),'Add')] or contains(.,'Add')]")
		if len(add_buttons) < 2:
			add_buttons = driver.find_elements(By.XPATH, "//div[contains(@class,'styles_itemAddButton') or contains(@class,'_1RPOp')]//button")

		if len(add_buttons) < 2:
			raise RuntimeError("Could not find at least two 'Add' buttons in the menu.")

		second_add = add_buttons[1]
		try:
			item_name_el = second_add.find_element(By.XPATH, "ancestor::div[contains(@class,'styles_item') or contains(@data-testid,'menu-item')][1]//h3 | ancestor::div[contains(@class,'styles_item') or contains(@data-testid,'menu-item')][1]//h4 | ancestor::div[contains(@class,'styles_item') or contains(@data-testid,'menu-item')][1]//*[contains(@class,'name')]")
			item_name_text = item_name_el.text.strip()
		except NoSuchElementException:
			item_name_text = "Unknown Item"

		second_add.click()
		time.sleep(2)

		try:
			custom_add = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Add Item') or contains(.,'Add to Cart') or .//span[contains(.,'Add')]]", timeout=8)
			custom_add.click()
			time.sleep(1)
		except Exception:
			pass

		try:
			view_cart_btn = wait_for_clickable(driver, By.XPATH, "//a[contains(@href,'cart') and (contains(.,'View Cart') or .//span[contains(.,'View Cart')]) ] | //button[contains(.,'View Cart')]")
			view_cart_btn.click()
		except TimeoutException:
			safe_click(driver, By.XPATH, "//a[contains(@href,'cart')] | //div[@role='button' and contains(.,'Cart')]")

		take_screenshot(driver, "after_add_to_cart")

		
		try:
			plus_btn = wait_for_clickable(driver, By.XPATH, "//button[contains(@aria-label,'increase') or contains(.,'+') or contains(@data-testid,'quantity-increase')]")
			plus_btn.click()
			time.sleep(1)
		except TimeoutException:
			plus_btn = wait_for_clickable(driver, By.XPATH, "(//button[contains(.,'+')])[1]")
			plus_btn.click()

		cart_total_text = ""
		try:
			cart_total_el = wait_for_element(driver, By.XPATH, "//*[contains(.,'To Pay') or contains(.,'Total')]/following::div[1] | //*[contains(@class,'total') and contains(.,'₹')] | //div[contains(@data-testid,'total-amount')]")
			cart_total_text = cart_total_el.text.strip()
		except Exception:
			pass

		take_screenshot(driver, "after_increase_quantity")

		
		try:
			add_address_btn = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Add new address') or contains(.,'Add New Address') or contains(.,'Add Address')]")
			add_address_btn.click()
		except TimeoutException:
			pass

		try:
			door_input = wait_for_element(driver, By.XPATH, "//input[contains(@placeholder,'Door') or contains(@placeholder,'Flat') or contains(@name,'door')]")
			door_input.clear()
			door_input.send_keys(os.getenv("SWIGGY_DOOR", "12A"))
		except TimeoutException:
			pass

		try:
			landmark_input = wait_for_element(driver, By.XPATH, "//input[contains(@placeholder,'Landmark') or contains(@name,'landmark')]")
			landmark_input.clear()
			landmark_input.send_keys(os.getenv("SWIGGY_LANDMARK", "Near Park"))
		except TimeoutException:
			pass

		try:
			home_tag = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Home')] | //span[contains(.,'Home')]/ancestor::button")
			home_tag.click()
		except TimeoutException:
			pass

		try:
			save_btn = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Save Address & Proceed') or contains(.,'Save and Proceed') or contains(.,'Save')]")
			save_btn.click()
		except TimeoutException:
			try:
				safe_click(driver, By.XPATH, "(//button[not(@disabled) and (contains(.,'Proceed') or contains(.,'Save'))])[1]")
			except Exception:
				pass

		take_screenshot(driver, "after_address_saved")

		
		try:
			proceed_to_pay = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Proceed to Pay') or contains(.,'Proceed to pay') or contains(.,'Proceed to payment')]")
			proceed_to_pay.click()
		except TimeoutException:
			try:
				proceed_to_pay = wait_for_clickable(driver, By.XPATH, "//button[contains(.,'Checkout') or contains(.,'Pay')]")
				proceed_to_pay.click()
			except TimeoutException:
				pass

		try:
			wait.until(lambda d: any(k in d.current_url.lower() for k in ["checkout", "payment", "pay"]))
		except TimeoutException:
			log("Payment page not confirmed by URL; it may be gated by address validation.")

		take_screenshot(driver, "after_proceed_to_pay")

		
		if restaurant_name_text:
			print(f"Restaurant Selected: {restaurant_name_text}")
		else:
			print("Restaurant Selected: Unknown")
		print(f"Food Item Selected: {item_name_text}")
		print(f"Cart Total: {cart_total_text}")

		log("Flow complete. Close the browser when done reviewing.")

	except Exception as e:
		print("Error during automation:")
		traceback.print_exc()
		print(f"\nBrowser will stay open for 30 seconds for you to review what happened...")
		time.sleep(30)
	finally:
		
		print("\nScript finished. Browser will stay open - close it manually when done reviewing.")
		input("Press Enter to close browser and exit...")
		driver.quit()


if __name__ == "__main__":
	main()
