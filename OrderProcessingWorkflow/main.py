from typing import TypedDict
import sqlite3


class OrderState(TypedDict):
    order_id : int
    product_id : int
    quantity: int
    total_amount: float
    order_status: str



def validate_order(state : OrderState):
    connection = sqlite3.connect("order_processing.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    order = cursor.execute(
        """
        select * from orders where id = ?         
        """, 
        (state["order_id"], )
    ).fetchone()
    connection.close()

    if order is None:
        return {
            "order_status" : "INVALID"
        }
    return {
        "order_id" : order["id"],
        "product_id" : order["product_id"],
        "quantity" : order["quantity"],
        "total_amount" : order["total_amount"],
        "order_status" : "VALID"
    }



state = {
    "order_id": 4
}

result = validate_order(state)
print(result)