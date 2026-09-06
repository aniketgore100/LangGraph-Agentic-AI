from OPWF_LangGraph import app


result = app.invoke({"order_id": 3})
print("Existing order:", result)

result = app.invoke({"order_id": 99})
print("Non-existent order:", result)
