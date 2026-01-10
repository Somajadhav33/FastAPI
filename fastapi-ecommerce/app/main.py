from fastapi import FastAPI, HTTPException, Query
from service.products import get_all_products
from fastapi import Path
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to FASTAPI"}


# @app.get('/products')
# def get_products():
#     return get_all_products()


@app.get("/products")
def list_products(
    name: str = Query(
        default=None, min_length=1, max_length=50, description="Search by name"
    ),
    sort_by_price: bool = Query(default=False, description="Sort Products by price"),
    order: str = Query(
        default="asc", description="Sort order when sort_by_price=true (asc, desc) "
    ),
    limit: int = Query(default=5, ge=1, le=100, description="No of items"),
    offset: int = Query(default=0, ge=0, description="Pagination OffSSet"),
):

    products = get_all_products()
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if not products:
        raise HTTPException(status_code=404, detail=f"No product found name = {name}")

    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)
    products = products[offset : offset + limit]
    return {"total": total, "limit": limit, "items": products}


@app.get("/products/{product_id}")
def get_products_by_id(
    product_id: str = Path(
        ...,
        min_length=36,
        max_length=36,
        description="UUID of the products",
        examples="cad06456-b6d3-4b85-abe8-26bc8afba19a",
    )
):
    products = get_all_products()
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product Not Found")


class Product(BaseModel):
    id: str
    sku: str = "87788-877887-8887"
    name: str


@app.post("/products", status_code=201)
def create_product(product: Product):
    return product
