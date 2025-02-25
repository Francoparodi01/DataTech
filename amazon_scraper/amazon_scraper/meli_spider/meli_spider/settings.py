# Scrapy settings for meli_spider project

BOT_NAME = "meli_spider"

SPIDER_MODULES = ["meli_spider.spiders"]
NEWSPIDER_MODULE = "meli_spider.spiders"

# Habilitar scrapy-fake-useragent
FAKEUSERAGENT_PROVIDERS = [
    "scrapy_fake_useragent.providers.FakeUserAgentProvider",
    "scrapy_fake_useragent.providers.FakerProvider",
    "scrapy_fake_useragent.providers.FixedUserAgentProvider",
]

USER_AGENT = None  # Dejar que scrapy-fake-useragent maneje esto automáticamente

# Configuraciones adicionales para evitar bloqueos
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 2  # Ajustar según sea necesario
RETRY_TIMES = 5

ROBOTSTXT_OBEY = False

# Permitir el acceso a mercadolibre.com.ar
OFFSITE_DOMAINS = ['mercadolibre.com.ar']
OFFSITE_ENABLED = False


# Otros ajustes predeterminados:
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
