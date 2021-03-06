import mysql.connector
from mysql.connector import Error
import connect_to_db
import query
import form2query
import dataDict
from flask import Flask, render_template, request 

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/views", methods = ['GET', 'POST'])
def views():
    if request.method == 'GET':
        return render_template("views.html", data = None)

    if request.method == 'POST':
        selected_view = request.form.get("select_view")
        selected_data = query.get_table("SELECT * FROM {}".format(selected_view))
        headers = query.get_one_col("DESCRIBE {}".format(selected_view))
        return render_template("presentation.html", data = [headers, selected_data])

@app.route("/modify-tables", methods = ['GET', 'POST'])
def modify():

    '''
        The "modify" form has 6 steps:
        - "zero" : Initial form state. User selects the desired table and action (frontend)
        - "one"  : User has selected table and action (backend)
        - "two"  : User inserts required data depending on selected table and action (frontend)
        - "three": For "insert" action new data is inserted to the database
                   For "modify" and "delete" search according to form data
        - "four" : For "modify" user changes old data on the form
                   For "delete" user verifies deletion
        - "five" : Modify or delete database entry (backend)
        - "done: : Action completed successfully (frontend prints "done" message)
        - "error": An error occured (frontend prints error message)
    '''
    
    data_dict = {}

    if request.method == 'GET':
        return render_template("modify_tables.html", data = None, step = 'zero')

    if request.method == 'POST':
       
        selected_table = request.form.get("select_table")
        selected_action = request.form.get("select_action")
        step = request.form.get("form_step")
 
        if not selected_table or not selected_action:
            return render_template("modify_tables.html", data = None, step = 'zero')
        else:
            data_dict['table'] = selected_table
            data_dict['action'] = selected_action
 
        if step == 'one':
            return render_template("modify_tables.html", data = data_dict, step = 'two')

        elif step == 'three':

            if selected_action == 'insert':
                
                if selected_table == 'Customer':
                    new_data = dataDict.Customer_data
                elif selected_table == 'Product':
                    new_data = dataDict.Product_data
                elif selected_table == 'Store':     
                    new_data = dataDict.Store_data 

                query_arr = form2query.insert(new_data, selected_table)
                for q in query_arr:
                    print(q)

                error = query.execute_and_commit(query_arr)
                if error == None:
                    return render_template("modify_tables.html", data = data_dict, step = 'done')
                else:
                    data_dict['error'] = error
                    return render_template("modify_tables.html", data = data_dict, step = 'error')

            elif selected_action in ['modify', 'delete']:
                
                if selected_table == 'Customer':
                    
                    selected_card = request.form.get("insert_card")
                    selected_name = request.form.get("insert_name")

                    if selected_card != "":
                        data_dict['card_id'] = selected_card
                        selected_name = query.get_one_col("SELECT customer_name FROM Customer WHERE card_id = {}".format(selected_card))
                        if not selected_name:
                            data_dict['customer_name'] = None
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                        else:
                            data_dict['customer_name'] = selected_name[0]
                            selected_name = data_dict['customer_name']

                    elif selected_name != "":
                        data_dict['customer_name'] = selected_name
                        selected_card = query.get_one_col("SELECT card_id FROM Customer WHERE customer_name = '{}'".format(selected_name))
                        if not selected_card:
                            data_dict['card_id'] = None
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                        else:
                            data_dict['card_id'] = selected_card[0]
                            selected_card = data_dict['card_id']

                    else:
                        return render_template("modify_tables.html", data = data_dict, step = 'two')

                    for d in dataDict.Customer_data.keys():
                        data_dict[d] = query.get_one_col("SELECT {} FROM Customer WHERE card_id = {}".format(d, selected_card))[0]
           
                    return render_template("modify_tables.html", data = data_dict, step = 'four') 

                elif selected_table == 'Product':

                    selected_barcode = request.form.get("insert_barcode")
                    if selected_barcode != "":
                        data_dict['barcode'] = selected_barcode
                        selected_product_name = query.get_table("SELECT product_name FROM Product WHERE barcode = {}".format(selected_barcode))
                        if not selected_product_name:
                            data_dict['product_name'] = None
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                        else:
                            for d in dataDict.Product_data.keys():
                                data_dict[d] = query.get_one_col("SELECT {} FROM Product WHERE barcode = {}".format(d, selected_barcode))[0]
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                    else:
                        return render_template("modify_tables.html", data = data_dict, step = 'two')

                elif selected_table == 'Store':
                    selected_store = request.form.get("insert_store_id")
                    if selected_store != "":
                        data_dict['store_id'] = selected_store
                        selected_store_name = query.get_one_col("SELECT store_name FROM Store WHERE store_id = {}".format(selected_store))
                        if not selected_store_name:
                            data_dict['store_name'] = None
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                        else:
                            data_dict['store_name'] = selected_store_name[0]
                            store_data = ['area','opening_hours','street_name','street_number','city','postal_code']
                            for d in store_data:
                                data_dict[d] = query.get_one_col("SELECT {} FROM Store WHERE store_id = {}".format(d, selected_store))[0]
                            return render_template("modify_tables.html", data = data_dict, step = 'four')
                    else:
                        return render_template("modify_templates.html", data = data_dict, step = 'two')

        elif step == 'five':

            if selected_action == 'modify':
                if selected_table == 'Customer':
                    new_data = dataDict.Customer_data
                elif selected_table == 'Product':
                    new_data = dataDict.Product_data
                elif selected_table == 'Store':
                   new_data = dataDict.Store_data

                query_arr = form2query.update(new_data, selected_table)
           
            elif selected_action == 'delete':
                query_arr = form2query.delete(selected_table)

            for q in query_arr:
                print(q)

            error = query.execute_and_commit(query_arr)
            if error == None:
                return render_template("modify_tables.html", data = data_dict, step = 'done')
            else:
                data_dict['error'] = error
                return render_template("modify_tables.html", data = data_dict, step = 'error')

        return render_template("modify_tables.html", data = None, step = 'zero')

