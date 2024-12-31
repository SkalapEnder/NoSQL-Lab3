import inquirer
from pymongo import MongoClient
from bson import ObjectId

# Establish connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['tv_store']
products_collection = db['products']
brands_collection = db['brands']
categories_collection = db['category']


# Getters
# Function to get brand options from MongoDB
def get_brands():
    brands = brands_collection.find()
    return [{'name': brand['brand_name']} for brand in brands]

# Function to get category options from MongoDB
def get_categories():
    categories = categories_collection.find()
    return [{'name': category['category_name']} for category in categories]

# Functions to get free id from collection
def get_free_id_products():
    existing_ids = sorted([product["product_id"] for product in products_collection.find({}, {"product_id": 1})])
    free_id = 100
    for existing_id in existing_ids:
        if existing_id == free_id:
            free_id += 1
        else:
            break
    return free_id

def get_free_id_brands():
    existing_ids = sorted([brand["brand_id"] for brand in brands_collection.find({}, {"brand_id": 1})])
    free_id = 0  # Start checking from ID 1
    for existing_id in existing_ids:
        if existing_id == free_id:
            free_id += 1
        else:
            break
    return free_id

def get_free_id_categories():
    existing_ids = sorted([category["category_id"] for category in categories_collection.find({}, {"category_id": 1})])
    free_id = 0  # Start checking from ID 1
    for existing_id in existing_ids:
        if existing_id == free_id:
            free_id += 1
        else:
            break
    return free_id


# ###################################################

# CRUD - Product
# Create new product
def create_product():
    categories = get_categories()
    brands = get_brands()

    if categories == [] or brands == []:
        print("Category list or brand list are empty! Please, add to both list something!")
        return

    # Ask the user to choose a category and a brand
    questions = [
        inquirer.List('category',
                      message="Which category does the product belong to?",
                      choices=[category['name'] for category in categories]),
        inquirer.List('brand',
                      message="Which company does the product belong to?",
                      choices=[brand['name'] for brand in brands]),
        inquirer.Text('name', message="Enter the product name:"),
        inquirer.Text('price', message="Enter the product price:"),
        inquirer.Text('quantity', message="Enter the product quantity:"),
        inquirer.Text('diagonal', message="Enter the screen size in inches:"),
        inquirer.Text('description', message="Enter the product description:")
    ]
    
    answers = inquirer.prompt(questions)
    
    selected_category = next(item for item in categories if item['name'] == answers['category'])
    selected_brand = next(item for item in brands if item['name'] == answers['brand'])
    
    # Create new product document
    new_product = {
        "product_id": get_free_id_products(),
        "name": answers['name'],
        "price": float(answers['price']),
        "quantity": int(answers['quantity']),
        "diagonal": float(answers['diagonal']),
        "description": answers['description'],
        "category": selected_category['name'],
        "brand": selected_brand['name']
    }

    # Insert new product into the products collection
    products_collection.insert_one(new_product)
    print("Product successfully added!")

