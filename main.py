
import json
import os


def load_json_file(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, 'r') as f:
            s = f.read()
            if not s.strip():
                return default
            data = json.loads(s)
            return data
    except (json.JSONDecodeError, ValueError):
        return default

def logout_staff(staff_id):
    # remove staff_id from live_logins.txt
    if os.path.exists('live_logins.txt'):
        with open('live_logins.txt', 'r') as f:
            live_logins = f.read().splitlines()
        if staff_id in live_logins:
            live_logins.remove(staff_id)
            with open('live_logins.txt', 'w') as f:
                for sid in live_logins:
                    f.write(sid + '\n')
    return


def save_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


credentials = load_json_file('credentials.json', [])
if not isinstance(credentials, list):
    credentials = []

# This fullfills the requirement of only allowing one of 5 servers on at once.
def login_stage2(name, staff_id):
    # switch to a txt with staff ids, when logout is implemented, remove the staff id from the txt, and check if the staff id is in the txt before allowing login. This will prevent multiple logins with the same staff id.
    #load live_logins.txt not json, just a list of staff ids, one per line
    with open('live_logins.txt', 'r') as f:
        live_logins = f.read().splitlines()
    if staff_id in live_logins:
        print("This staff ID is already logged in. Please try again later.")
        return False
    if len(live_logins) < 1: #max 5 concurrent logins
        with open('live_logins.txt', 'a') as f:
            f.write(staff_id + '\n')
        # After successful login, run order.py pass staffid to order.py using cmd args, and remove staff id from live_logins.txt when order.py exits
        os.system(f'python order.py {staff_id}')
    else:
        print("Too many users are currently logged in. Please try again later.")
        return False

#Fullfills the requirement of allowing staff to log in with their name and staff ID, it checks the credentials against a list of valid credentials loaded from a JSON file. If the credentials are valid and the staff ID is not already logged in, it allows the staff member to proceed to the next stage of the application. This ensures that only authorized staff members can access the system and helps to maintain security and accountability.
def login_stage1():
    name = input("Enter your name: ")
    staff_id = input("Enter your Staff ID: ")

    for credential in credentials:
        if credential.get('name') == name and credential.get('staff_id') == staff_id:
            return login_stage2(name, staff_id)
    print("Invalid credentials. Please try again.")
    return False


if __name__ == "__main__":
    login_stage1()

