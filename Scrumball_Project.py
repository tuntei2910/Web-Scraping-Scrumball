import time
import os
import pyperclip
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
)
from time import sleep

# --- Global results dictionary ---
results = {}

# --- Output file ---
OUTPUT_FILE = f"your_path/scrape_results.xlsx" #--> need change your_path

# --- Init output file before scraping ---
if not os.path.exists(OUTPUT_FILE):
    empty_df = pd.DataFrame(columns=["url", "name", "followers", "video_count", "avg_views", "eng.rate"])
    empty_df.to_excel(OUTPUT_FILE, index=False)
    print(f"📄 Created empty output file at {OUTPUT_FILE}")


def export_results_for_key(results_dict, key_name):
    """Append scraped results for one key to Excel file safely."""
    try:
        df_new = pd.DataFrame(results_dict)
        df_new['key_word'] = key_name
        if df_new.empty:
            print(f"⚠️ No data collected for key: {key_name}, skip saving.")
            return

        # Read old file
        try:
            df_old = pd.read_excel(OUTPUT_FILE)
        except Exception:
            df_old = pd.DataFrame(columns=["url", "name", "followers", "video_count", "avg_views", "eng.rate"])

        # Concat and save
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        df_all.to_excel(OUTPUT_FILE, index=False)
        print(f"💾 Data for key '{key_name}' saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error while exporting key {key_name}: {e}")


# --- Initialize WebDriver ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Optional
#[
#options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
#options.add_experimental_option('useAutomationExtension', False)
#options.add_argument("--window-size=1366,768")
#options.add_argument("--force-device-scale-factor=1")
#options.add_argument(
#       "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
#stealth(driver,
#        languages=["en-US", "en"],
#        vendor="Google Inc.",
#        platform="Win32",
#        webgl_vendor="Intel Inc.",
#        renderer="Intel Iris OpenGL Engine",
#        fix_hairline=True,
#    )
#]

wait = WebDriverWait(driver, 20)


# ---------- Helper functions ----------
def safe_find_elements(css):
    try:
        return driver.find_elements(By.CSS_SELECTOR, css)
    except Exception:
        return []


def click_element(el):
    try:
        el.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            return False

def handle_unlock_popup(kol_el, timeout=2):
    """If the unlock popup appears, close it and click KOL again."""
    try:
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.el-dialog__wrapper.kol-dialog"))
        )
        print("⚠️ Unlock popup detected!")
        close_btn = driver.find_element(By.CSS_SELECTOR, "button.el-dialog__headerbtn")
        click_element(close_btn)
        sleep(0.5)
        click_element(kol_el)
        print("🔄 Retried clicking KOL after closing popup.")
    except TimeoutException:
        pass

# ---------- Login ----------
def login(driver, wait, email, password):
    driver.get("https://www.scrumball.cn/en/admin/explore/kol")
    try:
        login_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.el-button.btn.scrumball-button-border-default.login.el-button--default")
            )
        )
        click_element(login_btn)
        sleep(1)

        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner")))
        email_input.clear()
        email_input.send_keys(email)
        sleep(0.5)

        pwd_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
        pwd_input.clear()
        pwd_input.send_keys(password)
        sleep(0.5)

        submit = driver.find_element(
            By.CSS_SELECTOR,
            "button.el-button.scrumball-el-button.w-100.el-button--primary.is-round",
        )
        click_element(submit)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.categorys.categorys-menu")))
        print("✅ Login successful, dashboard loaded.")
    except Exception as e:
        print("⚠️ Login failed:", e)
        raise


