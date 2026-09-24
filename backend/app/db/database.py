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

def hamming_distance(hash1: str, hash2: str) -> int:
    try:
        val = int(hash1, 16) ^ int(hash2, 16)
        return bin(val).count('1')
    except:
        return 999

def find_product_by_hash(image_hash: str, threshold: int = 10):
    if not image_hash:
        return None
        
    best_match = None
    min_dist = float('inf')
    
    for product in products_collection.find({"image_hash": {"$exists": True}}):
        dist = hamming_distance(image_hash, product.get("image_hash", ""))
        if dist <= threshold and dist < min_dist:
            min_dist = dist
            best_match = product
            
    return best_match

def get_or_create_product(product_id: str = None, image_hash: str = None):
    if product_id:
        product = products_collection.find_one({"product_id": product_id})
        if product:
            if "_id" in product:
                del product["_id"]
            if "created_at" in product and isinstance(product["created_at"], datetime):
                product["created_at"] = product["created_at"].isoformat()
            return product, False
            
    if image_hash:
        product = find_product_by_hash(image_hash)
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
    barcode = new_id
    
    new_product = {
        "product_id": new_id,
        "barcode": barcode,
        "image_hash": image_hash,
        "created_at": datetime.now(timezone.utc)
    }
    products_collection.insert_one(new_product)
    
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
