from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import List, Dict
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def scrape_page(page_number, seller, model, base_url, result_list, lock):
    url = f"{base_url}&p={page_number}"
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Scrape products from the page
    products = soup.find_all('div', class_='item col-md-3 col-sm-4 col-xs-6')
    
    # Process the products and append to the result_list
    for product in products:
        href = product.find('a')['href']
        product_name = product.find('div', class_='product-name compareproductname').text.strip()
        product_seller = product.find('div', class_='product-seller').text.strip().replace('by', '').strip()
        price = product.find('span', class_='price', id='product-price-_listing_grid').text.strip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # If model is defined, check both seller and model
        if model:
            if (seller and seller.lower() in product_seller.lower()) and (model.lower() in product_name.lower()):
                with lock:
                    if not any(p['Product Name'] == product_name and p['Seller'] == product_seller for p in result_list):
                        if len(result_list) < 3:
                            result_list.append({
                                "Product Name": product_name,
                                "Seller": product_seller,
                                "Price": price,
                                "Rating":"No rating",
                                "Reviews":"No Reviews",
                                "specifications":"No specification",
                                "Website": href,
                                "last_updated":current_time
                            })
                        if len(result_list) >= 3:
                            return
        # If model is not defined, check only the seller
        elif seller:
            if seller.lower() in product_seller.lower():
                with lock:
                    if not any(p['Product Name'] == product_name and p['Seller'] == product_seller for p in result_list):
                        if len(result_list) < 3:
                            result_list.append({
                                "Product Name": product_name,
                                "Seller": product_seller,
                                "Price": price,
                                "Rating":"No rating",
                                "Reviews":"No Reviews",
                                "specifications":"No specification",
                                "Website": href,
                                "last_updated":current_time
                            })
                        if len(result_list) >= 3:
                            return
                        
        else:
            with lock:
                # Check if the product is already in the result_list
                if not any(p['Product Name'] == product_name and p['Seller'] == product_seller for p in result_list):
                    if len(result_list) < 3:
                        result_list.append({
                                "Product Name": product_name,
                                "Seller": product_seller,
                                "Price": price,
                                "Rating":"No rating",
                                "Reviews":"No Reviews",
                                "specifications":"No specification",
                                "Website": href,
                                "last_updated":current_time
                        })
                    if len(result_list) >= 3:
                        return


    # If there's no 'next' button, stop further processing
    next_button = soup.find('a', class_='next i-next')
    if not next_button:
        return

def scrape_product_details_builder_mart(item_name, seller=None, model=None):
    search_query = item_name.replace(' ', '+')
    if seller:
        search_query += f"+{seller.replace(' ', '+')}"
    if model:
        search_query += f"+{model.replace(' ', '+')}"

    base_url = f"https://www.buildersmart.in/catalogsearch/result/?q={search_query}"
    result_list = []
    lock = threading.Lock()

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for page_number in range(1, 21):
            futures.append(executor.submit(scrape_page, page_number, seller, model, base_url, result_list, lock))
            
            with lock:
                if len(result_list) >= 3:
                    break

        # Wait for all futures to complete or early exit if 10 results found
        for future in as_completed(futures):
            with lock:
                if len(result_list) >= 3:
                    break  # Exit as soon as 10 results are found

    # end_time = time.perf_counter()
    # processing_time = end_time - start_time
    # print(f"Processing Time: {processing_time:.2f} seconds")

    return json.dumps(result_list, indent=4, ensure_ascii=False)


def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    ]
    return random.choice(user_agents)


def scrape_product_details_google(item_name, seller=None, model=None):
    
    
    headers = {
        "User-Agent": get_random_user_agent(),
    }
    
    search_query = item_name.replace(' ', '+')
    if seller:
        search_query += f"+{seller.replace(' ', '+')}"
    if model:
        search_query += f"+{model.replace(' ', '+')}"

    response = requests.get(f"https://www.google.co.uk/search?q={search_query}&tbm=shop", headers=headers)


    if response.status_code != 200:
        print(f"Failed to retrieve page with status code: {response.status_code}")
        return None

   
    soup = BeautifulSoup(response.content, 'html.parser')
    
    
    product_containers = soup.find_all('div', class_='sh-dgr__content')
    
    if not product_containers:
        print("No product containers found. The HTML structure may have changed.")
        return None


    result_list = []

    for container in product_containers:
        if len(result_list) >= 10:  
            break

        try:
            # Extract product name
            product_name = container.find('h3', class_='tAxDx')
            if product_name:
                product_name = product_name.text.strip()
            else:
                continue

            # Extract manufacturer or seller
            manufacturer = container.find('div', class_='aULzUe')
            if manufacturer:
                manufacturer = manufacturer.text.strip()
            else:
                continue

            # Extract product price
            price = container.find('span', class_='a8Pemb OFFNJ')
            if price:
                price = price.text.strip()
            else:
                continue
            rating = container.find('span', class_='Rsc7Yb').text if container.find('span', class_='Rsc7Yb') else 'No rating'
            div_rev = container.find('div', class_='qSSQfd uqAnbd') 
            if div_rev:
                text = div_rev.find_next_sibling(text=True)
                reviews = text.strip()
            else:
                reviews = "No Reviews"
            specifications = container.find('div', class_='F7Kwhf').text if container.find('div', class_='F7Kwhf') else 'No specifications'
            
            # div_img = soup.find('div', class_='ArOc1c')
            # if div_img:
            #     img_src = div_img.find('img')['src']
            # else:
            #     img_src = "No Image"
                    
            link_tag = container.find('a', class_='shntl')
            href = link_tag['href'] if link_tag else None

            # Extract the website name from the href
            website = href.split("url=")[-1].split("%")[0] if href else None
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Apply filters based on seller and model
            if model:
                if (seller and seller.lower() in product_name.lower()) and (model and model.lower() in product_name.lower()):
                    # Append the product details to the result list
                    result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Rating":rating,
                        "Reviews":reviews,
                        "specifications":specifications,
                        "Website": website,
                        "last_updated":current_time
                    })
            elif seller:
                if (seller and seller.lower() in product_name.lower()):
                    # Append the product details to the result list
                    result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Rating":rating,
                        "Reviews":reviews,
                        "specifications":specifications,
                        "Website": website,
                        "last_updated":current_time
                    })
            else:
                result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Rating":rating,
                        "Reviews":reviews,
                        "specifications":specifications,
                        "Website": website,
                        "last_updated":current_time
                    })

        except Exception as e:
            print(e)
            continue

    # Return the result list as a JSON object
    return json.dumps(result_list, indent=4,ensure_ascii=False)