@app.route("/price-history", methods = ['GET', 'POST'])
def price_history():

    if request.method == 'GET':
        return render_template("price_history.html", data = None)

    if request.method == 'POST':
       
        selected_barcode = request.form.get("insert_barcode")
        if selected_barcode == "":
           return render_template("price_history.html", data = None)

        data_dict = {}
        data_dict['barcode'] = selected_barcode
        description = query.get_one_col("SELECT product_name FROM Product WHERE barcode = {}".format(selected_barcode))         
        if not description:
            data_dict['description'] = None
        else:
            data_dict['description'] = description[0]

        data_dict['headers'] = ['start date', 'end date', 'amount']
        data_dict['values'] = query.get_table("SELECT DATE(start_date), DATE(end_date), amount " +
                                              "FROM Price " +
                                              "WHERE barcode = {}".format(selected_barcode))

        return render_template("price_history.html", barcode = selected_barcode, data = data_dict)

@app.route("/shopping-stats", methods = ['GET', 'POST'])
def shopping_stats():

    '''
        Available metrics:
        - 'fav_pairs': Pairs of products usually bought together (eg cheese and ham)
        - 'fav_spot': The most popular shelves in the supermarket
        - 'label_pop': Popularity of supermarket-manufactured products per category
        - 'fav_hour': Distribution of transactions per opening hour
        - 'area': Average transaction amount per customer's postal code
        - 'pet_amount': Average transaction amount per pet ownership

        The form has 3 steps:
        - step "zero" : User selects one of the available metrics (frontend)
        - step "one"  : Query the database and return results (backend)
        - step "two"  : Present the results or ask for more data based on previous query (frontend)
        - step "three": Query the database again (not needed for all metrics - backend) 
        - step "four" : Present the results (not needed for all metrics - frontend)
    '''

    if request.method == 'GET':
       return render_template("shopping_stats.html", metric = None, data = None, step = 'zero')

    if request.method == 'POST':

       selected_metric = request.form.get("select_metric")
       step = request.form.get("form_step")
       data_dict = {}

       if selected_metric == None:
           return render_template("shopping_stats.html", metric = None, data = None, step = 'zero')
       
       if selected_metric == 'fav_pairs':
           headers_arr = ['Barcode 1', 'Product name 1', 'Barcode 2', 'Product name 2', 'Pair frequency']
           query_str = ("WITH buy_products_names(barcode, name, transaction_id) AS " +
                        "(SELECT P.barcode, P.product_name, B.transaction_id FROM buy_products AS B NATURAL JOIN Product AS P) " +
                        "SELECT B1.barcode, B1.name, B2.barcode, B2.name, COUNT(*) AS pair_freq " +
                        "FROM buy_products_names AS B1, buy_products_names AS B2 " +
                        "WHERE B1.transaction_id = B2.transaction_id and B1.barcode < B2.barcode " +
                        "GROUP BY B1.barcode, B2.barcode " +
                        "ORDER BY pair_freq DESC " +
                        "LIMIT 10")

       if selected_metric == 'fav_spot':

           if step == 'one':
               store_names = query.get_table("SELECT store_id, store_name FROM Store")
               return render_template("shopping_stats.html", metric = selected_metric, data = store_names, step = 'two')

           else:     
               selected_store = request.form.get("select_store")
               if selected_store == None:
                   store_names = query.get_table("SELECT store_id, store_name FROM Store")
                   return render_template("shopping_stats.html", metric = selected_metric, data = store_names, step = 'two')
               data_dict['store'] = query.get_one_col("SELECT store_name FROM Store WHERE store_id = {}".format(selected_store))[0]

               headers_arr = ['Store_id', 'Aisle', 'Shelf', 'Shelf share']
               query_str = ("SELECT O.store_id, O.aisle, O.shelf, SUM(B.quantity) * 100.0 / SUM(SUM(B.quantity)) OVER(PARTITION BY O.store_id) AS shelf_share " +
                            "FROM offers_products as O, buy_products as B, Transaction as T " +
                            "WHERE O.barcode = B.barcode AND T.transaction_id = B.transaction_id AND O.store_id = T.store_id AND O.store_id = {} ".format(selected_store) +
                            "GROUP BY O.store_id, O.aisle, O.shelf " +
                            "ORDER BY O.store_id, O.aisle, O.shelf")

 
       if selected_metric == 'label_pop':
           headers_arr = ['Category', 'is_label', 'Percentage']
           query_str = ("SELECT P.category_id, P.label, SUM(B.quantity) * 100.0 / SUM(SUM(B.quantity)) OVER(PARTITION BY category_id) AS label_share " +
                        "FROM Product as P INNER JOIN buy_products as B ON P.barcode = B.barcode " +
                        "GROUP BY P.category_id, P.label " +
                        "ORDER BY P.category_id, P.label")

       if selected_metric == 'fav_hour':

           if step == 'one':
               store_names = query.get_table("SELECT store_id, store_name FROM Store")
               return render_template("shopping_stats.html", metric = selected_metric, data = store_names, step = 'two')

           else:    
               selected_store = request.form.get("select_store")
               if selected_store == None:
                   store_names = query.get_table("SELECT store_id, store_name FROM Store")
                   return render_template("shopping_stats.html", metric = selected_metric, data = store_names, step = 'two')
               data_dict['store'] = query.get_one_col("SELECT store_name FROM Store WHERE store_id = {}".format(selected_store))[0]

               headers_arr = ['Store_id', 'Hour', 'Share']
               query_str = ("SELECT store_id, HOUR(timestamp) AS shop_time, " + 
                            "SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER(PARTITION BY store_id) AS amount_per_hour " +
                            "FROM Transaction " +
                            "WHERE store_id = {} ".format(selected_store) +
                            "GROUP BY store_id, shop_time " +
                            "ORDER BY store_id, shop_time")

               data_dict['age_hour'] = {}
               data_dict['age_hour']['headers'] = ['Age', 'Hour', 'Share']
               data_dict['age_hour']['values'] = query.get_table("SELECT FLOOR(YEAR(C.date_of_birth)/10)*10 AS age, HOUR(T.Timestamp) as shop_time, " + 
                                                                 "COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY FLOOR(YEAR(C.date_of_birth)/10)*10) as share " +
                                                                 "FROM Transaction AS T INNER JOIN Customer AS C ON T.card_id = C.card_id " +
                                                                 "WHERE store_id = {} ".format(selected_store) +
                                                                 "GROUP BY age, shop_time " +
                                                                 "ORDER BY age, shop_time")

       if selected_metric == 'area':
           headers_arr = ['Postal code', 'Average amount']
           query_str = ("SELECT C.postal_code, AVG(T.total_amount) AS amount_per_area " + 
                        "FROM Transaction AS T NATURAL JOIN Customer AS C " +
                        "GROUP BY C.postal_code " +
                        "ORDER BY C.postal_code")

       if selected_metric == 'pet_amount':
           headers_arr = ['Pet','Average amount']
           query_str = ("SELECT DISTINCT C.pet, AVG(T.total_amount) OVER (PARTITION BY C.pet) AS amount_per_pet " +
                        "FROM Transaction as T NATURAL JOIN Customer AS C")

       print(query_str)
       data_dict[selected_metric] = {}
       data_dict[selected_metric]['headers'] = headers_arr
       data_dict[selected_metric]['values'] = query.get_table(query_str)
       return render_template("shopping_stats.html", metric = selected_metric, data = data_dict)

