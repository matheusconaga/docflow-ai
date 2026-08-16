import os
import hmac
import hashlib
import json
import httpx
from typing import Optional, Dict, Any

ABACATEPAY_API_KEY = os.getenv("ABACATEPAY_API_KEY", "")
ABACATEPAY_BASE_URL = "https://api.abacatepay.com/v2"

# In-memory cache for product IDs to avoid fetching every time
_PRODUCT_CACHE = {}

def get_headers():
    return {
        "Authorization": f"Bearer {ABACATEPAY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def get_or_create_product(plan_type: str) -> str:
    """Returns the AbacatePay Product ID for a given plan (essencial or pro)."""
    if plan_type in _PRODUCT_CACHE:
        return _PRODUCT_CACHE[plan_type]

    external_id = f"educassist_plan_{plan_type}"
    
    async with httpx.AsyncClient() as client:
        # First, try to list products and find ours
        resp = await client.get(f"{ABACATEPAY_BASE_URL}/products/list", headers=get_headers())
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for prod in data:
                if prod.get("externalId") == external_id:
                    _PRODUCT_CACHE[plan_type] = prod["id"]
                    return prod["id"]
        
        # If not found, create it
        price = 1490 if plan_type == "essencial" else 3990
        name = "Plano Essencial" if plan_type == "essencial" else "Plano Pro"
        
        payload = {
            "externalId": external_id,
            "name": name,
            "price": price,
            "currency": "BRL",
            "description": f"Assinatura do {name} do EducAssist"
        }
        
        create_resp = await client.post(f"{ABACATEPAY_BASE_URL}/products/create", json=payload, headers=get_headers())
        create_resp.raise_for_status()
        
        prod_data = create_resp.json().get("data", {})
        prod_id = prod_data.get("id")
        
        _PRODUCT_CACHE[plan_type] = prod_id
        return prod_id

async def create_checkout(plan_type: str, user_id: str, email: str, name: str) -> str:
    """Creates an AbacatePay checkout and returns the URL."""
    product_id = await get_or_create_product(plan_type)
    
    # Optional: ensure customer exists
    customer_payload = {
        "email": email,
        "name": name
    }
    
    async with httpx.AsyncClient() as client:
        # Create/Get Customer
        cust_resp = await client.post(f"{ABACATEPAY_BASE_URL}/customers/create", json=customer_payload, headers=get_headers())
        customer_id = None
        if cust_resp.status_code == 200:
            customer_id = cust_resp.json().get("data", {}).get("id")

        checkout_payload = {
            "items": [{"id": product_id, "quantity": 1}],
            "metadata": {"user_id": user_id, "plan_type": plan_type},
            "returnUrl": "http://localhost:5173/professor/planos?status=success",
            "completionUrl": "http://localhost:5173/professor/planos?status=success"
        }
        if customer_id:
            checkout_payload["customerId"] = customer_id
            
        checkout_resp = await client.post(f"{ABACATEPAY_BASE_URL}/checkouts/create", json=checkout_payload, headers=get_headers())
        checkout_resp.raise_for_status()
        
        checkout_data = checkout_resp.json().get("data", {})
        return checkout_data.get("url")

def verify_abacatepay_webhook(raw_body: bytes, signature_header: str, secret: str) -> bool:
    """Verifies HMAC signature of AbacatePay webhooks. Not strict due to generic header unknowns for MVP."""
    if not secret or not signature_header:
        return True # Dev mode fallback if not provided
        
    expected_mac = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_mac, signature_header)
