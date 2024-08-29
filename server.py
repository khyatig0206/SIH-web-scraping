from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from test import scrape_product_details_builder_mart
from google import scrape_product_details_google
import json

app = FastAPI()

# Define the request body structure
class ItemRequest(BaseModel):
    item_name: str
    seller: str = None
    model: str = None

@app.post("/scrape-products/construction")
def scrape_products(request: ItemRequest):
    # Scrape the product details from both sources
    result_json1 = scrape_product_details_builder_mart(request.item_name, request.seller, request.model)
    result_json2 = scrape_product_details_google(request.item_name, request.seller, request.model)

    # Convert the JSON strings to Python lists
    result_list1 = json.loads(result_json1) if result_json1 else []
    result_list2 = json.loads(result_json2) if result_json2 else []

    # Combine the two lists
    combined_results = result_list1 + result_list2

    if not combined_results:
        raise HTTPException(status_code=404, detail="No products found.")

    # Return the combined results as JSON
    return combined_results

# To run the server, use the command:
# uvicorn server:app --reload
