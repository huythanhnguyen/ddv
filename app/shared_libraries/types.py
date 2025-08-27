"""Data models and schemas for DDV Product Advisor"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ProductCategory(str, Enum):
    """Product categories"""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    ACCESSORY = "accessory"


class Brand(str, Enum):
    """Brand names"""
    SAMSUNG = "Samsung"
    APPLE = "Apple"
    XIAOMI = "Xiaomi"
    OPPO = "OPPO"
    VIVO = "Vivo"
    NOKIA = "Nokia"
    ASUS = "Asus"
    LENOVO = "Lenovo"


class Product(BaseModel):
    """Product model"""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category")
    price: int = Field(..., description="Current price in VND")
    storage: str = Field(..., description="Storage capacity")
    ram: str = Field(..., description="RAM capacity")
    chipset: str = Field(..., description="Processor chipset")
    camera_main: str = Field(..., description="Main camera specification")
    camera_front: str = Field(..., description="Front camera specification")
    battery: str = Field(..., description="Battery specification")
    screen: str = Field(..., description="Screen specification")
    os: str = Field(..., description="Operating system")
    connectivity: List[str] = Field(default_factory=list, description="Connectivity features")
    features: List[str] = Field(default_factory=list, description="Special features")
    url: str = Field(..., description="Product URL on DDV website")


class PriceVariant(BaseModel):
    """Price variant model"""
    variant: str = Field(..., description="Price variant name")
    price_vnd: int = Field(..., description="Current price in VND")
    original_price_vnd: int = Field(..., description="Original price in VND")
    discount_percentage: int = Field(..., description="Discount percentage")
    currency: str = Field(default="VND", description="Currency")


class PricingInfo(BaseModel):
    """Pricing information model"""
    current_prices: List[PriceVariant] = Field(..., description="Current prices")
    price_note: str = Field(..., description="Price note or description")


class PromotionInfo(BaseModel):
    """Promotion information model"""
    free_gifts: List[str] = Field(default_factory=list, description="Free gifts")
    special_discounts: List[str] = Field(default_factory=list, description="Special discounts")
    bundle_offers: List[str] = Field(default_factory=list, description="Bundle offers")


class AvailabilityInfo(BaseModel):
    """Availability information model"""
    status: str = Field(..., description="Availability status")
    delivery: str = Field(..., description="Delivery information")
    available_stores: List[str] = Field(default_factory=list, description="Available store IDs")


class Offer(BaseModel):
    """Offer model"""
    product_id: str = Field(..., description="Product identifier")
    pricing: PricingInfo = Field(..., description="Pricing information")
    promotions: PromotionInfo = Field(..., description="Promotion information")
    availability: AvailabilityInfo = Field(..., description="Availability information")
    last_updated_at: str = Field(..., description="Last update timestamp")


class ReviewSection(BaseModel):
    """Review section model"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")


class PricingRow(BaseModel):
    """Pricing row in review"""
    variant: str = Field(..., description="Variant name")
    current_price: str = Field(..., description="Current price")
    original_price: str = Field(..., description="Original price")


class Comparison(BaseModel):
    """Product comparison model"""
    vs: str = Field(..., description="Comparison target")
    advantages: List[str] = Field(..., description="Advantages")
    disadvantages: List[str] = Field(default_factory=list, description="Disadvantages")


class FAQ(BaseModel):
    """FAQ model"""
    question: str = Field(..., description="Question")
    answer: str = Field(..., description="Answer")


class Review(BaseModel):
    """Review model"""
    product_id: str = Field(..., description="Product identifier")
    table_of_contents: List[str] = Field(default_factory=list, description="Table of contents")
    summary: str = Field(..., description="Review summary")
    sections: List[ReviewSection] = Field(default_factory=list, description="Review sections")
    pricing_table: List[PricingRow] = Field(default_factory=list, description="Pricing information")
    colors: List[str] = Field(default_factory=list, description="Available colors")
    comparisons: List[Comparison] = Field(default_factory=list, description="Product comparisons")
    faqs: List[FAQ] = Field(default_factory=list, description="Frequently asked questions")


class Store(BaseModel):
    """Store model"""
    id: str = Field(..., description="Store identifier")
    name: str = Field(..., description="Store name")
    address: str = Field(..., description="Store address")
    phone: str = Field(..., description="Contact phone")
    status: str = Field(..., description="Store status")
    region: str = Field(..., description="Store region")
    city: str = Field(..., description="Store city")
    parking: Optional[str] = Field(None, description="Parking information")


class ProductRequirement(BaseModel):
    """User product requirement model"""
    budget_min: Optional[int] = Field(None, description="Minimum budget in VND")
    budget_max: Optional[int] = Field(None, description="Maximum budget in VND")
    preferred_brands: List[str] = Field(default_factory=list, description="Preferred brands")
    features: List[str] = Field(default_factory=list, description="Required features")
    location: Optional[str] = Field(None, description="Preferred location")
    use_case: Optional[str] = Field(None, description="Primary use case")


class ProductRecommendation(BaseModel):
    """Product recommendation model"""
    products: List[Product] = Field(..., description="Recommended products")
    reasoning: str = Field(..., description="Reasoning for recommendation")
    alternatives: List[Product] = Field(default_factory=list, description="Alternative products")
    stores: List[Store] = Field(default_factory=list, description="Available stores")
    total_price: int = Field(..., description="Total price for all products")


class StoreRecommendation(BaseModel):
    """Store recommendation model"""
    stores: List[Store] = Field(..., description="Recommended stores")
    product_availability: Dict[str, bool] = Field(..., description="Product availability by store")
    distances: Dict[str, float] = Field(default_factory=dict, description="Distances to stores")
    best_options: List[str] = Field(..., description="Best store options")


class PriceAnalysis(BaseModel):
    """Price analysis model"""
    current_price: int = Field(..., description="Current price")
    original_price: int = Field(..., description="Original price")
    discount_percentage: float = Field(..., description="Discount percentage")
    price_trend: str = Field(..., description="Price trend")
    value_score: float = Field(..., description="Value for money score")
    recommendations: List[str] = Field(..., description="Price recommendations")


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SessionState(BaseModel):
    """Session state model"""
    user_profile: Dict[str, Any] = Field(default_factory=dict, description="User profile")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Conversation history")
    current_use_case: str = Field(default="product_recommendation", description="Current use case")
    system_time: datetime = Field(default_factory=datetime.now, description="System time")
    user_input: Optional[str] = Field(None, description="Current user input")
