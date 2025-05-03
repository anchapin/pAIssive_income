from api.utils.query_params import FilterOperator, QueryParams, apply_filtering

# Test data
items = [
    {"id": 1, "name": "Item 1", "price": 10.5, "active": True, "tags": ["a", "b"]},
    {"id": 2, "name": "Item 2", "price": 20.0, "active": False, "tags": ["b", "c"]},
    {"id": 3, "name": "Test 3", "price": 15.0, "active": True, "tags": ["a", "c"]},
    {"id": 4, "name": "Test 4", "price": 25.5, "active": True, "tags": ["d"]},
    {"id": 5, "name": "Item 5", "price": 5.0, "active": False, "tags": ["a", "b", "c"]}
]

# Create query params
params = QueryParams(
    filters={"name": "Item", "price": 10.0},
    filter_operators={"name": FilterOperator.STARTS_WITH, "price": FilterOperator.GT}
)

# Apply filtering
filtered = apply_filtering(items, params)

# Print results
print('Filtered items:')
for item in filtered:
    print(f'ID: {item["id"]}, Name: {item["name"]}, Price: {item["price"]}')

# Manual check
print('\nManual check:')
for item in items:
    if item["name"].startswith("Item") and item["price"] > 10.0:
        print(f'ID: {item["id"]}, Name: {item["name"]}, Price: {item["price"]}')
