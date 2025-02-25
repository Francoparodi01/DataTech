from flask import Flask, render_template, jsonify
import pymongo
import pandas as pd

app = Flask(__name__)

# Conexión a MongoDB
client = pymongo.MongoClient("mongodb+srv://francoparodi2001:sMf6Wk8ircI7HHsc@informes.mr0bw.mongodb.net/")
db = client["AmazonScraper"]
collection = db["amazon_products"]
@app.route("/")
def index():
    products = list(collection.find({}, {"_id": 0}))
    return render_template("index.html", products=products)

@app.route("/dashboard")
def dashboard():
    products = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(products)

    # Convertir precio a número y eliminar NaN
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Calcular métricas clave
    avg_price = df["price"].mean()
    max_price = df["price"].max()
    min_price = df["price"].min()

    # Obtener los top 5 más caros y más baratos
    top_expensive = df.nlargest(5, "price")[["title", "price"]].to_dict(orient="records")
    top_cheap = df.nsmallest(5, "price")[["title", "price"]].to_dict(orient="records")

    # Distribución de precios por rango
    price_bins = [0, 50, 100, 150, 200, df["price"].max()]
    price_labels = ["0-50", "51-100", "101-150", "151-200", "201+"]
    price_distribution = df["price"].value_counts(bins=price_bins, sort=False).tolist()

    return render_template("dashboard.html",
                           avg_price=avg_price,
                           max_price=max_price,
                           min_price=min_price,
                           top_expensive=top_expensive,
                           top_cheap=top_cheap,
                           price_distribution=price_distribution)

if __name__ == "__main__":
    app.run(debug=True)