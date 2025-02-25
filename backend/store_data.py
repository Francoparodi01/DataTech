import pymongo
import json
import os

# Conectar a MongoDB
client = pymongo.MongoClient("mongodb+srv://francoparodi2001:sMf6Wk8ircI7HHsc@informes.mr0bw.mongodb.net/")
db = client["AmazonScraper"]
collection_amazon = db["amazon_products"]
collection_meli = db["meli_products"]

def cargar_datos_json(archivo_json):
    """Cargar datos desde un archivo JSON"""
    if os.path.exists(archivo_json):
        with open(archivo_json, encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ El archivo {archivo_json} no existe.")
        return []


def insertar_datos_mongo(coleccion, datos):
    """Insertar datos en MongoDB"""
    if datos:
        try:
            coleccion.insert_many(datos)
            print("✅ Datos almacenados en MongoDB")
        except Exception as e:
            print(f"❌ Error al insertar los datos en MongoDB: {e}")
    else:
        print("❌ No se han encontrado datos para insertar.")

# Ruta al archivo JSON de Amazon
amazon_json_products = os.path.join('spiders', 'data', 'amazon_products.json')
data_amazon = cargar_datos_json(amazon_json_products)
insertar_datos_mongo(collection_amazon, data_amazon)

# Ruta al archivo JSON de Mercado Libre
meli_json_products = os.path.join('spiders', 'data', 'meli_products.json')
data_meli = cargar_datos_json(meli_json_products)
insertar_datos_mongo(collection_meli, data_meli)
