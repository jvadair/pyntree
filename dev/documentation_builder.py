"""
Set this file up in your IDE or terminal
so that it runs from the root folder of
the repository.
"""
# noinspection PyPackageRequirements
import requests

EXPORT_URL = "https://pen.jvadair.com/books/pyntree/export/pdf"

with open("documentation.pdf", "wb") as file:
    file.write(requests.get(EXPORT_URL).content)
