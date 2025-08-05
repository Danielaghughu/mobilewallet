import requests
import json
from django.conf import settings
from django.http import JsonResponse, Http404

def initiate(email: str, amount: int):
    try:
        if not email:
            return JsonResponse({"error": "Email is missing or invalid"}, status=400)
        if not amount:
            return JsonResponse({"error": "Amount is required"}, status=400)

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": int(amount) * 100,  
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            res_data = response.json()
            return JsonResponse({
                "authorization_url": res_data["data"]["authorization_url"],
                "reference": res_data["data"]["reference"]
            })
        return JsonResponse({"error": response.json()}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


def verify(reference: str):
    try:
        if not reference:
            return JsonResponse({"error": "Reference is missing or invalid"}, status=400)   
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",  
            "Content-Type": "application/json" 
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            res_data = response.json()
            if res_data["data"]["status"] == "success": 
                return JsonResponse("success")
            return JsonResponse("failed")
        return JsonResponse({"error": response.json()}, status=response.status_code)        
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)