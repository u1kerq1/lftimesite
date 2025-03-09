import requests
import json
import asyncio

def create_payment(merchant_id, secret, price, redirect, nickname,currency):
    r = requests.post("https://nicepay.io/public/api/payment",headers={"Content-type":"application/json"},json={
        "merchant_id":merchant_id,
        "secret": secret,
        "order_id": 1,
        "customer": nickname,
        "amount": price,
        "currency": currency,
        "success_url": redirect
    })
    if r.json()['status'] == "success":
        return r.json()['data']['link']
    else:
        raise ValueError(f"{r.json()['data']['message']}")