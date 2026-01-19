"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional


class CreateOrderRequest(BaseModel):
    plan_id: int
    amount: float  # Amount in USD (e.g., 100 for $100)
    user_id: int


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_id: int


class PaymentOrderResponse(BaseModel):
    razorpay_key_id: str
    razorpay_order_id: str
    amount: float
    currency: str
    order_id: int


class PaymentVerifyResponse(BaseModel):
    success: bool
    message: str
    subscription_id: Optional[int] = None

class WalletTopUpRequest(BaseModel):
    amount: float  # Amount in USD

class WalletTopUpOrderResponse(BaseModel):
    razorpay_key_id: str
    razorpay_order_id: str
    amount: float
    currency: str
    transaction_id: int

class WalletTopUpVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    transaction_id: int

class WalletTopUpVerifyResponse(BaseModel):
    success: bool
    message: str
    new_balance: Optional[float] = None
    transaction_id: Optional[int] = None