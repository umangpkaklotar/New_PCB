import os
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "pcb_inspection_db")

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

products_collection = db["products"]
inspections_collection = db["inspections"]

# Ensure unique index on product_id
products_collection.create_index("product_id", unique=True)
products_collection.create_index("barcode", unique=True)
inspections_collection.create_index("inspection_request_id", unique=True, sparse=True)

def get_product_by_barcode(barcode: str):
    product = products_collection.find_one({"barcode": barcode})
    if product:
        if "_id" in product:
            del product["_id"]
        if "created_at" in product and isinstance(product["created_at"], datetime):
            product["created_at"] = product["created_at"].isoformat()
    return product

def get_or_create_product(barcode: str = None):
    if barcode:
        product = products_collection.find_one({"barcode": barcode})
        if product:
            if "_id" in product:
                del product["_id"]
            if "created_at" in product and isinstance(product["created_at"], datetime):
                product["created_at"] = product["created_at"].isoformat()
            return product, False
    
    # Create new product with sequential ID (PCB-000001)
    last_product = products_collection.find_one(
        {"product_id": {"$regex": "^PCB-"}}, 
        sort=[("product_id", -1)]
    )
    new_num = 1
    if last_product and "product_id" in last_product:
        try:
            last_num = int(last_product["product_id"].split("-")[1])
            new_num = last_num + 1
        except ValueError:
            pass
            
    new_id = f"PCB-{new_num:06d}"
    new_barcode = barcode if barcode else new_id
    
    new_product = {
        "product_id": new_id,
        "barcode": new_barcode,
        "created_at": datetime.now(timezone.utc)
    }
    
    try:
        products_collection.insert_one(new_product)
    except Exception:
        product = products_collection.find_one({"barcode": new_barcode})
        if product:
            if "_id" in product:
                del product["_id"]
            if "created_at" in product and isinstance(product["created_at"], datetime):
                product["created_at"] = product["created_at"].isoformat()
            return product, False
    
    # We return the dict without the '_id' object to avoid JSON serialization issues in FastAPI
    if "_id" in new_product:
        del new_product["_id"]
    if "created_at" in new_product and isinstance(new_product["created_at"], datetime):
        new_product["created_at"] = new_product["created_at"].isoformat()
        
    return new_product, True

def save_inspection(inspection_data: dict):
    from pymongo import ReturnDocument
    
    if "inspection_request_id" in inspection_data and inspection_data["inspection_request_id"]:
        # Atomic upsert to prevent race conditions on duplicate inserts
        inspection_data["created_at"] = datetime.now(timezone.utc)
        
        # Move inspection_data into $setOnInsert so we don't overwrite if it already exists
        result = inspections_collection.find_one_and_update(
            {"inspection_request_id": inspection_data["inspection_request_id"]},
            {"$setOnInsert": inspection_data},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        
        if "_id" in result:
            del result["_id"]
        if "created_at" in result and isinstance(result["created_at"], datetime):
            result["created_at"] = result["created_at"].isoformat()
            
        return result
        
    else:
        inspection_data["created_at"] = datetime.now(timezone.utc)
        inspections_collection.insert_one(inspection_data)
        
        if "_id" in inspection_data:
            del inspection_data["_id"]
        if "created_at" in inspection_data and isinstance(inspection_data["created_at"], datetime):
            inspection_data["created_at"] = inspection_data["created_at"].isoformat()
            
        return inspection_data

def find_matching_pcb_by_hash(image_hash: str, threshold: int = 10):
    if not image_hash:
        return None, None
        
    # Find matching hash by calculating Hamming distance
    cursor = inspections_collection.find({"image_hash": {"$exists": True}}).sort("created_at", -1).limit(1000)
    for inspection in cursor:
        db_hash = inspection.get("image_hash")
        if not db_hash: continue
        
        dist = bin(int(image_hash, 16) ^ int(db_hash, 16)).count('1')
        if dist <= threshold:
            product = products_collection.find_one({"product_id": inspection["product_id"]})
            if product:
                if "_id" in product:
                    del product["_id"]
                if "created_at" in product and isinstance(product["created_at"], datetime):
                    product["created_at"] = product["created_at"].isoformat()
                    
            if "_id" in inspection:
                del inspection["_id"]
            if "created_at" in inspection and isinstance(inspection["created_at"], datetime):
                inspection["created_at"] = inspection["created_at"].isoformat()
                
            return inspection, product
            
    return None, None
