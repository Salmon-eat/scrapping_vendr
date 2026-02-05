# Project Overview

This project is a high-performance web scraping system designed to extract book data from the "Books to Scrape" website. 
It leverages a multiprocessing architecture to ensure scalability and speed, while adhering to the SOLID, DRY, and 
KISS principles.

The system uses Playwright for browser automation and SQLAlchemy for persistent data storage in a PostgreSQL database.

## Key Features
Concurrency: Implements Python's multiprocessing module to bypass the Global Interpreter Lock (GIL) and maximize CPU usage.

Database Management: Uses SQLAlchemy with a thread-safe session management approach to handle concurrent database writes.

Resource Optimization: Employs multiprocessing.Manager().Queue(maxsize=100) to prevent memory overflow.

Page Object Model (POM): Organizes parsing logic into dedicated classes for better maintainability and readability.

## Requirements
Python 3.10+
Docker and Docker Compose
Playwright (Chromium)
SQLAlchemy
PostgreSQL

## Installation and Usage
Clone the repository: 
```bash 
git clone <repository_url>
```
Setup environment: Create a .env file with your database credentials (DB_USER, DB_PASSWORD, DB_NAME, DB_HOST).

Run with Docker: 
```bash
docker-compose up --build
```

Monitor execution: The system provides detailed logs including execution time and record confirmation.