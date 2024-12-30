import inquirer
from pymongo import MongoClient
from bson import ObjectId

# Establish connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['tv_store']
products_collection = db['products']
brands_collection = db['brands']
categories_collection = db['categories']

# Function to get brand options from MongoDB
def get_brands():
    brands = brands_collection.find()
    return [{'name': brand['brand_name'], 'value': brand['_id']} for brand in brands]

# Function to get category options from MongoDB
def get_categories():
    categories = categories_collection.find()
    return [{'name': category['category_name'], 'value': category['_id']} for category in categories]

# 1) Create new product
def create_product():
    categories = get_categories()
    brands = get_brands()

    # Ask the user to choose a category and a brand
    questions = [
        inquirer.List('category',
                      message="Which category does the product belong to?",
                      choices=[category['name'] for category in categories]),
        inquirer.List('brand',
                      message="Which company does the product belong to?",
                      choices=[brand['name'] for brand in brands]),
        inquirer.Text('name', message="Enter the product name:"),
        inquirer.Number('price', message="Enter the product price:"),
        inquirer.Number('quantity', message="Enter the product quantity:"),
        inquirer.Text('description', message="Enter the product description:")
    ]
    
    answers = inquirer.prompt(questions)
    
    selected_category = next(item for item in categories if item['name'] == answers['category'])
    selected_brand = next(item for item in brands if item['name'] == answers['brand'])
    
    # Create new product document
    new_product = {
        "product_id": answers['product_id'],
        "name": answers['name'],
        "price": answers['price'],
        "quantity": answers['quantity'],
        "description": answers['description'],
        "category": {
            "_id": selected_category['value'],
            "category_name": selected_category['name']
        },
        "brand": {
            "_id": selected_brand['value'],
            "brand_name": selected_brand['name']
        }
    }

    # Insert new product into the products collection
    products_collection.insert_one(new_product)
    print("Product successfully added!")

# 2) Display products by category or brand
def display_products():
    # Ask user whether to filter by category or brand
    filter_choice = inquirer.List('filter_choice', message="Filter products by", choices=["Category", "Brand"])
    filter_answer = inquirer.prompt([filter_choice])

    if filter_answer['filter_choice'] == "Category":
        categories = get_categories()
        category_choice = inquirer.List('category', message="Select category", choices=[category['name'] for category in categories])
        selected_category = inquirer.prompt([category_choice])

        # Find products by category
        category = next(item for item in categories if item['name'] == selected_category['category'])
        products = products_collection.find({'category._id': category['value']})

    elif filter_answer['filter_choice'] == "Brand":
        brands = get_brands()
        brand_choice = inquirer.List('brand', message="Select brand", choices=[brand['name'] for brand in brands])
        selected_brand = inquirer.prompt([brand_choice])

        # Find products by brand
        brand = next(item for item in brands if item['name'] == selected_brand['brand'])
        products = products_collection.find({'brand._id': brand['value']})

    # Display products
    print("\nProducts:")
    for product in products:
        print(f"{product['name']} ({product['category']['category_name']}) - ${product['price']}")

# 3) Update product property
def update_product():
    product_id = inquirer.Text('product_id', message="Enter product ID to update:").prompt()
    product = products_collection.find_one({"product_id": int(product_id)})
    
    if product:
        questions = [
            inquirer.Text('name', message="Enter new product name", default=product['name']),
            inquirer.Number('price', message="Enter new product price", default=product['price']),
            inquirer.Number('quantity', message="Enter new product quantity", default=product['quantity']),
            inquirer.Text('description', message="Enter new product description", default=product['description']),
        ]
        updated_data = inquirer.prompt(questions)

        # Update the product
        products_collection.update_one(
            {"product_id": int(product_id)},
            {"$set": updated_data}
        )
        print("Product updated successfully!")
    else:
        print("Product not found!")

# 4) Remove product by product_id
def remove_product():
    product_id = inquirer.Text('product_id', message="Enter product ID to remove:").prompt()
    product = products_collection.find_one({"product_id": int(product_id)})
    
    if product:
        products_collection.delete_one({"product_id": int(product_id)})
        print("Product removed successfully!")
    else:
        print("Product not found!")

# Main menu
def main_menu():
    questions = [
        inquirer.List('action', message="Select an action", choices=["Create Product", "Display Products", "Update Product", "Remove Product", "Exit"])
    ]
    
    while True:
        answers = inquirer.prompt(questions)
        action = answers['action']
        
        if action == "Create Product":
            create_product()
        elif action == "Display Products":
            display_products()
        elif action == "Update Product":
            update_product()
        elif action == "Remove Product":
            remove_product()
        elif action == "Exit":
            break

if __name__ == '__main__':
    main_menu()
