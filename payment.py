"""
    Author Munis Isazade Django payments
    E-Commerce gateway for merchants
    Transaction registration
    Request
    Test system
    Production system
    Parameters
    Name Description
    Merchant Key
    Amount = Transaction amount (Integer: $50.25 = 5025)
    Currency =  Transaction currency code (ISO 4217)
    Description = Transaction description (Can be used for item assigenment)
    Language = Language (az/en/ru)
"""

import os
from xml.dom.minidom import parseString

import requests
from django.conf import settings

decline_url = cancel_url = approve_url = "https://example.com/payment/approve/"

certificate_folder = os.path.join(settings.BASE_DIR, "certificate")


class BirKartPayment(object):
    URL = "https://e-commerce.kapitalbank.az:5443/Exec"

    def __init__(self, amount, description):
        self.merchant = settings.BIRKART_MERCHANT_KEY
        self.amount = amount
        self.currency = "944"
        self.description = description
        self.language = "AZ"

    def run(self):
        payment_url = self._prepare_payment_url()
        return payment_url

    def _prepare_request(self):
        url = settings.BIRKART_PAYMENT_HTTPS or self.URL
        cert = "{path}/company_prod.crt".format(path=certificate_folder)
        key = "{path}/company.key".format(path=certificate_folder)
        timeout = 30
        headers = {"Content-Type": "application/xml"}
        return {
            "url": url,
            "cert": cert,
            "key": key,
            "timeout": timeout,
            "headers": headers,
        }

    def _create_order(self):
        body = (
            "<?xml version='1.0' encoding='UTF-8'?> "
            "<TKKPG>"
            "<Request>"
            "<Operation>CreateOrder</Operation>"
            "<Language>{language}</Language>"
            "<Order> "
            "<OrderType>Purchase</OrderType>"
            "<Merchant>{merchant}</Merchant>"
            "<Amount>{amount}</Amount> "
            "<Currency>{currency}</Currency>"
            "<Description>{description}</Description>"
            "<ApproveURL>{approve_url}</ApproveURL> "
            "<CancelURL>{cancel_url}</CancelURL> "
            "<DeclineURL>{decline_url}</DeclineURL> "
            "</Order>"
            "</Request>"
            "</TKKPG>".format(
                language=self.language,
                merchant=self.merchant,
                amount=self.amount,
                currency=self.currency,
                description=self.description,
                approve_url=approve_url,
                cancel_url=cancel_url,
                decline_url=decline_url,
            )
        )

        config = self._prepare_request()
        response = requests.post(
            config["url"],
            cert=(config["cert"], config["key"]),
            timeout=config["timeout"],
            headers=config["headers"],
            data=body,
            verify=False,
        )
        print(response.text)
        return response.text

    def check_status(self, orderID, sessionID):
        body = (
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<TKKPG>"
            "<Request>"
            "<Operation>GetOrderStatus</Operation>"
            "<Language>AZ</Language>"
            "<Order>"
            "<Merchant>{merchant}</Merchant>"
            "<OrderID>{orderid}</OrderID>"
            "</Order>"
            "<SessionID>{sessionid}</SessionID>"
            "</Request>"
            "</TKKPG>".format(
                merchant=self.merchant, orderid=orderID, sessionid=sessionID
            )
        )

        config = self._prepare_request()
        response = requests.post(
            config["url"],
            cert=(config["cert"], config["key"]),
            timeout=config["timeout"],
            headers=config["headers"],
            data=body,
            verify=False,
        )
        return response.text

    def _prepare_payment_url(self):
        xmldoc = parseString(self._create_order())
        status = xmldoc.getElementsByTagName("Status")
        orderID = xmldoc.getElementsByTagName("OrderID")
        sessionID = xmldoc.getElementsByTagName("SessionID")
        url = xmldoc.getElementsByTagName("URL")
        if str(status[0].firstChild.nodeValue) == "00":
            return (
                str(url[0].firstChild.nodeValue)
                + "?ORDERID="
                + str(orderID[0].firstChild.nodeValue)
                + "&SESSIONID="
                + str(sessionID[0].firstChild.nodeValue)
                + "&expm=05&expy=17"
            )
        else:
            return False
