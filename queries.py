import connection

def get_all_supermarkets():
    return connection.execute_select("""
    SELECT *
    FROM supermarket
    """)


def get_products_by_supermarket_id(supermarket_id):
    return connection.execute_select("""
    SELECT *
    FROM products
    WHERE supermarket_id = %(supermarket_id)s
    """, {'supermarket_id': supermarket_id})


def insert_register_request(request):
    connection.execute_dml_statement("""
        INSERT INTO requests (username, password, user_status_id, name, email, phone_number,address)
        VALUES ( %(username)s,
        %(password)s,
        %(status)s,
        %(name)s,
        %(email)s,
        %(phone_number)s,
        %(address)s
        )
    """, request)


def confirm_register_request(request_id):
    connection.execute_dml_statement("""
        INSERT INTO users (username, password, user_status_id, name, email, phone_number, cui_number)  
        (SELECT username, password, user_status_id, name, email, phone_number, cui_number         
         FROM requests WHERE request_id = %(request_id)s);
         INSERT INTO supermarket(name, address, user_id)  SELECT name, address, 
                (SELECT last_value FROM users_user_id_seq) as user_id FROM requests WHERE request_id = %(request_id)s;
         DELETE FROM requests WHERE  request_id = %(request_id)s;
    """, {"request_id": request_id})
    return connection.execute_select("""SELECT email, name FROM users 
    WHERE user_id = (SELECT last_value FROM users_user_id_seq);""")


def confirm_register_request_for_organisation(request_id):
    connection.execute_dml_statement("""
        INSERT INTO users (username, password, user_status_id, name, email, phone_number, cui_number)  
        (SELECT username, password, user_status_id, name, email, phone_number, cui_number         
         FROM requests WHERE request_id = %(request_id)s);
         INSERT INTO user_cart(user_id)  SELECT last_value FROM users_user_id_seq;
         DELETE FROM requests WHERE  request_id = %(request_id)s;
    """, {"request_id": request_id})
    return connection.execute_select("""SELECT email, name FROM users 
    WHERE user_id = (SELECT last_value FROM users_user_id_seq);""")


def get_user(username):
    return connection.execute_select("""
        SELECT user_id, username, password , users.name, us.name as status 
        FROM users
        JOIN user_status us on us.user_status_id = users.user_status_id
        WHERE username = %(username)s
    """, {"username": username})


def get_address():
    return connection.execute_select("""
    SELECT *
    FROM supermarket
    """)


def get_product_by_id_product(product_id):
    return connection.execute_select("""
    SELECT *
    FROM products
    """, {'product_id': product_id})


def get_register_requests():
    return connection.execute_select("""
        SELECT requests.request_id, requests.username, requests.user_status_id, requests.name, 
            requests.email, requests.phone_number, requests.cui_number, us.name as status
        FROM requests
        JOIN user_status us on us.user_status_id = requests.user_status_id;
    """)


def reject_register_request(request_id):
    user = connection.execute_select("SELECT name, email FROM requests WHERE request_id=%(request_id)s",
                                     {"request_id": request_id})
    connection.execute_dml_statement("""
        DELETE FROM requests
        WHERE request_id=%(request_id)s;
    """, {"request_id": request_id})
    return user


def get_supermarket_by_id(supermarket_id):
    return connection.execute_select("""
    SELECT *
    FROM supermarket
    WHERE supermarket_id = %(supermarket_id)s
    """, {"supermarket_id": supermarket_id}, False)


def insert_product(product):
    return connection.execute_dml_statement("""
    INSERT 
    INTO products(supermarket_id, category_id, name, quantity, price, expire_date) 
    values (%(supermarket_id)s, %(category_id)s, %(name)s, %(quantity)s, %(price)s, %(expire_date)s)
    """, product)


def delete_product(product_id):
    return connection.execute_select("""
    DELETE 
    FROM products
    WHERE product_id = %(product_id)s
    """, {"product_id": product_id})


def update_product(product_id, new_quantity):
    return connection.execute_dml_statement("""
    UPDATE products 
    SET quantity = %(new_quantity)s
    WHERE product_id=%(product_id)s
    """, {"product_id": product_id, "new_quantity": new_quantity})


def edit_product(product):
    return connection.execute_dml_statement("""
    UPDATE products 
    SET quantity = %(quantity)s,
        name = %(name)s,
        expire_date = %(expire_date)s
    WHERE product_id=%(product_id)s
    """, product)


def add_products_to_cart_by_id(user_id, product_id, quantity):
    return connection.execute_dml_statement("""
        INSERT INTO cart_products (cart_id, product_id, quantity)
        VALUES ((SELECT cart_id FROM user_cart WHERE user_id = %(user_id)s 
        ORDER BY cart_id DESC LIMIT 1), %(product_id)s, %(quantity)s)
        RETURNING 1 as row
    """, {"user_id": user_id, "product_id": product_id, "quantity": quantity})


def get_total_quantity_reserved_by_product_id(product_id, user_id):
    return connection.execute_select("""
    SELECT SUM(quantity) AS total_quantity
    FROM cart_products    
    WHERE product_id = %(product_id)s AND cart_id = (SELECT cart_id 
                FROM user_cart WHERE user_id= %(user_id)s ORDER BY cart_id DESC LIMIT 1)
    """, {"product_id": product_id, "user_id": user_id}, False)


def get_quantity_by_product_id(product_id):
    return connection.execute_select("""
    SELECT quantity
    FROM products
    WHERE product_id = %(product_id)s
    """, {"product_id": product_id}, False)


def get_cart_products_by_user_id(user_id):
    return connection.execute_select("""
    SELECT cp.quantity, cp.product_id, cp.cart_id, p.name
    FROM cart_products cp
    JOIN user_cart uc on uc.cart_id = cp.cart_id 
    JOIN products p on p.product_id = cp.product_id
    WHERE user_id = %(user_id)s AND uc.cart_id = (SELECT cart_id FROM user_cart ORDER BY cart_id DESC LIMIT 1)
    """, {"user_id": user_id})


def get_product_quantity(product_id):
    return connection.execute_select("""
        SELECT quantity FROM products WHERE product_id=%(product_id)s
    """, {"product_id": product_id})[0]


def place_order(user_id):
    products = get_cart_products_by_user_id(user_id)
    for product in products:
        update_product(product["product_id"], get_product_quantity(product["product_id"])["quantity"] - product["quantity"])
    connection.execute_dml_statement("""
        INSERT INTO orders(user_id, cart_id) VALUES (%(user_id)s, 
            (SELECT cart_id FROM user_cart WHERE user_cart.user_id=%(user_id)s ORDER BY cart_id DESC LIMIT 1));
        INSERT INTO user_cart (user_id) values (%(user_id)s);
    """, {"user_id": user_id})


def get_orders_by_user_id(user_id):
    return connection.execute_select("""
    SELECT *
    FROM orders
    WHERE  user_id=%(user_id)s
    """, {"user_id": user_id})


def get_categories():
    return connection.execute_select("""
    SELECT *
    FROM categories""")


def get_supermarket_id_by_user_id(user_id):
    return connection.execute_select("""
    SELECT supermarket_id
    FROM supermarket
    WHERE user_id=%(user_id)s
    """, {'user_id': user_id})


def get_cart_products_by_cart_id(cart_id):
    return connection.execute_select("""
        SELECT * FROM cart_products
        JOIN products p on p.product_id = cart_products.product_id
         WHERE cart_id=%(cart_id)s
    """, {"cart_id": cart_id})
