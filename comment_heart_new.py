from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import json
from anticaptchaofficial.imagecaptcha import *
from PIL import Image
from io import BytesIO
import os

VIDEO_SEARCH_INPUT = """div.col-sm-5.col-xs-12.p-1.container.t-chearts-menu
div.card.m-b-20.card-ortlax form
div.input-group.mb-3 input"""

VIDEO_SEARCH_BUTTON = """div.col-sm-5.col-xs-12.p-1.container.t-chearts-menu
div.card.m-b-20.card-ortlax form
div.input-group.mb-3 div.input-group-append button"""

PAGES = """div.col-sm-5.col-xs-12.p-1.container.t-chearts-menu div.card.m-b-20.card-ortlax div div.d-flex.justify-content-center.mb-3 div form"""

def fetch_driver():
    options = webdriver.ChromeOptions()
    options.add_extension('AdBlock.zip')
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_website(driver):
    driver.get('https://zefoy.com/')
    return driver

def fetch_captcha(driver):
    driver.execute_script("""
        document.querySelector("form div.justify-content-center").style.cssText = `
        justify-content: normal !important;
        position: absolute !important;
        top: 0px !important;
        z-index: 9999 !important;
        `;
    """)
    time.sleep(10) # Wait for page to load
    img = driver.get_screenshot_as_png() 
    im = Image.open(BytesIO(img)) # open image in memory with PIL library
    im = im.crop((0, 0, 290, 290)) # define crop points
    im.save('captcha.png')
    solver = imagecaptcha()
    solver.set_verbose(1)  # 1 - To display status because it's slow
    solver.set_key(os.environ['ANTI_CAPTCHA_KEY'])
    captcha_text = solver.solve_and_return_solution("captcha.png")
    
    return [captcha_text, driver]

def fill_captcha(driver, captcha):
    cap_input = driver.find_element(By.CSS_SELECTOR, ".form-control.form-control-lg.text-center.rounded-0.remove-spaces")
    cap_input.send_keys(captcha)
    
    time.sleep(10)
    driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.btn-lg.btn-block.rounded-0.submit-captcha').click()
    return driver

def click_comment_hearts(driver):
    driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.rounded-0.t-chearts-button').click()
    return driver

def find_video(driver, url):
    url_input = driver.find_element(By.CSS_SELECTOR, VIDEO_SEARCH_INPUT)
    url_input.send_keys(url)
    driver.find_element(By.CSS_SELECTOR, VIDEO_SEARCH_BUTTON).click()
    time.sleep(5)

    while len(driver.find_elements(By.CSS_SELECTOR, '.row.text-light.d-flex.justify-content-center button')) == 0:
        print('Waiting for comments to open up')
        time.sleep(30)
    
        driver.find_element(By.CSS_SELECTOR, VIDEO_SEARCH_BUTTON).click()
        time.sleep(5)

    driver.find_element(By.CSS_SELECTOR, '.row.text-light.d-flex.justify-content-center button').click()
    return driver

def find_like_comment(driver, username):
    time.sleep(10)

    if (driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]")
        and
        driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]").text == username) :
        target_div = driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]")
        parent_li = target_div.find_element(By.XPATH, "./ancestor::li")
        heart_button = parent_li.find_element(By.XPATH, ".//button")
        heart_button.click()

    else:
        pages = driver.find_elements(By.CSS_SELECTOR, PAGES)
        for page in pages:
            page.click()
            driver = page.find_element(By.XPATH, "./ancestor::body")
            if (driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]")
                and
                driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]").text == username) :
                target_div = driver.find_element(By.XPATH, f"//ul[@class='list-group']//li[contains(@class, 'list-group-item')]//div[contains(text(), '{username}')]")
                parent_li = target_div.find_element(By.XPATH, "./ancestor::li")
                heart_button = parent_li.find_element(By.XPATH, ".//button")
                heart_button.click()
                break
            else:
                print('====================\nComment not found\n========================')
        
    return driver

def main():
    data_file =  open('data_input.json', 'r')
    videos = json.load(data_file)
    
    driver = fetch_driver()
    driver = fetch_website(driver)
    try:
        captcha, driver = fetch_captcha(driver)
        driver = fill_captcha(driver, captcha)
    except:
        pass
    
    for video in videos:
        try:
            captcha, driver = fetch_captcha(driver)
            driver = fill_captcha(driver, captcha)
            print("captcha filled")
        except:
            pass
        
        # If captcha is still visible
        # This happens in case your session ends
        time.sleep(2)
        try :
            driver.find_element(By.CSS_SELECTOR, 'div.noscriptcheck div.ua-check form div.d-flex.justify-content-center div.card.mb-3.word-load')
        except:
            driver = fetch_website(driver)
            try:
                captcha, driver = fetch_captcha(driver)
                driver = fill_captcha(driver, captcha)
            except:
                pass
            
        # If comment heart navigation is not available
        while True:
            try :
                driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.rounded-0.t-chearts-button')
                break
            except:
                driver = fetch_website(driver)
                try:
                    captcha, driver = fetch_captcha(driver)
                    driver = fill_captcha(driver, captcha)
                except:
                    pass
            
        driver = click_comment_hearts(driver)
        driver = find_video(driver, video['url'])
        driver = find_like_comment(driver, video['username'])
        
        time.sleep(5)
        print("one comment have been liked")
    
    print("comments have been liked")
    data_file.close()
        
if __name__ == '__main__':
    main()