def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    ]
    return random.choice(user_agents)



def scrape_product_details_google_specs(item_name ,specifications):

    headers = {
        "User-Agent": get_random_user_agent(),
    }

    search_query = item_name.replace(' ', '+')
    if specifications:
        for spec in specifications:
            spec_name = spec["specification_name"]
            spec_value = spec["value"]
            search_query += f"+{spec_name.replace(' ', '+')}"
            search_query += f"+{spec_value.replace(' ', '+')}"

    response = requests.get(f"https://www.google.co.uk/search?q={search_query}&tbm=shop", headers=headers)


    if response.status_code != 200:
        print(f"Failed to retrieve page with status code: {response.status_code}")
        return None

   
    soup = BeautifulSoup(response.content, 'html.parser')
    
    
    product_containers = soup.find_all('div', class_='sh-dgr__content')
    if not product_containers:
        print("No product containers found. The HTML structure may have changed.")
        return None


    result_list = []

    for container in product_containers:
        if len(result_list) >= 10:  
            break

        try:
            # Extract product name
            product_name = container.find('h3', class_='tAxDx')
            if product_name:
                product_name = product_name.text.strip()
            else:
                continue

            # Extract manufacturer or seller
            manufacturer = container.find('div', class_='aULzUe')
            if manufacturer:
                manufacturer = manufacturer.text.strip()
            else:
                continue

            # Extract product price
            price = container.find('span', class_='a8Pemb OFFNJ')
            if price:
                price = price.text.strip()
            else:
                continue
            rating = container.find('span', class_='Rsc7Yb').text if container.find('span', class_='Rsc7Yb') else 'No rating'
            
            div_rev = container.find('div', class_='qSSQfd uqAnbd') 
            if div_rev:
                text = div_rev.find_next_sibling(string=True)
                reviews = text.strip()
            else:
                reviews = "No Reviews"
            specifi = container.find('div', class_='F7Kwhf').text if container.find('div', class_='F7Kwhf') else 'No specifications'
                    
            link_tag = container.find('a', class_='shntl')
            href = link_tag['href'] if link_tag else None

            # Extract the website name from the href
            website = href.split("url=")[-1].split("%")[0] if href else None
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            if specifications:
                specs_match = all(
                    spec["value"].lower() in product_name.lower() or spec["value"].lower() in specifi.lower()
                    for spec in specifications
                )
            else:
                specs_match = True  # No specifications to match

            if specs_match:
                result_list.append({
                    "Product Name": product_name,
                    "Seller": manufacturer,
                    "Price": price,
                    "Rating": rating,
                    "Reviews": reviews,
                    "Specifications": specifi,
                    "Website": website,
                    "Last Updated": current_time
                })

        except Exception as e:
            print(e)
            continue


    return json.dumps(result_list, indent=4,ensure_ascii=False)

# Define the request body structure
class ItemRequest_form1(BaseModel):
    item_name: str
    seller: str = None
    model: str = None

class ItemRequest_form2(BaseModel):
    item_name: str
    specifications: List[Dict[str, str]] = None

category_functions_form1 = {
    "construction": [scrape_product_details_builder_mart, scrape_product_details_google],
    "medical": [scrape_product_details_google],
    "electronics": [scrape_product_details_google],
}

category_functions_form2 = {
    "construction": [scrape_product_details_google_specs],
    "medical": [scrape_product_details_google_specs],
    "electronics": [scrape_product_details_google_specs],
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



@app.post("/scrape-specs/{category}")
def scrape_products_specs(category: str, request: ItemRequest_form2):
    # Scrape the product details based on specifications
    if category not in category_functions_form2:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")

    scraping_functions = category_functions_form2[category]

    combined_results = []

    # Execute the scraping functions and combine results
    for func in scraping_functions:
        # Unpack specifications list to pass it as individual arguments
        result_json = func(request.item_name, request.specifications)
        result_list = json.loads(result_json) if result_json else []
        combined_results.extend(result_list)

    if not combined_results:
        raise HTTPException(status_code=404, detail="No products found.")

    # Return the combined results as JSON
    return combined_results







# To run the server, use the command:
# uvicorn server:app --reload
