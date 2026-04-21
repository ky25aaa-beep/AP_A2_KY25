import json # for json handling
import os # for exiting the program
import random # for the random drink selection
import sys # for interpretting parameters from the main program when executing orders
import keyboard # for grabbing the keyboard shortcut for logging out
from main import load_json_file, logout_staff #import logout function from main 

#json to dict of item_no -> item, and list of drinks
def load_menu(path): # defines a program for loading the menu 
    with open(path, 'r') as f:
        menu = json.load(f) # returns a dictionary or list. 
    foodstuffs = {} # foodstuffs dictionary  
    drinks = {} # drinks dictionary
    # flatten menu into item_no -> item dict 
    if 'foodstuffs' in menu:
        for category, list in menu['foodstuffs'].items():
            for item in list:
                item_copy = item.copy()
                item_copy['category'] = category
                foodstuffs[item['item_no']] = item_copy

    if 'drinks' in menu:
        for drink_category, list in menu['drinks'].items():
            for item in list:
                item_copy = item.copy()
                item_copy['category'] = 'drink'
                item_copy['drink_type'] = drink_category
                drinks[item['item_no']] = item_copy

    return menu, foodstuffs, drinks



def print_menu(menu):
    print('\nMenu:')
    if 'foodstuffs' in menu:
        for section in ['pizzas', 'sides']:
            if section in menu['foodstuffs']:
                print(f"\n{section.capitalize()}:")
                for item in menu['foodstuffs'][section]:
                    print(f"    {item['item_no']}: {item['name']} - {item['description']} (£ {item['price']:.2f})")
    if 'drinks' in menu:
        print('\nDrinks:')
        for drinkcategory, list in menu['drinks'].items():
            print(f"  {drinkcategory.capitalize()}:")
            for item in list:
                print(f"    {item['item_no']}: {item['name']} - {item['description']} (£ {item['price']:.2f})")


def input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val is not None and max_val is not None and not (min_val <= val <= max_val):                
                print(f"Enter a number between {min_val} and {max_val}.")
                continue
            if min_val is not None and val < min_val:
                print(f"Enter a number >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Enter a number <= {max_val}.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")



def get_order_for_person(person_no, items):
    print(f"\nEntering order for Person {person_no}.")
    print("Enter item numbers separated by commas (e.g. 1,4,7). Enter blank when done.")
    order = []
    while True:
        raw = input("Items: ").strip()
        if raw == '':
            break
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        for p in parts:
            if not p.isdigit():
                print(f"'{p}' is not a valid item number.")
                continue
            number = int(p)
            if number not in items:
                print(f"Item number {number} not found.")
                continue
            order.append(number)
        print(f"Current items: {order}. Add more or press Enter to finish.")
    return order


def order_has_drink(order, items):
    for number in order:
        item = items.get(number)
        if item and (item.get('category') == 'drink' or item.get('drink_type')):
            return True
    return False


def suggest_drink(drinks):
    return random.choice(list(drinks.values())) if drinks else None

def get_server_name(staff_id):
    #using credentials.json and the known staff id get the server name 
    credentials = load_json_file('credentials.json', [])
    for credential in credentials:
        if credential.get('staff_id') == staff_id:
            global server_name
            server_name = credential.get('name')
            return server_name
    return "Unknown Server"


def print_receipt(table_no, all_orders, items):
    server_name = get_server_name(staff_id)
    print('\n' + '-' * 54)
    print('------- The Spectra Pizzeria -------')
    print(f'Table {table_no}')
    print('-' * 54)
    total_table = 0.0
    for idx, order in enumerate(all_orders, start=1):
        print(f"Person {idx} Price")
        total = 0.0
        if not order:
            print(' No items ordered')
        for number in order:
            it = items.get(number)
            if it:
                print(f"    {it['name']} £ {it['price']:.2f}")
                total += float(it['price'])
        print(f"Total £ {total:.2f}\n")
        total_table += total
    print(f"Total for the table: £ {total_table:.2f}")
    print(f"Your server is: {server_name}")
    print('Enjoy your meal! Remember to recommend us to friends and family.')


def main():
    try:
        menu, foodstuffs, drinks = load_menu('menu.json')
        all_items = {**foodstuffs, **drinks}
    except FileNotFoundError:
        print('menu.json not found in current directory.')
        sys.exit(1)

    print('Welcome to The Spectra Pizzeria!')
    while True: #loop until valid table number and confirmation
        table_no = input_int('Enter table number (tables open today: 1-143): ', min_val=1, max_val=143)
        confirm = input(f"You entered table number {table_no}. Is this correct? (yes/no): ").strip().lower()
        if confirm in ('yes', 'y'):
            break
        else:
            print("Let's try again.")
        

        
    num_people = input_int('Enter number of people at the table: ', min_val=1)

    print_menu(menu)

    all_orders = []
    for p in range(1, num_people + 1):
        order = get_order_for_person(p, all_items)
        if not order:
            print('No items added. You can still add suggestions.')
        if not order_has_drink(order, all_items):
            suggestion = suggest_drink(drinks)
            if suggestion:
                ans = input(f"Suggest drink: {suggestion['name']} (£ {suggestion['price']:.2f}). Add to order? (yes/no): ").strip().lower()
                if ans in ('yes', 'y'):
                    order.append(suggestion['item_no'])
        all_orders.append(order)

    print_receipt(table_no, all_orders, all_items)
#logout staff when order.py eits also interpret ctrl+x as logout
def exit_handler():
    print("\nLogging out...")
    logout_staff(staff_id)
    print("Logged out successfully. Goodbye!")
    os._exit(0)


if __name__ == '__main__':
    #get staff id from cmd args, if not provided, exit with error
    if len(sys.argv) < 2:
        print("Staff ID not provided. Usage: python order.py <staff_id>")
        sys.exit(1)
    print("Logout at any time by typing 'pressing ctrl+x or closing the window'.")
    keyboard.add_hotkey('ctrl + x', exit_handler) 
    global staff_id
    staff_id = sys.argv[1]
    main()