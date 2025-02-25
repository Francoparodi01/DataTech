import pymongo
import pandas as pd
from fpdf import FPDF
import unicodedata

def clean_text(text):
    if isinstance(text, str):
        return text.encode("latin-1", "replace").decode("latin-1")
    return text

# Conectar a MongoDB
client = pymongo.MongoClient("mongodb+srv://francoparodi2001:sMf6Wk8ircI7HHsc@informes.mr0bw.mongodb.net/")
db = client["AmazonScraper"]
collection = db["amazon_products"]

# Convertir los datos a DataFrame
df = pd.DataFrame(list(collection.find()))

# Limpiar datos de precios
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df.dropna(subset=["price"], inplace=True)

# Obtener productos más baratos y más caros
cheapest = df.sort_values(by="price").head(10)
most_expensive = df.sort_values(by="price", ascending=False).head(10)

# Estadísticas de precios
avg_price = df["price"].mean()
median_price = df["price"].median()
price_range = df["price"].max() - df["price"].min()

# Limpiar datos de ratings
df["rating"] = pd.to_numeric(df["rating"].str.extract(r'(\d+\.\d+)')[0], errors='coerce')
df.dropna(subset=["rating"], inplace=True)

# Estadísticas de ratings
avg_rating = df["rating"].mean()
rating_distribution = df["rating"].value_counts().sort_index()

# Tendencia mensual de precios
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df.dropna(subset=["timestamp"], inplace=True)
df["year_month"] = df["timestamp"].dt.to_period("M")
monthly_avg_price = df.groupby("year_month")["price"].mean()

# Crear el PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", style='B', size=16)
pdf.cell(200, 10, clean_text("Amazon Products Analysis"), ln=True, align="C")
pdf.ln(10)

# Sección de Mejores Ofertas
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Best Deals:"), ln=True)
pdf.set_font("Arial", size=12)
for index, row in cheapest.iterrows():
    pdf.multi_cell(0, 8, clean_text(f"- {row['title']}\n  Price: ${row['price']:.2f}\n  Link: {row['link']}\n"))
pdf.ln(5)

# Sección de Productos Más Caros
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Most Expensive Products:"), ln=True)
pdf.set_font("Arial", size=12)
for index, row in most_expensive.iterrows():
    pdf.multi_cell(0, 8, clean_text(f"- {row['title']}\n  Price: ${row['price']:.2f}\n  Link: {row['link']}\n"))
pdf.ln(5)

# Estadísticas de Precios
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Price Statistics:"), ln=True)
pdf.set_font("Arial", size=12)
pdf.cell(200, 8, clean_text(f"Average Price: ${avg_price:.2f}"), ln=True)
pdf.cell(200, 8, clean_text(f"Median Price: ${median_price:.2f}"), ln=True)
pdf.cell(200, 8, clean_text(f"Price Range: ${price_range:.2f}"), ln=True)
pdf.ln(5)

# Estadísticas de Ratings
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Rating Statistics:"), ln=True)
pdf.set_font("Arial", size=12)
pdf.cell(200, 8, clean_text(f"Average Rating: {avg_rating:.2f}"), ln=True)
pdf.ln(5)
pdf.cell(200, 8, clean_text("Rating Distribution:"), ln=True)
for rating, count in rating_distribution.items():
    pdf.cell(200, 8, clean_text(f"  - {rating} stars: {count} products"), ln=True)
pdf.ln(5)

# Correlación Precio-Rating
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Correlation between Price and Rating:"), ln=True)
pdf.set_font("Arial", size=12)
pdf.cell(200, 8, clean_text(f"{df['price'].corr(df['rating']):.2f}"), ln=True)
pdf.ln(5)

# Tendencia de Precios Mensual
pdf.set_font("Arial", style='B', size=14)
pdf.cell(200, 10, clean_text("Monthly Price Trend:"), ln=True)
pdf.set_font("Arial", size=12)
for period, price in monthly_avg_price.items():
    pdf.cell(200, 8, clean_text(f"{period}: ${price:.2f}"), ln=True)

# Guardar el PDF
pdf.output("Amazon_Analysis_Cleaned.pdf")
print("✅ PDF generado con mejor formato")
