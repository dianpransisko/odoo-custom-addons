from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Ecommerce Marketplace Mock API", version="2.0.0")

# --- DATA SCHEMAS (Parameter) ---

class Buyer(BaseModel):
    name: str
    username: str
    phone: str
    email: str

class ShippingAddress(BaseModel):
    recipient_name: str
    phone: str
    address_line1: str
    city: str
    province: str
    postal_code: str
    country: str

class OrderItem(BaseModel):
    sku: str
    name: str
    qty: int
    price: float

class Payment(BaseModel):
    method: str
    paid_amount: float
    payment_status: str

class ShippingInfo(BaseModel):
    courier: str
    service: str
    shipping_fee: float

class FullOrder(BaseModel):
    order_sn: str
    order_status: str
    create_time: int
    buyer: Buyer
    shipping_address: ShippingAddress
    items: List[OrderItem]
    payment: Payment
    shipping: ShippingInfo

# . Tambahkan Schema Status
class StatusUpdate(BaseModel):
    order_sn: str
    new_status: str  # Contoh: 'CANCELLED_STOCK_OUT' atau 'SHIPPED'
    message: Optional[str] = None


# --- SCHEMA TAMBAHAN UNTUK STOK ---
class StockUpdate(BaseModel):
    item_id: str
    new_stock: int

# --- DATABASE SIMULATION ---
ORDERS_DB = []
STOCK_DB = {} # Menyimpan simulasi stok di sisi Marketplace

# 2. Tambahkan Endpoint Update Status
@app.post("/api/v2/order/update_status")
def update_order_status(payload: StatusUpdate, authorization: Optional[str] = Header(None)):
    if authorization != "L5WDGoBLjmeNjpNwuxoY":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Cari order di database simulasi
    order = next((o for o in ORDERS_DB if o["order_sn"] == payload.order_sn), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order SN tidak ditemukan")
    
    # Update statusnya
    order["order_status"] = payload.new_status
    print(f">>> API ALERT: Order {payload.order_sn} STATUS BERUBAH -> {payload.new_status} | Note: {payload.message}")
    
    return {"status": "success", "order_sn": payload.order_sn, "current_status": payload.new_status}

# --- ENDPOINTS ORDER ---

@app.post("/api/v2/order/create_test_order")
def create_test_order(payload: FullOrder):
    """Endpoint untuk menyuntikkan pesanan simulasi"""
    if any(o['order_sn'] == payload.order_sn for o in ORDERS_DB):
        return {"status": "error", "message": "Order SN sudah ada"}
    
    ORDERS_DB.append(payload.dict())
    print(f">>> MOCK API: Pesanan {payload.order_sn} dari {payload.buyer.username} BERHASIL DITERIMA.")
    return {"status": "success", "order_sn": payload.order_sn}

@app.get("/api/v2/order/get_order_list")
def get_order_list(authorization: Optional[str] = Header(None)):
    if authorization != "L5WDGoBLjmeNjpNwuxoY":
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    return {
        "response": {
            "order_list": [{"order_sn": o["order_sn"]} for o in ORDERS_DB],
            "more": False
        }
    }

@app.get("/api/v2/order/get_order_detail")
def get_order_detail(order_sn: str, authorization: Optional[str] = Header(None)):
    order = next((o for o in ORDERS_DB if o["order_sn"] == order_sn), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"response": {"order_list": [order]}, "message": "success"}

# --- ENDPOINT STOK (BARU) ---

@app.post("/api/v2/product/update_stock")
def update_stock(payload: StockUpdate, authorization: Optional[str] = Header(None)):
    """Endpoint yang dipanggil Odoo untuk sinkronisasi stok"""
    if authorization != "L5WDGoBLjmeNjpNwuxoY":
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    # Simulasi update di database marketplace
    STOCK_DB[payload.item_id] = payload.new_stock
    
    print(f">>> API LOG: Stok Produk ID {payload.item_id} diupdate oleh Odoo menjadi {payload.new_stock}")
    return {"status": "success", "message": f"Stok ID {payload.item_id} berhasil diupdate."}

#--------------Database Sementara kiriman dari ERP ---------------
@app.get("/debug/all_data")
def peek_database():
    """Endpoint untuk melihat isi database API saat ini"""
    return {
        "simulated_marketplace_stock": STOCK_DB,
        "simulated_marketplace_orders": ORDERS_DB
    }