# Display products by category or brand
def display_products():
    categories = list(categories_collection.find().sort({"category_id": 1}))
    brands = list(brands_collection.find().sort({"brand_id": 1}))

    # Ask user whether to filter by category or brand
    filter_choice = inquirer.List(
        'filter_choice', 
        message="Filter products by", 
        choices=["Category", "Brand", "All"]
    )
    filter_answer = inquirer.prompt([filter_choice])

    if filter_answer['filter_choice'] == "Category":
        category_choice = inquirer.List(
            'category', 
            message="Select category", 
            choices=[category['category_name'] for category in categories]
        )
        selected_category = inquirer.prompt([category_choice])

        # Find products by category_id
        category = next(item for item in categories if item['category_name'] == selected_category['category'])
        products = products_collection.find({'category_id': category['category_id']}).sort("product_id", 1)

    elif filter_answer['filter_choice'] == "Brand":
        brand_choice = inquirer.List(
            'brand', 
            message="Select brand", 
            choices=[brand['brand_name'] for brand in brands]
        )
        selected_brand = inquirer.prompt([brand_choice])

        # Find products by brand_id
        brand = next(item for item in brands if item['brand_name'] == selected_brand['brand'])
        products = products_collection.find({'brand_id': brand['brand_id']}).sort("product_id", 1)

    else:  # No filter
        products = products_collection.find().sort("product_id", 1)

    # Display products
    print("\nProducts:")
    for product in products:
        # Get category and brand names for display
        category_name = next((cat['category_name'] for cat in categories if cat.get('category_id') == product.get('category_id')), "Unknown")
        brand_name = next((brand['brand_name'] for brand in brands if brand.get('brand_id') == product.get('brand_id')), "Unknown")

        print(f"\nID: {product['product_id']}\n"
              f"Name: {product['name']}\n"
              f"Price: ${product['price']}\n"
              f"Quantity: {product['quantity']}\n"
              f"Screen size: {product['diagonal']}\n"
              f"Category: {category_name}\n"
              f"Brand: {brand_name}\n"
              f"Description: {product['description']}")

# Display all products in short variant
def display_products_short():
    products = products_collection.find({}, {'product_id': 1, 'name': 1, '_id': 0}).sort({"product_id": 1})
    print("\nShort list of products")
    for product in products:
        print(f"ID: {product['product_id']} Name: {product['name']}")

# Update product
def update_product():
    display_products_short()

    questions = [
        inquirer.Text('product_id', message="Enter product ID to update:")
    ]
    answers = inquirer.prompt(questions)

    categories = get_categories()
    brands = get_brands()

    product_id = int(answers['product_id'])
    product = products_collection.find_one({"product_id": product_id})

    if product:
        questions = [
            inquirer.Text('name', message="Enter new product name", default=product['name']),
            inquirer.Text('price', message="Enter new product price", default=str(product['price'])),
            inquirer.Text('quantity', message="Enter new product quantity", default=str(product['quantity'])),
            inquirer.Text('diagonal', message="Enter new screen size", default=str(product['diagonal'])),
            inquirer.Text('description', message="Enter new product description", default=product['description']),
            inquirer.List('category', message="Select new category", choices=[category['category_name'] for category in categories], default=next(category['category_name'] for category in categories if category['category_id'] == product['category'])),
            inquirer.List('brand', message="Select new brand", choices=[brand['brand_name'] for brand in brands], default=next(brand['brand_name'] for brand in brands if brand['brand_id'] == product['brand']))
        ]
        updated_data = inquirer.prompt(questions)

        # Map category and brand names back to their IDs
        updated_category_id = next(category['category_id'] for category in categories if category['category_name'] == updated_data['category'])
        updated_brand_id = next(brand['brand_id'] for brand in brands if brand['brand_name'] == updated_data['brand'])

        # Prepare the updated product data
        updated_product = {
            "name": updated_data['name'],
            "price": float(updated_data['price']),
            "quantity": int(updated_data['quantity']),
            "diagonal": float(updated_data['diagonal']),
            "description": updated_data['description'],
            "category": updated_category_id,
            "brand": updated_brand_id
        }

        # Update the product in the database
        products_collection.update_one(
            {"product_id": product_id},
            {"$set": updated_product}
        )
        print("Product updated successfully!")
    else:
        print("Product not found!")

# Remove product by product_id
def remove_product():
    display_products_short()

    questions = [
        inquirer.Text('product_id', message="Enter product ID to update:")
    ]
    answers = inquirer.prompt(questions)

    product_id = int(answers['product_id'])
    product = products_collection.find_one({"product_id": int(product_id)})
    
    if product:
        products_collection.delete_one({"product_id": int(product_id)})
        print("Product removed successfully!")
    else:
        print("Product not found!")

# ###################################################