# ---------- Select category / subcategory / key ----------
def select_category_subcategory_key(category_name, subcategory_name, key_name):
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.el-popover__reference-wrapper"))).click()
    categories = wait.until(
        EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "div.categorys.categorys-menu.scrumball-scrollbar span.categorys-menu-item")
        )
    )
    clicked = False
    for cate in categories:
        try:
            if cate.text.strip() == category_name:
                click_element(cate)
                clicked = True
                break
        except StaleElementReferenceException:
            continue
    if not clicked:
        print(f"⚠️ Category '{category_name}' not found.")
        return False

    time.sleep(0.8)

    sub_categories = wait.until(
        EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "div.types.categorys-menu.scrumball-scrollbar div.categorys-menu-item")
        )
    )
    clicked = False
    for sub_cate in sub_categories:
        try:
            if sub_cate.text.strip() == subcategory_name:
                chk = sub_cate.find_element(By.CSS_SELECTOR, "span.el-checkbox__inner")
                click_element(chk)
                clicked = True
                break
        except (StaleElementReferenceException, NoSuchElementException):
            continue
    if not clicked:
        print(f"⚠️ Subcategory '{subcategory_name}' not found.")
        return False

    time.sleep(0.8)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.reset-button"))).click()
    sleep(2)

    keys = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.options.categorys-menu.scrumball-scrollbar label.el-checkbox")
        )
    )
    clicked = False
    for item in keys:
        try:
            label = item.find_element(By.CSS_SELECTOR, "span.el-checkbox__label")
            if label.text.strip() == key_name:
                box = item.find_element(By.CSS_SELECTOR, "span.el-checkbox__inner")
                click_element(box)
                clicked = True
                break
        except (StaleElementReferenceException, NoSuchElementException):
            continue
    if not clicked:
        print(f"⚠️ Key '{key_name}' not found.")
        return False

    time.sleep(1)
    return True


# ---------- Apply region / platform / pagination ----------
def apply_region_platform_pagination(region_text="country", platform_index=2 , per_page_text="50/page"): #--> platform_index=2 is Tiktok, 0 is Youtube, 1 is Instagram
    try:
        inp = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-select__input")))
        inp.clear()
        inp.send_keys(region_text)
        sleep(0.8)

        try:
            region_li = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/ul/li[1]",
                    )
                )
            )
            click_element(region_li)
        except TimeoutException:
            suggestions = safe_find_elements("ul.el-scrollbar__view li.el-select-dropdown__item")
            if suggestions:
                click_element(suggestions[0])
        sleep(1)

        platforms = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.changePlatform.filter-left div.platform-item")
            )
        )
        if len(platforms) > platform_index:
            click_element(platforms[platform_index])
        elif platforms:
            click_element(platforms[0])
        sleep(1)

        per_page_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.el-select.el-select--mini"))
        )
        click_element(per_page_select)
        sleep(0.5)
        options = driver.find_elements(
            By.CSS_SELECTOR, "ul.el-scrollbar__view.el-select-dropdown__list li.el-select-dropdown__item span"
        )
        for opt in options:
            try:
                if opt.text.strip() == per_page_text:
                    click_element(opt)
                    break
            except StaleElementReferenceException:
                continue
        sleep(1)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cards a.kol-card")))
        backtop = driver.find_elements(
            By.CSS_SELECTOR,
            "#admin-content > div > div.page.page-main-wrapper > div > div > div.el-backtop",
        )
        if backtop:
            click_element(backtop[0])
            time.sleep(0.6)

        time.sleep(0.8)
        return True
    except Exception as e:
        print("❌ Error while applying region/platform/pagination:", e)
        return False


