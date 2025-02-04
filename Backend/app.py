from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from langgraph import LangGraph
from transformers import pipeline
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models
class Product(Base):
    __tablename__ = "products"
    ProductID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Brand = Column(String)
    Price = Column(Float)
    Category = Column(String)
    Description = Column(Text)
    SupplierID = Column(Integer, ForeignKey("suppliers.SupplierID"))

class Supplier(Base):
    __tablename__ = "suppliers"
    SupplierID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    ContactInfo = Column(String)
    ProductCategoriesOffered = Column(Text)

# Initialize FastAPI
app = FastAPI()

# LangGraph setup
graph = LangGraph()

# LLM setup for summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Define nodes for LangGraph
@graph.node
def fetch_products_by_category(category: str):
    db = SessionLocal()
    products = db.query(Product).filter(Product.Category == category).all()
    db.close()
    return products

@graph.node
def fetch_suppliers_by_category(category: str):
    db = SessionLocal()
    suppliers = db.query(Supplier).filter(Supplier.ProductCategoriesOffered.contains(category)).all()
    db.close()
    return suppliers

@graph.node
def summarize_supplier(supplier: Supplier):
    summary = summarizer(supplier.ProductCategoriesOffered, max_length=50, min_length=25, do_sample=False)
    return summary[0]['summary_text']

# Define workflow
@graph.workflow
def handle_query(query: str):
    if "product" in query.lower() and "category" in query.lower():
        category = query.split("category")[-1].strip()
        products = fetch_products_by_category(category)
        return {"products": [p.__dict__ for p in products]}
    elif "supplier" in query.lower() and "category" in query.lower():
        category = query.split("category")[-1].strip()
        suppliers = fetch_suppliers_by_category(category)
        summaries = [summarize_supplier(s) for s in suppliers]
        return {"suppliers": [s.__dict__ for s in suppliers], "summaries": summaries}
    else:
        raise HTTPException(status_code=400, detail="Invalid query")

# API endpoint
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_database(request: QueryRequest):
    try:
        result = handle_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)