from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from database import get_connection


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
    print("product :: ", product)
    if product is None:
        return {
            "order_status": "INVALID_PRODUCT"
        }

    print("product ::", product["name"], product["price"])

    return {
        "order_status": "PRODUCT_VALID"
    }




def route_after_validation(state: OrderState) -> str:
    if state["order_status"] == "VALIDATED":
        return "VALID"
    return "INVALID"



graph = StateGraph(OrderState)
graph.add_node("validate_order", validate_order)
graph.add_node("check_product", check_product)


graph.add_edge(START, "validate_order")
graph.add_conditional_edges(
    "validate_order",
    route_after_validation,
    {
        "VALID" : "check_product",
        "INVALID" : END
    }
)
graph.add_edge("check_product", END)

app = graph.compile()
