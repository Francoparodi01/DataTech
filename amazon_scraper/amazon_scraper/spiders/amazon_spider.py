import requests
from bs4 import BeautifulSoup
import pandas as pd

class AmazonScraper:

    def __init__(self):
        # Lista de países y URLs base para Amazon (como ejemplo)
        self.urls = {
            1: 'https://www.amazon.com/s?k=monitores+144',
            2: 'https://www.amazon.co.uk/s?k=monitores+144',
            3: 'https://www.amazon.de/s?k=monitores+144',
            4: 'https://www.amazon.fr/s?k=monitores+144',
            5: 'https://www.amazon.es/s?k=monitores+144',
            # ... agrega más países si es necesario
        }

        self.exclude_keywords = ["cable", "hdmi", "usb", "vga", "adaptador", "hub", "extensor", "switch"]
        self.data = []

    def menu(self):
        menu = ("""
    Escoge el país:
    1. Estados Unidos
    2. Reino Unido
    3. Alemania
    4. Francia
    5. España
        """)
        
        valid_options = list(range(1, 6))

        while True:
            print(menu)
            opcion = int(input('Número de país (Ejemplo: 1): '))

            if opcion in valid_options:
                self.base_url = self.urls[opcion]
                break
            else:
                print("Escoge un número válido entre 1 y 5")

    def scraping(self):
        product_name = input("\nProducto: ")
        cleaned_name = product_name.replace(" ", "+").lower()
        urls = [self.base_url + "&k=" + cleaned_name]

        page_number = 50
        for i in range(0, 10000, 50):
            urls.append(f"{self.base_url}&k={cleaned_name}&page={page_number + 1}")
            page_number += 50

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }

        for i, url in enumerate(urls, start=1):
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Depuración: Imprimir la respuesta HTML
            with open(f'response_{i}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            products = soup.find_all('div', {'class': 's-main-slot'}).find_all('div', {'class': 's-result-item'})

            if not products:
                print("\nTerminó el scraping.")
                break

            print(f"\nScrapeando página número {i}. {url}")

            for product in products:
                try:
                    title = product.find('h2', class_='a-size-medium').text.strip()
                except AttributeError:
                    title = "Título no disponible"

                try:
                    price = product.find('span', class_='a-price-whole').text.replace('.', '').replace(',', '.')
                except AttributeError:
                    price = "Precio no disponible"

                try:
                    post_link = product.find("a", class_='a-link-normal')['href']
                except (AttributeError, KeyError):
                    post_link = "Enlace no disponible"

                try:
                    img_link = product.find("img", class_='s-image')['src']
                except (AttributeError, KeyError):
                    img_link = "Imagen no disponible"

                # Excluir productos con palabras clave no deseadas
                if any(f" {keyword} " in f" {title.lower()} " for keyword in self.exclude_keywords):
                    print(f"Excluido: {title}")
                    continue

                post_data = {
                    "title": title,
                    "price": price,
                    "post link": post_link,
                    "image link": img_link
                }
                self.data.append(post_data)

    def export_to_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(r"data/amazon_scraped_data.csv", sep=";", index=False)

if __name__ == "__main__":
    scraper = AmazonScraper()
    scraper.menu()
    scraper.scraping()
    scraper.export_to_csv()
