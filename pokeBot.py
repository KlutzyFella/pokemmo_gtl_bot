import pyautogui
import cv2
import numpy as np
from PIL import Image
import time
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Constants on 14inch 1920x1080 screen
SHINY_WIDTH = 15
SHINY_HEIGHT = 15
SHINY_START_X = 51
SHINY_START_Y = 4

PRICE_WIDTH = 101
PRICE_HEIGHT = 36
PRICE_START_X = 1004 - 529
PRICE_START_Y = 0

REFRESH_BUTTON_X = 1226
REFRESH_BUTTON_Y = 292

BUY_BUTTON_X = 1343
BUY_BUTTON_Y = 373

SHINY_BUY_THRESHOLD = 3000000

# Define region (left, top, width, height)
RELEVANT_GTL_REGION = [529, 355, 576, 380]

# Define the template image to identify shiny Pokémon
# template = cv2.imread("shiny.png")

rows = []


def take_screenshot():
    # Wait for a moment to switch to the right window
    time.sleep(3)

    # Take screenshot of the region
    screenshot = pyautogui.screenshot(region=RELEVANT_GTL_REGION)

    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Save image
    cv2.imwrite("gtl_screenshot.png", img_cv)

    # Get the dimensions of the screenshot
    # img_height, img_width = img_cv.shape[:2]

    return img_cv


def click_refresh():
    # Click the refresh button
    pyautogui.click(REFRESH_BUTTON_X, REFRESH_BUTTON_Y)
    print("Clicked refresh button")
    # time.sleep(1)


def read_screenshot(image):
    # reading through all the 10 rows of the GTL
    for i in range(10):
        # Calculate the coordinates for the shiny Pokémon and price
        shiny_y = SHINY_START_Y + i * 38
        shiny_x = SHINY_START_X
        price_y = PRICE_START_Y + i * 39
        price_x = PRICE_START_X
        buy_button_y = BUY_BUTTON_Y + i * 38

        # Ensure we're not out of bounds
        # if shiny_y + SHINY_HEIGHT > img_height or shiny_x + SHINY_WIDTH > img_width:
        #     print(f"Skipping row {i}: crop exceeds image bounds.")
        #     continue

        # Crop the shiny Pokémon area
        shiny_crop = image[
            shiny_y : shiny_y + SHINY_HEIGHT, shiny_x : shiny_x + SHINY_WIDTH
        ]

        # Write the cropped image to a file
        cv2.imwrite(f"shiny_crop_{i}.png", shiny_crop)

        # Convert the cropped image to grayscale and apply thresholding for OCR
        shiny_crop_gray = cv2.cvtColor(shiny_crop, cv2.COLOR_BGR2GRAY)
        shiny_crop_gray = cv2.threshold(shiny_crop_gray, 120, 255, cv2.THRESH_BINARY)[1]
        shiny_text = pytesseract.image_to_string(shiny_crop_gray, config="--psm 6")

        if shiny_text.strip() == "":
            print(f"Skipping row {i}: no shiny Pokémon detected.")
            continue

        # Crop the price area
        price_crop = image[
            price_y : price_y + PRICE_HEIGHT, price_x : price_x + PRICE_WIDTH
        ]

        # Write the cropped image to a file
        cv2.imwrite(f"price_crop_{i}.png", price_crop)

        # Convert the cropped image to grayscale and apply thresholding for OCR
        price_crop_gray = cv2.cvtColor(price_crop, cv2.COLOR_BGR2GRAY)
        price_crop_gray = cv2.threshold(price_crop_gray, 120, 255, cv2.THRESH_BINARY)[1]
        price_text = pytesseract.image_to_string(price_crop_gray, config="--psm 6")
        price_int = int(price_text.replace("$", "").replace(",", ""))

        # Append the shiny Pokémon name and price to the list
        rows.append((shiny_text.strip(), price_int))

        if shiny_text.strip() != "" and price_int < SHINY_BUY_THRESHOLD:
            # Click the buy button
            pyautogui.click(BUY_BUTTON_X, buy_button_y)
            pyautogui.press("e")
            print(f"Bought shiny Pokémon: {shiny_text.strip()} for {price_int}")
            # time.sleep(1)
            break

        # pyautogui.click(BUY_BUTTON_X, buy_button_y)
        # print(f"Bought shiny Pokémon: {shiny_text.strip()} for {price_int}")

    print(rows)


# Main loop
def main():
    while True:
        # Take a screenshot
        screenshot = take_screenshot()

        # Click the refresh button
        click_refresh()

        # Read the screenshot
        read_screenshot(screenshot)


if __name__ == "__main__":
    main()
