from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from database import get_connection


# gpt_key = vnsdaifnvdksfvisdfvnmsdkfnvaewi5n645t6n34b34534

class OrderState(TypedDict):
    order_id: int
    product_id: int
    quantity: int
    total_amount: float
    order_status: str
    inventory_status: str
    payment_status: str
    shipment_status: str




def validate_order(state: OrderState):
    connection = get_connection()
    cursor = connection.cursor()

    order = cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (state["order_id"],)
    ).fetchone()
    connection.close()

    if order is None:
        return {"order_status": "INVALID"}

    return {
        "product_id": order["product_id"],
        "quantity": order["quantity"],
        "total_amount": order["total_amount"],
        "order_status": "VALIDATED"
    }

def check_product(state: OrderState):
    connection = get_connection()
    cursor = connection.cursor()

    product = cursor.execute(
        "select * from products where id = ?",
        (state["product_id"],)
    ).fetchone()

    connection.close()
    if product is None:
        return {
            "order_status": "INVALID_PRODUCT"
        }
    return {
        "order_status": "PRODUCT_VALID"
    }


def check_inventry(state : OrderState):
    connection = get_connection()
    cursor = connection.cursor()

    inventory = cursor.execute(
        "select * from inventory where product_id = ?",
        (state["product_id"],)
    ).fetchone()

    connection.close()

    if inventory is None or inventory["quantity"] < state["quantity"]:
        return{
            "inventory_status" : "UNAVAILABLE"
        }
    return {
        "inventory_status" : "AVAILABLE"
    }


def route_after_validation(state: OrderState) -> str:
    if state["order_status"] == "VALIDATED":
        return "VALID"
    return "INVALID"


def route_after_product_check(state : OrderState) -> str:
    if state["order_status"] == "PRODUCT_VALID":
        return "VALID"
    return "INVALID"


#Create State graph
graph = StateGraph(OrderState)

#Register Nodes here
graph.add_node("validate_order", validate_order)
graph.add_node("check_product", check_product)
graph.add_node("check_inventory", check_inventry)


graph.add_edge(START, "validate_order")
graph.add_conditional_edges(
    "validate_order",
    route_after_validation,
    {
        "VALID" : "check_product",
        "INVALID" : END
    }
)
graph.add_conditional_edges(
    "check_product",
    route_after_product_check,
    {
        "VALID" : "check_inventory",
        "INVALID" : END
    }
)

graph.add_edge("check_inventory", END)

app = graph.compile()
