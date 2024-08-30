from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from test import scrape_product_details_builder_mart
from google import scrape_product_details_google
import json

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the request body structure
class ItemRequest_form1(BaseModel):
    item_name: str
    seller: str = None
    model: str = None

category_functions_form1 = {
    "construction": [scrape_product_details_builder_mart, scrape_product_details_google],
    "medical": [scrape_product_details_google],
    "electronics": [scrape_product_details_google],
}

@app.post("/scrape-make-model/{category}")
def scrape_products(category: str, request: ItemRequest_form1):
    # Scrape the product details from both sources
    if category not in category_functions_form1:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")

    scraping_functions = category_functions_form1[category]

    combined_results = []

    # Execute the scraping functions and combine results
    for func in scraping_functions:
        result_json = func(request.item_name, request.seller, request.model)
        result_list = json.loads(result_json) if result_json else []
        combined_results.extend(result_list)

    if not combined_results:
        raise HTTPException(status_code=404, detail="No products found.")

    # Return the combined results as JSON
    return combined_results

# To run the server, use the command:
# uvicorn server:app --reload
