## Swiggy Selenium Automation (Windows)

This project automates a Swiggy order flow using Selenium in Python, with manual OTP entry. It captures screenshots and prints key logs.

### Prerequisites
- **Python**: 3.9+
- **Chrome**: Latest
- **OS**: Windows 10/11 (run from Command Prompt)

### Setup
1. Open Command Prompt in the project folder:
```bash
cd "C:\Users\CHATT\Frugal Testing"
```
2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project folder with your details (or copy `.env.example`):
```env
SWIGGY_PHONE=9XXXXXXXXX
SWIGGY_CITY=Bengaluru
SWIGGY_DOOR=12A
SWIGGY_LANDMARK=Near Park
SWIGGY_RESTAURANT=Domino's Pizza
```
- **SWIGGY_PHONE** is required for OTP login.
- City defaults to Bengaluru if not provided.

### Run
```bash
python swiggy_automation.py
```
During login, the script pauses ~35s so you can manually enter the OTP in the browser. Keep the browser in the foreground and do not close it.

### What the script does
- Prints page title and URL
- Logs in via OTP (manual entry window)
- Sets delivery location
- Searches for restaurant (Domino’s Pizza)
- Opens first result
- Adds the second menu item and opens cart
- Increases quantity to 2
- Adds a new address (Home) and saves
- Proceeds to payment page (no payment filled)
- Screenshots saved to `screenshots/`:
  - after_add_to_cart, after_increase_quantity, after_address_saved, after_proceed_to_pay
- Console logs:
  - Page title, URL, restaurant name, food item, cart total

