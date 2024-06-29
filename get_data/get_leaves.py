import json
def get_categories_from_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)         
            return data
    except Exception as e:
        print(e)
        return None

def write_to_file(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file)
        return True
    except Exception as e:
        print(e)
        return None
leaves = []
def recursive_extract(d):
        if 'children' in d:
            for child in d['children']:
                recursive_extract(child)
        else:
             leaves.append(d['name'])
             

categories = get_categories_from_file('filtered_categories.json')
recursive_extract(categories)
print(write_to_file('leave_categories.json', leaves))

