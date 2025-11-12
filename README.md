# 🛒 Product Price & Specification Scraper

## 📘 Overview

A **FastAPI-based web scraping tool** that fetches **product prices, ratings, reviews, and specifications** from **Google Shopping** and **BuilderMart**.
It supports searches by **item name, seller, model**, or **custom specifications**, enabling quick and automated product comparison.

---

## 🎯 Purpose

To simplify **price comparison and product data extraction** across multiple online platforms — useful for businesses, researchers, and data analysts.

---

## ⚙️ Features

* Scrapes product details from **Google Shopping** & **BuilderMart**
* Supports multiple categories: **construction, electronics, medical**
* Search by **make/model** or **specifications**
* Uses **multi-threading** for faster performance
* Randomized **User-Agent rotation**
* RESTful **API endpoints** built with FastAPI

---

## 🧩 Tech Stack

**Python**, **FastAPI**, **BeautifulSoup**, **Requests**, **ThreadPoolExecutor**, **JSON**

---

## 🚀 API Endpoints

### 1️⃣ `/scrape-make-model/{category}`

Search products using:

```json
{
  "item_name": "Cement",
  "seller": "Ultratech",
  "model": "Premium"
}
```

### 2️⃣ `/scrape-specs/{category}`

Search products using specifications:

```json
{
  "item_name": "Laptop",
  "specifications": [
    {"specification_name": "RAM", "value": "16 GB"},
    {"specification_name": "Color", "value": "Black"}
  ]
}
```

---

## ⚡ How to Run

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Visit Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧠 Achievements

* Built concurrent scrapers for multiple sites
* Designed unified API for diverse search modes
* Achieved faster scraping using threading
* Created extendable structure for new categories/sources

---

## 👩‍💻 Author

**Khyati Gupta**
Full Stack Developer | Data & Automation Enthusiast

