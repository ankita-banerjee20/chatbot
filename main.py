from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import essentials 
import db_helper

app = FastAPI()

inprogress_order_dict = {}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json() # retrive the json file from the request
    


    # extracting necessary info
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = essentials.extract_session_id(output_contexts[0]['name'])




    def add_to_order(parameters, session_id):
        food_items = parameters['food-items']
        food_quantities = parameters['number']

        if len(food_items) != len(food_quantities):
            fulfillment_text = "Specify quantity along with food items properly."
        else:
            food_dict = dict(zip(food_items, food_quantities))
            
            if session_id in inprogress_order_dict:
                temp = inprogress_order_dict[session_id]
                temp.update(food_dict)
                inprogress_order_dict[session_id] = temp
            else:
                inprogress_order_dict[session_id] = food_dict

            order_str = essentials.get_str_from_food_dict(inprogress_order_dict[session_id])
            fulfillment_text = f"So far you have {order_str}. Do you need anything else?"
        
        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text})
    



    def remove_from_order(parameters, session_id):
        if session_id not in inprogress_order_dict:
            fulfillment_text = "Sorry there was a trouble finding your order. Please order again."
        else:
            curr_food_dict = inprogress_order_dict[session_id]
            remove_item = parameters['food-items']

            removed_items = []
            not_found = []

            for item in remove_item:
                if item in curr_food_dict:
                    removed_items.append(item)
                    del curr_food_dict[item]
                else:
                    not_found.append(item)

            if len(removed_items) > 0:
                fulfillment_text = "Removed " + ", ".join(removed_items) + "from your order." 
            
            if len(not_found) > 0:
                fulfillment_text = "Could not find " + ", ".join(not_found) + "in your order."

            if len(curr_food_dict) == 0:
                fulfillment_text = "Your order is empty!"

        return JSONResponse(content={
            'fulfillmentText': fulfillment_text
        })



    def complete_order(parameters, session_id):
        if session_id not in inprogress_order_dict:
            fulfillment_text = "Sorry having trouble finding your order. Please order again."
        else:
            food_dict = inprogress_order_dict[session_id]
            order_id = db_helper.save_to_db(food_dict)

            if order_id == -1:
                fulfillment_text = "Sorry there was a trouble processing your order"
            else:
                order_total = db_helper.get_total_order_price(order_id)
                fulfillment_text = f"Successfully placed your order with order id {order_id} and total amount is {order_total}"
        
        del inprogress_order_dict[session_id]
        
        return JSONResponse(content={
            'fulfillmentText': fulfillment_text
        })


        
    def track_order(parameters, session_id):
        order_id = parameters['number']
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            fulfillment_text = f"The order status for order id: {order_id} is {order_status}"
        else:
            fulfillment_text = f"No order found for order id: {order_id}"

        return JSONResponse(content={
            'fulfillmentText': fulfillment_text
        })
    
   

    intent_handler_dict = {
        'order.add-context:ongoing-order' : add_to_order,
        'order.remove-context:ongoing-order' : remove_from_order,
        'order.complete-context:ongoing-order' : complete_order,
        'track.order-context:ongoing-tracking' : track_order
    }

    return intent_handler_dict[intent](parameters, session_id)







