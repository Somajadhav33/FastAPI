from pydantic import BaseModel, Field, AnyUrl, field_validator, model_validator, computed_field, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime


# "dimensions_cm": {
#       "length": 27.4,
#       "width": 20.8,
#       "height": 1.9
#     },
class DimensionsCM(BaseModel):
    length: Annotated[float, Field(gt=0, strict=True, description="Length of product in cm", examples=[27.4])]
    width: Annotated[float, Field(gt=0, strict=True, description="Width of product in cm", examples=[20.4])]
    height: Annotated[float, Field(gt=0, strict=True, description="Height of product in cm", examples=[1.4])]


class Seller(BaseModel):
    id: UUID
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Seller Name",
            description="Seller name (3-80 chars).",
            examples=["Mi Store", "Apple Store"],
        ),
    ]
    email: EmailStr
    website: AnyUrl

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        allowed_domains = ["mistore.in",
                           "realmeofficial.in",
                           "samsungindia.in",
                           "lenovostore.in",
                           "hpworld.in",
                           "applestoreindia.in",
                           "dellexclusive.in",
                           "sonycenter.in",
                           "oneplusstore.in",
                           "asusexclusive.in", ]
        domain = str(value).split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed {domain}")

        return value


class Product(BaseModel):
    id: UUID
    sku: Annotated[
        str,
        Field(
            min_length=6,
            max_length=30,
            title="SKU",
            description="Stock Keeping Unit",
            examples=["XIAO-359GB-001", "APPL-212GB-049"],
        ),
    ]
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Product Name",
            description="Readable product name (3-80 chars).",
            examples=["Xiaomi Model Pro", "Apple Model X"],
        ),
    ]

    description: Annotated[
        str,
        Field(max_length=200, description="Short product description"),
    ]

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            description="Category like mobiles/laptops/electronics/accessories",
            examples=["mobiles", "laptops"],
        ),
    ]

    brand: Annotated[
        str,
        Field(min_length=2, max_length=40, examples=["Xiaomi", "Apple"]),
    ]

    price: Annotated[float, Field(gt=0, strict=True, description="Base price (INR)")]
    currency: Literal["INR"] = "INR"

    discount_percent: Annotated[
        int,
        Field(ge=0, le=90, description="Discount in percent (0-90)"),
    ] = 0

    stock: Annotated[int, Field(ge=0, description="Available stock (>=0)")]
    is_active: Annotated[bool, Field(description="Is product active?")]

    rating: Annotated[
        float,
        Field(ge=0, le=5, strict=True, description="Rating out of 5"),
    ]
    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Up to 10 tags"),
    ]
    image_urls: Annotated[
        List[AnyUrl],
        Field(max_length=1, description="At least 1 image url"),
    ]
    dimensions_cm: DimensionsCM
    seller: Seller
    created_at: datetime

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")

        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -234")

        return value

    @model_validator(mode="after")
    @classmethod
    def validate_bussiness_Rules(cls, model: "Product"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("if stock is 0 is_active must be false")

        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("Discounted prise must have rating > 0")

        return model

    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)

    @computed_field
    @property
    def volume_cm3(self) -> float:
        d = self.dimensions_cm
        return round(d.length * d.width * d.height, 2)
