from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
import time
from datetime import datetime

# Conexión a MongoDB
client = pymongo.MongoClient("mongodb+srv://francoparodi2001:sMf6Wk8ircI7HHsc@informes.mr0bw.mongodb.net/")
db = client["AmazonScraper"]
collection = db["amazon_products"]

# Configuración de Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

def extract_products():
    time.sleep(3)  # Esperar a que cargue la página
    products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div.s-result-item:not([data-component-type='sp-sponsored-result'])")
    
    if not products:
        print("⚠️ No se encontraron productos en esta página.")
        return
    
    for product in products:
        try:
            title = product.find_element(By.CSS_SELECTOR, "h2.a-size-medium.a-spacing-none.a-color-base.a-text-normal").text.strip()
        except:
            title = "N/A"
        
        try:
            price_whole = product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
            price_fraction = product.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
            price = f"{price_whole}.{price_fraction}"
        except:
            price = "N/A"
        
        try:
            brand = product.find_element(By.CSS_SELECTOR, "span.a-size-base-plus").text
        except:
            brand = "N/A"
        
        try:
            seller = product.find_element(By.CSS_SELECTOR, "span.a-size-small.a-color-secondary").text
        except:
            seller = "N/A"
        
        try:
            availability = product.find_element(By.CSS_SELECTOR, "div.a-row span.a-declarative span").text
        except:
            availability = "N/A"
        
        try:
            rating = product.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text.split()[0]
        except:
            rating = "N/A"
        
        try:
            reviews = product.find_element(By.CSS_SELECTOR, "span.a-size-base").text
        except:
            reviews = "N/A"
        
        try:
            image_url = product.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
        except:
            image_url = "N/A"
        
        try:
            link = product.find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")
        except:
            link = "N/A"
        
        product_data = {
            "title": title,
            "price": price,
            "brand": brand,
            "seller": seller,
            "availability": availability,
            "rating": rating,
            "reviews": reviews,
            "image_url": image_url,
            "link": link,
            "timestamp": datetime.utcnow()
        }
        
        if image_url == "N/A" or link == "N/A":
            continue
        
        collection.insert_one(product_data)
        print("✅ Guardado en MongoDB:", product_data)

# Función para cambiar de página
def go_to_next_page():
    try:
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next")))
        next_button.click()
        time.sleep(5)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot div.s-result-item")))
        return True
    except:
        print("⚠️ No hay más páginas disponibles.")
        return False

# Ejecutar scraping en múltiples páginas
start_url = "https://www.amazon.com/s?k=monitores+144"
driver.get(start_url)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot div.s-result-item")))

page = 1
while True:
    print(f"📄 Extrayendo datos de la página {page}...")
    extract_products()
    
    if not go_to_next_page():
        break

    page += 1

# Cerrar conexión
driver.quit()
client.close()
print("🚀 Scraping finalizado. Datos almacenados en MongoDB.")