@app.route("/customer-stats", methods = ['GET', 'POST'])
def customer_stats():

    '''
        Returns statistics about a customer's shopping behaviour
        Searching for a specific customer is done by card ID or customer name
        The following metrics are calculated:
        - Most frequently bought products
        - Stores the customer shops from
        - Distribution of money spent against opening hours
        - Total amount spent per week and month 
    '''

    customer_dict = {}
    data_dict = {}

    if request.method == 'GET':
        return render_template("customer_stats.html", customer = None, data = None)

    if request.method == 'POST':
        selected_card = request.form.get("insert_card")
        selected_name = request.form.get("insert_name")

        if selected_card != "":
            customer_dict['card_id'] = selected_card
            selected_name = query.get_one_col("SELECT customer_name FROM Customer WHERE card_id = {}".format(selected_card))
            if not selected_name:
                customer_dict['customer_name'] = None
                return render_template("customer_stats.html", customer = customer_dict, data = None)
            else:
                customer_dict['customer_name'] = selected_name[0]
                selected_name = customer_dict['customer_name']	

        elif selected_name != "":
            customer_dict['customer_name'] = selected_name
            selected_card = query.get_one_col("SELECT card_id FROM Customer WHERE customer_name = '{}'".format(selected_name))
            if not selected_card:
                customer_dict['card_id'] = None
                return render_template("customer_stats.html", customer = customer_dict, data = None)
            else:
                customer_dict['card_id'] = selected_card[0]
                selected_card = customer_dict['card_id']

        else:
            return render_template("customer_stats.html", customer = None, data = None)         

        query_str = ("SELECT P.barcode, P.product_name, sum(B.quantity) AS total_quantity " +
                     "FROM buy_products AS B INNER JOIN Product AS P ON B.barcode = P.barcode " +
                     "AND B.transaction_id IN (SELECT transaction_id FROM Transaction WHERE card_id = {}) ".format(selected_card) +
                     "GROUP BY P.barcode " +
                     "ORDER BY total_quantity DESC " +
                     "LIMIT 10")
        print(query_str)
        top10_products = query.get_table(query_str)

        query_str = ("SELECT DISTINCT T.store_id, S.store_name " +
                     "FROM Transaction AS T INNER JOIN Store AS S ON T.store_id = S.store_id AND T.card_id = {} ".format(selected_card) +
                     "ORDER BY store_id")
        print(query_str)
        visited_stores = query.get_table(query_str)

        query_str = ("SELECT SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER () AS share_per_dt, HOUR(timestamp) AS dt " +
                     "FROM Transaction " +
                     "WHERE card_id = {} ".format(selected_card) +
                     "GROUP BY dt " +
                     "ORDER BY dt")
        print(query_str)
        hours_share = query.get_table(query_str)

        query_str = ("SELECT YEAR(timestamp) AS t_year, WEEK(timestamp) AS t_week, SUM(total_amount) AS week_total " +
                     "FROM Transaction " +
                     "WHERE card_id = {} ".format(selected_card) +
                     "GROUP BY t_year, t_week " +
                     "ORDER BY t_year, t_week")
        print(query_str)
        week_average = query.get_table(query_str)

        query_str = ("SELECT YEAR(timestamp) AS t_year, MONTH(timestamp) AS t_month, SUM(total_amount) AS month_total " +
                     "FROM Transaction " +
                     "WHERE card_id = {} ".format(selected_card) +
                     "GROUP BY t_year, t_month " +
                     "ORDER BY t_year, t_month")
        print(query_str)
        month_average = query.get_table(query_str)

        if not visited_stores:
            return render_template("customer_stats.html", customer = customer_dict, data = None)

        data_dict['fav_prod'] = {}
        data_dict['fav_prod']['table'] = top10_products
        data_dict['fav_prod']['headers'] = ['barcode', 'product name', 'total quantity']

        data_dict['stores'] = {}
        data_dict['stores']['table'] = visited_stores
        data_dict['stores']['headers'] = ['store ID', 'Store name']

        data_dict['week_avg'] = {}
        data_dict['week_avg']['table'] = week_average
        data_dict['week_avg']['headers'] = ['year', 'week', 'Week total']

        data_dict['month_avg'] = {}
        data_dict['month_avg']['table'] = month_average
        data_dict['month_avg']['headers'] = ['year', 'month', 'month total'] 

        data_dict['fav_hour'] = {}
        data_dict['fav_hour']['table'] = hours_share
        data_dict['fav_hour']['headers'] = ['share', 'hour']

        return render_template("customer_stats.html", customer = customer_dict, data = data_dict)

