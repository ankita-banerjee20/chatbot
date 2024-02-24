import mysql.connector
global cnx 

cnx = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'root',
    database = 'fairy_eatery'
)

def get_order_status(order_id):
    # Cursor object
    cursor = cnx.cursor()

    # Query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Executing the query
    cursor.execute(query, (order_id,))

    # Fetching the query
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()

    if result is not None:
        return result[0]
    else:
        return None
    


def generate_order_id():
    cursor = cnx.cursor()

    query = ("SELECT MAX(order_id) FROM orders")

    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    if result is not None:
        return result + 1
    else:
        return 1



def insert_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        cnx.commit()

        cursor.close()

        return 1
    
    except mysql.connector.Error as err:
        print(err)
        return -1
    
    except Exception as e:
        print(e)
        return -1



def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    query = f"INSERT INTO order_tracking (order_id, status) VALUES(%s, %s)"

    cursor.execute(query, (order_id, status))

    cnx.commit()

    cursor.close()



def save_to_db(food_dict):
    order_id = generate_order_id()

    for food_item, quantity in food_dict.items():
        flag = insert_item(food_item, quantity, order_id)

        if flag == -1:
            return -1
    
    insert_order_tracking(order_id, 'in progress')
    
    return order_id



def get_total_order_price(order_id):
    cursor = cnx.cursor()

    query = f"SELECT get_total_order_price({order_id})"

    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    return result



    