# CRUD - Brand
# Create new brand
def create_brand():
    questions = [
        inquirer.Text('brand_name', message="Enter brand name"),
        inquirer.Text('brand_description', message="Enter brand description", default=''),
        inquirer.Text('headquarters', message="Enter country of origin", default=''),
        inquirer.Text('founded_year', message="Enter year of establishment", default=''),
        inquirer.Text('website', message='Enter the web link to website', default='')
    ]
    answers = inquirer.prompt(questions)
    brand = {
        "brand_id": get_free_id_brands(),
        "brand_name": answers['brand_name'],
        "brand_description": answers['brand_description'],
        "headquarters": answers['headquarters'],
        "founded_year": int(answers['founded_year']),
        "website": answers['website']
    }
    brands_collection.insert_one(brand)
    print("Brand created successfully!")

# Display all brands
def display_brands():
    brands = brands_collection.find().sort({"brand_id": 1})
    for brand in brands:
        print(f"\nID: {brand['brand_id']}\nName: {brand['brand_name']}\nDescription: {brand['brand_description']}\nLocation: {brand['headquarters']}\nEstablished: {brand['founded_year']}\nWebsite: {brand['website']}")

def display_brands_short():
    brands = brands_collection.find({}, {"brand_name": 1, "brand_id": 1}).sort({"brand_id": 1})
    print("\nBrands:")
    for brand in brands:
        print(f"ID: {brand['brand_id']} Name: {brand['brand_name']}")

# Update brand
def update_brand():
    display_brands_short()

    questions_start = [
        inquirer.Text('brand_id', message="Enter the brand ID to update:")
    ]
    answers = inquirer.prompt(questions_start)

    brand_id = int(answers['brand_id'])
    brand = brands_collection.find_one({"brand_id": brand_id})

    if brand:
        questions = [
            inquirer.Text('brand_name', message="Enter new brand name", default=brand['brand_name']),
            inquirer.Text('brand_description', message="Enter new brand description", default=brand['brand_description']),
            inquirer.Text('headquarters', message="Enter new country of origin", default=brand['headquarters']),
            inquirer.Text('founded_year', message="Enter new year of establishment", default=brand['founded_year']),
            inquirer.Text('website', message="Enter new link to website", default=brand['website'])
        ]
        answers = inquirer.prompt(questions)

        # Update brand details
        updated_brand = {
            "brand_name": answers['brand_name'],
            "brand_description": answers['brand_description'],
            "headquarters": answers['headquarters'],
            "founded_year": int(answers['founded_year']),
            "website": answers['website']
        }

        brands_collection.update_one({"brand_id": brand_id}, {"$set": updated_brand})
        print("Brand updated successfully!")
    else:
        print("Brand not found!")


# Remove brand by brand_id
def remove_brand():
    display_brands_short()

    questions = [
        inquirer.Text('brand_id', message="Enter brand ID to delete:")
    ]
    answers = inquirer.prompt(questions)

    brand_id = int(answers['brand_id'])
    brand = brands_collection.find_one({"brand_id": brand_id})

    if brand:
        products_collection.delete_many({"brand_id": brand_id})
        brands_collection.delete_one({"brand_id": brand_id})
        print("Brand and all relevant products removed successfully!")
    else:
        print("Brand not found!")

# ###################################################

# CRUD - Category
# Create new category
def create_category():
    questions = [
        inquirer.Text('category_name', message="Enter category name"),
        inquirer.Text('category_description', message="Enter category description"),
        inquirer.Text('category_type', message="Enter type of category", default="Display Technologies"),
        inquirer.Text('target_audience', message="Enter target audience", default="General consumers")
    ]
    answers = inquirer.prompt(questions)
    category = {
        "category_id": get_free_id_categories(),
        "category_name": answers['category_name'],
        "category_description": answers['category_description'],
        'category_type': answers['category_type'],
        'target_audience': answers['target_audience']
    }
    categories_collection.insert_one(category)
    print("Category created successfully!")

