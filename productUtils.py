import dbUtils
import json
from datetime import datetime
from datetime import timezone 

# importing enum for enumerations
import enum
  
# creating enumerations using class
class ProductStatus(enum.Enum):
    inactive = 0
    active = 1

def product_add(id, unit_price,currency, billing_frequency = 1, status = 1):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            dt = datetime.now() 
  
            utc_time = dt.replace(tzinfo = timezone.utc) 

            #insert into user table
            insert_query = """INSERT INTO products (id, unit_price,currency, billing_frequency, status, created_on) 
                                VALUES 
                                (%s,%s,%s, %s,%s,%s)"""
            
            data_tuple = (id, unit_price, currency, billing_frequency,status,utc_time)
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

def product_update(id, updates):

    error = ''
    try:

        try:

            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            dt = datetime.now()   
            utc_time = dt.replace(tzinfo = timezone.utc) 

            updates['updated_on'] = utc_time

            sql_template = "UPDATE products SET ({}) = %s WHERE id = '{}'"
            sql = sql_template.format(', '.join(updates.keys()), str(id))
            params = (tuple(updates.values()),)
            print ( cursor.mogrify(sql, params))
            cursor.execute(sql, params)

            db_con.commit()
            return (0, "Product updated successfully.")

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
        
def product_list(status=1):
    error = ''
    try:
        try:
            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            sql = "SELECT * FROM products"
            cursor.execute(sql)
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


## main entry point
if __name__ == "__main__":

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