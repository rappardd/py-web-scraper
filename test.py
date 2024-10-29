import json

# 1. load the json file
# 2. parse the json data to access the structure
# 3. retrieve the array from the json object
# 4. check if the number is in the array
# 5. if it is, return a message saying it is already in the array
# 6. if it is not, add it to the array and return a message saying it has been added

# Data to write to JSON file
my_array = [1, 2, 3, 4, 5]

# Write data to JSON file
def write_json_file(file_path, data):
    # if number is already in the array, don't write it
    if data in read_json_file(file_path):
        return (f"{data} is already in the array")
    else:
        with open(file_path, "w") as file:
            json.dump(data, file)
        return (f"{data} has been added to the array")

# Read data from JSON file
def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def check_if_in_array(filename, number_to_check):
    with open(filename, 'r') as file:
        data = json.load(file)

    array = data.get("episodes", [])

    if number_to_check in array:
        return (f"{number_to_check} is already in the array")
    else:
        return (f"{number_to_check} is not in the array")


print(check_if_in_array("my_data.json", 3))
