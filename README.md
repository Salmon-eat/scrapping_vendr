# Vendr Scraper (Multi-threaded)

A high-performance, multi-threaded web scraper designed to collect software product data from the Vendr platform. This project implements a producer-consumer architecture using task queues, a worker pool, and automated data persistence to PostgreSQL via SQLAlchemy.

## Features

- **Multi-threading**: Utilizes 5 parallel worker threads for efficient page parsing.
- **Database Writer Pattern**: Dedicated DB writer thread to prevent I/O operations from blocking the scraping process.
- **SQLAlchemy 2.0 ORM**: Modern model declaration using Mapped and mapped_column for robust type safety.
- **Docker Integration**: PostgreSQL 16 database pre-configured in an isolated container.
- **Clean Code**: Fully type-hinted and formatted according to industry standards.

## Tech Stack

- **Python 3.10+**
- **Requests + lxml (XPath)**: For networking and HTML parsing.
- **SQLAlchemy**: ORM for database interaction.
- **PostgreSQL 16**: Primary data storage.
- **Docker & Docker Compose**: For database containerization.
- **python-dotenv**: For secure environment variable management.

## Installation and Setup

### 1. Clone the repository and set up the environment
```bash
git clone <your-repo-url>
cd scrapping_vendr
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure Environment Variables
Create a .env file in the project root:
3. 
POSTGRES_DB=vendr
POSTGRES_USER=vendr
POSTGRES_PASSWORD=vendr
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

3. Start the Database (Docker)
```bash
docker-compose up -d
```

4. Run the Scraper
```bash
python -m app.main
```
Data Architecture
The scraper extracts the following fields for each product:

product_name: The name of the software.

category: Software category (e.g., DevOps, IT Infrastructure).

low_price, median_price, high_price: Pricing tiers extracted from range sliders.

description: Product overview/description.