# ---------- Scrape one keyword ----------
def scrape_keyword(category_name, subcategory_name, key, max_pages=40):
    print(f"\n===== START: {category_name} > {subcategory_name} > {key} =====")
    global results
    results.clear()
    try:
        ok = select_category_subcategory_key(category_name, subcategory_name, key)
        if not ok:
            print(f"Skipping keyword '{key}' because selection failed.")
            return

        ok = apply_region_platform_pagination("country", 2, "50/page") # --> need change country want to target
        if not ok:
            print(f"Warning: filters not applied properly for key '{key}'. Attempting to continue...")

        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cards a.kol-card")))
        except TimeoutException:
            print("No KOL cards found after filters; skipping this key.")
            return

        for page_num in range(1, max_pages + 1):
            print(f"-- Page {page_num}/{max_pages} --")
            try:
                kols = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cards a.kol-card")))
            except TimeoutException:
                print("No KOL cards found on this page, breaking pages loop.")
                break

            if not kols:
                break

            for idx in range(len(kols)):
                try:
                    kols = driver.find_elements(By.CSS_SELECTOR, "div.cards a.kol-card")
                    kol = kols[idx]

                    try:
                        inner_click = kol.find_element(By.CSS_SELECTOR, "div.right dl dt.tiktok")
                        click_element(inner_click)
                        handle_unlock_popup(kol)
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.el-dialog__body")))
                    except Exception:
                        continue

                    try:
                        copy_btn = wait.until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    "body > div.el-dialog__wrapper > div > div.el-dialog__body > div > div.main-right > div.videoInfo > div.footer.tk-footer > button.el-button.el-button--primary",
                                )
                            )
                        )
                        click_element(copy_btn)
                        time.sleep(0.25)
                        url = pyperclip.paste().strip()
                    except Exception:
                        url = ""

                    empty_btns = driver.find_elements(By.CSS_SELECTOR, "div.main div.main-right div.empty p")
                    if not (empty_btns and empty_btns[0].text.strip().startswith("Sorry")):
                        try:
                            name = kol.find_element(By.CSS_SELECTOR, "div.left div.con span.name").text.strip()
                        except Exception:
                            name = ""

                        try:
                            nums = kol.find_elements(By.CSS_SELECTOR, "div.mid div.nums.tiktok p.kol-number")
                            followers = nums[0].text.strip() if len(nums) > 0 else ""
                            video_count = nums[1].text.strip() if len(nums) > 1 else ""
                            avg_views = nums[2].text.strip() if len(nums) > 2 else ""
                            eng_rate = nums[3].text.strip() if len(nums) > 3 else ""
                        except Exception:
                            followers = video_count = avg_views = eng_rate = ""

                        results.setdefault("url", []).append(url)
                        results.setdefault("name", []).append(name)
                        results.setdefault("followers", []).append(followers)
                        results.setdefault("video_count", []).append(video_count)
                        results.setdefault("avg_views", []).append(avg_views)
                        results.setdefault("eng.rate", []).append(eng_rate)
                        print(f" + Collected: {name} | {url}")

                    try:
                        close_btn = wait.until(
                            EC.element_to_be_clickable(
                                ("body > div.el-dialog__wrapper > div > div.el-dialog__header > button",)
                            )
                        )
                        click_element(close_btn)
                        time.sleep(0.2)
                    except Exception:
                        try:
                            driver.execute_script("document.body.click();")
                        except Exception:
                            pass

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

            if page_num < max_pages:
                try:
                    next_btn = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.page.kol-pagination.el-pagination button.btn-next"))
                    )
                    click_element(next_btn)
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cards a.kol-card")))
                    backtop = driver.find_elements(By.CSS_SELECTOR, "#admin-content > div > div.page.page-main-wrapper > div > div > div.el-backtop")
                    if backtop:
                        click_element(backtop[0])
                        time.sleep(0.5)
                    time.sleep(0.8)
                except TimeoutException:
                    break
                except Exception:
                    break

        print(f"✅ Finished scraping key: {key}")
        export_results_for_key(results, key) 
        results.clear() 
    except Exception as e:
        print(f"❌ Error while scraping {category_name}/{subcategory_name}/{key}: {e}")



# ---------- Main ----------
if __name__ == "__main__":
    try:
        login(driver, wait, "your_email", "your_password")

        keyword_list = [
            ("category1", "sub-category1", "keyword1"),
            ("category2", "sub-category2", "keyword2"),
            ("category3", "sub-category3", "keyword3")
        ]

        for idx, (cat, subcat, key) in enumerate(keyword_list, start=1):
            print(f"\n=== Processing keyword {idx}/{len(keyword_list)} ===")
            scrape_keyword(cat, subcat, key, max_pages=40)
            driver.refresh()
            time.sleep(5)

        print("🎉 All keywords processed!")
    finally:
        try:
            driver.quit()
        except Exception:
            pass