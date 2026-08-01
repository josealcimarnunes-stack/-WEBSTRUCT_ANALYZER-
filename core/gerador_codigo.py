def gerar_snippet_playwright(css_selector, xpath_selector, acao="click"):
    return f"""from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("URL_AQUI")
    
    # Selecionar por CSS
    element = page.locator("{css_selector}")
    
    # Executar ação
    element.{acao}()
    
    browser.close()
"""


def gerar_snippet_selenium(css_selector, xpath_selector, acao="click"):
    return f"""from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("URL_AQUI")

# Selecionar por XPath
element = driver.find_element(By.XPATH, "{xpath_selector}")

# Executar ação
element.{acao}()

driver.quit()
"""
