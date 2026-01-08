from fastapi import FastAPI, HTTPException, Query
from service.products import get_all_products

app = FastAPI()

@app.get('/')
def root():
    return {"message" : "Welcome to FASTAPI"}
    

# @app.get('/products')
# def get_products():
#     return get_all_products()

@app.get("/products")
def list_products(name: str = Query(default=None, min_length=1, max_length=50, description="Search by name") ):
    
    products = get_all_products()
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]
        if not products:
            raise HTTPException(status_code=404, detail=f"No product found name = {name}")
        
        total = len(products)
    return {
        "total": total,
        "items" : products
    }