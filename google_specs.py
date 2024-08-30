from datetime import datetime
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


# Example usage
# specifications = [
#     {"specification_name": "color", "value": "Black"},
#     {"specification_name": "RAM", "value": "16 GB"},

# ]

# print(scrape_product_details_google_specs("Laptop", specifications))


