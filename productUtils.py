import dbUtils
import json
from datetime import datetime
from datetime import timezone 

# importing enum for enumerations

CART_STATUS_INACTIVE = 0
CART_STATUS_SHOPPING = 1
CART_STATUS_CHECKEDOUT = 2

PRODUCT_STATUS_INACTIVE = 0
PRODUCT_STATUS_ACTIVE = 1

PRODUCT_BF_MONTHLY = 1

def add_product(id, unit_price,currency, billing_frequency = PRODUCT_BF_MONTHLY, status = PRODUCT_STATUS_ACTIVE):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            #dt = datetime.now()   
            #utc_time = dt.replace(tzinfo = timezone.utc) 
            dt = datetime.now(tz=timezone.utc) 
            #insert into user table
            insert_query = """INSERT INTO products (id, unit_price,currency, billing_frequency, status, created_on) 
                                VALUES 
                                (%s,%s,%s, %s,%s,%s)"""
            
            data_tuple = (id, unit_price, currency, billing_frequency,status,dt)
            cursor.execute(insert_query, data_tuple)

            db_con.commit()
            return (0, "Product added successfully.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("In the exception block.")
        return ( -2, str(e))

def update_product(id, updates):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            #dt = datetime.now()   
            #utc_time = dt.replace(tzinfo = timezone.utc) 
            dt = datetime.now(tz=timezone.utc) 

            updates['updated_on'] = dt

            sql_template = "UPDATE products SET ({}) = %s WHERE id = '{}'"
            sql = sql_template.format(', '.join(updates.keys()), str(id))
            params = (tuple(updates.values()),)
            print ( cursor.mogrify(sql, params))
            cursor.execute(sql, params)
            updated_rows = cursor.rowcount
            
            if updated_rows == 1:
                db_con.commit()
                return (0, "Product updated successfully.")
            else:
                db_con.rollback()
                return (1, "Failed : No product found for the given product ID.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("In the exception block.")
        return ( -2, str(e))
        
def list_products(status=PRODUCT_STATUS_ACTIVE):
    error = ''
    try:
        try:
            db_con = dbUtils.getConnFromPool()
            #cursor = db_con.cursor()
            cursor = dbUtils.getDictCursor(db_con)

            sql = "SELECT * FROM products where status = %s"
            data_tuple = (status,)

            cursor.execute(sql, data_tuple)
            result = cursor.fetchall()

            db_con.commit()
            return (0, "Product list executed successfully.",result)

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("In the exception block.")
        return ( -2, str(e))

def create_cart(cart_id, status = CART_STATUS_SHOPPING):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            dt = datetime.now(tz=timezone.utc) 
            print(dt)
            #utc_time = dt.replace(tzinfo = timezone.utc) 
            #print(utc_time)
            #insert into user table
            insert_query = """INSERT INTO carts (id, status, created_on) 
                                VALUES 
                                (%s,%s,%s)"""
            
            data_tuple = (cart_id,status,dt)
            cursor.execute(insert_query, data_tuple)

            db_con.commit()
            return (0, "Cart created successfully.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("Exception occured in cart creation.")
        return ( -2, str(e))

def add_product_to_cart(cart_id, product_id):

    error = ''
    try:

        try:
            #TODO: ensure product_id is in active state                
            
            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            dt = datetime.now(tz=timezone.utc) 
            print(dt)
            #utc_time = dt.replace(tzinfo = timezone.utc) 
            #print(utc_time)
            #insert into user table
            insert_query = """INSERT INTO cart_products (cart_id, product_id, created_on) 
                                VALUES 
                                (%s,%s,%s)"""
            
            data_tuple = (cart_id,product_id,dt)
            cursor.execute(insert_query, data_tuple)

            db_con.commit()
            return (0, "Product successfully added to Cart.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("Exception occured in adding products to cart.")
        return ( -2, str(e))

def remove_product_from_cart(cart_id, product_id):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            #utc_time = dt.replace(tzinfo = timezone.utc) 
            #print(utc_time)
            #insert into user table
            sql_template = """DELETE FROM cart_products WHERE cart_id = %s and product_id = %s"""
            
            data_tuple = (cart_id,product_id)
            cursor.execute(sql_template, data_tuple)

            db_con.commit()
            return (0, "Product successfully removed from Cart.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("Exception occured while removing product from cart.")
        return ( -2, str(e))

def get_cart_details(cart_id):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = dbUtils.getDictCursor(db_con)
            #cursor = db_con.cursor()

            #utc_time = dt.replace(tzinfo = timezone.utc) 
            #print(utc_time)
            #insert into user table
            sql = """
            select id,unit_price,billing_frequency,currency from products as p
            where p.status = 1 and p.id in ( select product_id from cart_products where cart_id = %s)
            """
            
            data_tuple = (cart_id,)
            
            #print ( cursor.mogrify(sql, data_tuple))
            
            cursor.execute(sql, data_tuple)

            result = cursor.fetchall()

            db_con.commit()
            return (0, "Cart Items details successfully fetched.", result)

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe), None)
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("Exception occured while fetching product details from cart.")
        return ( -2, str(e), None)

def checkout_cart(cart_id):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            dt = datetime.now(tz=timezone.utc) 
            print(dt)
            #utc_time = dt.replace(tzinfo = timezone.utc) 
            #print(utc_time)
            #insert into user table
            sql = """UPDATE carts set status = %s, updated_on = %s where id = %s""" 
            data_tuple = (CART_STATUS_CHECKEDOUT,dt,cart_id)
            cursor.execute(sql, data_tuple)

            db_con.commit()
            return (0, "Cart checkedout successfully.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        #flash(e)
        print ("Exception occured in cart checkout process.")
        return ( -2, str(e))

## main entry point
if __name__ == "__main__":

    """    
    (retCode, msg ) = product_add('Starter', 5,'USD')
    print( retCode)
    print ( msg)

    (retCode, msg ) = product_add('Mini', 10,'USD')
    print( retCode)
    print ( msg)
    
    (retCode, msg ) = product_update('Mini', {'status' : 0, 'unit_price' : 110})
    print( retCode)
    print ( msg)

    (retCode, msg, result ) = product_list()
    print( retCode)
    print (msg)
    print(result)
    #print( json.dumps(result))

    (retCode,msg) = cart_create("NEWCART#3")
    print(retCode)
    print(msg)

    (retCode,msg) = add_product_to_cart("NEWCART#3","Starter")
    print(retCode)
    print(msg)
    """

    (retCode, msg) = checkout_cart("Cart1")
    print( retCode)
    print (msg)


    """    (retCode,msg, results) = get_cart_details("NEWCART#3")
    print(retCode)
    print(msg)
    print(results)
    """
    #(retCode,msg) = remove_product_from_cart("NEWCART#3","Mini")
    #print(retCode)
    #print(msg)

