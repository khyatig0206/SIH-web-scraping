import requests
import json
from bs4 import BeautifulSoup
import random
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

            # Extract the href link
            link_tag = container.find('a', class_='xCpuod')
            href = link_tag['href'] if link_tag else None

            # Extract the website name from the href
            website = href.split("url=")[-1].split("%")[0] if href else None

            # Apply filters based on seller and model
            if model:
                if (seller and seller.lower() in product_name.lower()) and (model and model.lower() in product_name.lower()):
                    # Append the product details to the result list
                    result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Website": website
                    })
            elif seller:
                if (seller and seller.lower() in product_name.lower()):
                    # Append the product details to the result list
                    result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Website": website
                    })
            else:
                result_list.append({
                        "Product Name": product_name,
                        "Seller": manufacturer,
                        "Price": price,
                        "Website": website
                    })

        except AttributeError:
            print("Attribute error occurred while processing a product.")
            continue

    # Return the result list as a JSON object
    return json.dumps(result_list, indent=4,ensure_ascii=False)