# Display all categories
def display_categories():
    categories = categories_collection.find().sort({"category_id": 1})
    for category in categories:
        print(f"\nID: {category['category_id']}\nName: {category['category_name']}\nDescription: {category['category_description']}\nType: {category['category_type']}\nTarget audience: {category['target_audience']}")

def display_categories_short():
    categories = categories_collection.find({}, {"category_name": 1, "category_id": 1, "_id": 0}).sort({"category_id": 1})
    print("\nCategories:")
    for category in categories:
        print(f"ID: {category['category_id']} Name: {category['category_name']}")

# Update category
def update_category():
    display_categories_short()

    questions_start = [
        inquirer.Text('category_id', message="Enter the category ID to update:")
    ]
    answers = inquirer.prompt(questions_start)

    category_id = int(answers['category_id'])
    category = categories_collection.find_one({"category_id": category_id})

    if category:
        questions = [
            inquirer.Text('category_name', message="Enter new category name", default=category['category_name']),
            inquirer.Text('category_description', message="Enter new category description", default=category['category_description']),
            inquirer.Text('category_type', message="Enter new category type", default=category['category_type']),
            inquirer.Text('target_audience', message="Enter new target audience", default=category['target_audience'])
        ]
        answers = inquirer.prompt(questions)

        # Update category details
        updated_category = {
            "category_name": answers['category_name'],
            "category_description": answers['category_description'],
            "category_type": answers['category_type'],
            "target_audience": answers['target_audience']
        }

        categories_collection.update_one({"category_id": category_id}, {"$set": updated_category})
        print("Category updated successfully!")
    else:
        print("Category not found!")

# Remove category by category_id
def remove_category():
    display_categories_short()

    questions = [
        inquirer.Text('category_id', message="Enter category ID to delete:")
    ]
    answers = inquirer.prompt(questions)

    category_id = int(answers['category_id'])
    category = categories_collection.find_one({"category_id": category_id})

    if category:
        products_collection.delete_many({"category_id": category_id})
        categories_collection.delete_one({"category_id": category_id})
        print("Category and all relevant products removed successfully!")
    else:
        print("Category not found!")

# ###################################################

# Sections menu
def product_menu():
    questions_product = [
            inquirer.List('action', message="Select an action", choices=["Create Product", "Display Products", "Update Product", "Remove Product", "Exit"])
        ]
        
    answers = inquirer.prompt(questions_product)
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
        pass
    return

def brand_menu():
    questions_brand = [
        inquirer.List('action', message="Select an action", choices=[
            "Create Brand", "Display Brands", "Update Brand", "Remove Brand", "Exit"])
    ]

    answers = inquirer.prompt(questions_brand)
    action = answers['action']

    if action == "Create Brand":
        create_brand()
    elif action == "Display Brands":
        display_brands()
    elif action == "Update Brand":
        update_brand()
    elif action == "Remove Brand":
        remove_brand()
    elif action == "Exit":
        return

def category_menu():
    questions_category = [
        inquirer.List('action', message="Select an action", choices=[
            "Create Category", "Display Categories", "Update Category", "Remove Category", "Exit"])
    ]

    answers = inquirer.prompt(questions_category)
    action = answers['action']

    if action == "Create Category":
        create_category()
    elif action == "Display Categories":
        display_categories()
    elif action == "Update Category":
        update_category()
    elif action == "Remove Category":
        remove_category()
    elif action == "Exit":
        return

# ###################################################

# Main menu
def main_menu():
    questions_main = [
        inquirer.List('main', message="Select an section", choices=["Product", "Category", "Brand", "Exit"])
    ]

    while True:
        answers = inquirer.prompt(questions_main)
        main_action = answers['main']

        if main_action == "Product":
            product_menu()
        elif main_action == "Category":
            category_menu()
        elif main_action == "Brand":
            brand_menu()
        elif main_action == "Exit":
            break


        
if __name__ == '__main__':
    main_menu()
