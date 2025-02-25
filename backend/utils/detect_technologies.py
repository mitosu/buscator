import re
from bs4 import BeautifulSoup

def detect_technologies(html):
    """
    Detecta tecnologías utilizadas en un sitio web analizando su HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    technologies = set()

    # Lenguajes y tecnologías básicas
    if soup.find("html"): technologies.add("HTML")
    if soup.find("link", rel="stylesheet"): technologies.add("CSS")
    if soup.find("script"): technologies.add("JavaScript")

    # Bibliotecas y frameworks
    for script in soup.find_all("script", src=True):
        src = script["src"].lower()
        if "jquery" in src: technologies.add("jQuery")
        if "bootstrap" in src: technologies.add("Bootstrap")
        if "react" in src: technologies.add("React")
        if "vue" in src: technologies.add("Vue.js")
        if "angular" in src: technologies.add("Angular")

    # Detectar CMS
    for meta in soup.find_all("meta"):
        if meta.get("content"):
            content = meta["content"].lower()
            if "wordpress" in content: technologies.add("WordPress")
            if "joomla" in content: technologies.add("Joomla")
            if "drupal" in content: technologies.add("Drupal")

    # URLs específicas de CMS
    if soup.find_all(href=re.compile(r"wp-content")): technologies.add("WordPress")
    if soup.find_all(href=re.compile(r"cdn.shopify.com")): technologies.add("Shopify")
    if soup.find_all(href=re.compile(r"mage-")): technologies.add("Magento")

    return list(technologies)