@app.route("/select", methods = ['GET', 'POST'])
def select():

    # Select a table to present and apply filters to data

    filters_dict = {}
    filters_dict['tables'] = ['Product', 'Store', 'Customer', 'Transaction']
    if request.method == 'GET':
        filters_dict['selected_table'] = ""
        return render_template("select.html", filters = filters_dict)
    if request.method == 'POST':
        filters_dict['selected_table'] = request.form.get("select_table")
        filters_dict['store_names'] = query.get_one_col("SELECT store_name from Store")
        filters_dict['category_names'] = query.get_one_col("SELECT category_name from Category")
        return render_template("select.html", filters = filters_dict)

@app.route("/presentation", methods = ['POST'])
def present():

    # Presentation of a database table
    # This function is responsible for reading a HTML form with filters (according to selected table),
    # querying the database, and presenting the results as a table

    if request.method == 'POST':
        selected_table = request.form.get("select_table")

        if selected_table == "Transaction":
            selected_store = request.form.get("select_store")
            selected_payment = request.form.get("payment_method")
            selected_min_date = request.form.get("min_date")
            selected_max_date = request.form.get("max_date")
            selected_tid = request.form.get("transaction_id")
            selected_min_quantity = request.form.get("min_quantity")
            selected_max_quantity = request.form.get("max_quantity")
            selected_min_price = request.form.get("min_price")
            selected_max_price = request.form.get("max_price")

            if selected_tid != "":
                query_str = "SELECT * FROM Transaction WHERE transaction_id = {}".format(selected_tid)
            else:
                query_arr = ["SELECT * FROM Transaction"]
                if selected_store != None:
                    query_arr.append("store_id = (SELECT store_id FROM Store WHERE store_name = '{}')".format(selected_store))
                if selected_payment != None:
                    query_arr.append("payment_method = '{}'".format(selected_payment))
                if selected_min_quantity != "":
                    query_arr.append("total_pieces >= {}".format(selected_min_quantity))
                if selected_max_quantity != "":
                    query_arr.append("total_pieces <= {}".format(selected_max_quantity))
                if selected_min_price != "":
                    query_arr.append("total_amount > {}".format(selected_min_price))
                if selected_max_price != "":
                    query_arr.append("total_amount < {}".format(selected_max_price))
                if selected_min_date != "" and selected_max_date != "":
                    query_arr.append("timestamp BETWEEN '{}' AND '{}'".format(selected_min_date, selected_max_date))
                elif selected_min_date != "":
                    query_arr.append("timestamp like '{}%'".format(selected_min_date))
                elif selected_max_date != "":
                    query_arr.append("timestamp like '{}%'".format(selected_max_date))

                if len(query_arr) > 1:
                    query_str = query_arr[0] + " WHERE "
                    for q in query_arr[1:-1]:
                        query_str += q + " AND "
                    query_str += query_arr[-1]
                else:
                    query_str = "SELECT * FROM Transaction LIMIT 100"

            print(query_str)
            selected_data = query.get_table(query_str)
            headers = query.get_one_col("DESCRIBE Transaction")
            return render_template("presentation.html", data = [headers, selected_data])

        elif selected_table == "Product":
            selected_category = request.form.get("select_category")
            selected_barcode = request.form.get("barcode")
            if selected_barcode != "":
                query_str = "SELECT * FROM Product WHERE barcode = {}".format(selected_barcode)
            elif selected_category != None:
                query_str = "SELECT * FROM Product WHERE category_id = (SELECT category_id FROM Category WHERE category_name = '{}')".format(selected_category)
            else:
                query_str = "SELECT * FROM Product"

            print(query_str)
            selected_data = query.get_table(query_str)
            headers = query.get_one_col("DESCRIBE Product")
            return render_template("presentation.html", data = [headers, selected_data])

        elif selected_table == "Customer":
            selected_card = request.form.get("card_id")
            selected_reg_date = request.form.get("reg_date")
            selected_pet = request.form.get("select_pet")
            selected_city = request.form.get("select_city")
            if selected_card != "":
                query_str = "SELECT * FROM Customer WHERE card_id = {}".format(selected_card)
            else:
                query_arr = ["SELECT * FROM Customer"]
                if selected_pet != None:
                    query_arr.append("pet = '{}'".format(selected_pet)) 
                if selected_reg_date != "":
                    query_arr.append("reg_date = '{}'".format(str(selected_reg_date))) 
                if selected_city != None:
                    query_arr.append("city = '{}'".format(selected_city))

                if len(query_arr) > 1:
                    query_str = query_arr[0] + " WHERE "
                    for q in query_arr[1:-1]:
                        query_str += q + " AND "
                    query_str += query_arr[-1]
                else:
                    query_str = "SELECT * FROM Customer LIMIT 100"

            print(query_str)
            selected_data = query.get_table(query_str)
            headers = query.get_one_col("DESCRIBE Customer")
            return render_template("presentation.html", data = [headers, selected_data])

        else:
            selected_store = request.form.get("select_store")
            selected_city = request.form.get("select_city")
            if selected_store != None:
                query_str = "SELECT * FROM Store WHERE store_name = '{}'".format(selected_store)
            elif selected_city != None:
                query_str = "SELECT * FROM Store WHERE city = '{}'".format(selected_city)
            else:
                query_str = "SELECT * FROM Store"

            print(query_str)
            selected_data = query.get_table(query_str)
            headers = query.get_one_col("DESCRIBE Store")
            return render_template("presentation.html", data = [headers, selected_data])


if __name__ == "__main__":
   app.run(host='0.0.0.0')
