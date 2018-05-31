"""Basic contact book program"""

from pymongo import MongoClient

def get_phone(user):
    """Extracts a phone number from a user dictionary and returns it as a string"""

    phone_dict = user.get('phone_num')
    if phone_dict is not None:
        return "{}-{}".format(phone_dict.get('area'), phone_dict.get('num'))
    return "ERROR"

def valid_phone(number):
    """Checks if a string is a valid phone number"""
    return len(number) == 12 and \
           number.count("-") == 2 and \
           number[0:3].isdecimal() and \
           number[4:7].isdecimal() and \
           number[8:].isdecimal()

def run():
    """Main method. Loops infinitely and handles user input."""

    client = MongoClient()

    db = client.MongoDBSurvivalGuideExamples
    users = db.users

    while True:
        # Basic menu.
        print("1: Find User")
        print("2: Insert User")
        print("3: Remove User")
        print("0: Exit")
        intent = input("What would you like to do?: ")

        # Find
        if intent == "1":
            user = input("Which User?: ")

            # Search for a single user to see if they get a perfect match.
            # We could use a library like fuzzywuzzy to check for close
            # matches, but it's not super necessary in this case.
            found_user = users.find_one({"name": user})
            if found_user is not None:
                print("Name:         ", found_user.get('name'))
                print("Phone Number: ", get_phone(found_user))
            else:
                print(user, "not found")

        # Insert
        elif intent == "2":
            name = input("Name?: ")
            if name in users.distinct("name"):
                print(name, "already in the database")
                continue

            number = input("Phone Number? (format: XXX-XXX-XXXX): ")
            if valid_phone(number) and name != "":
                # Splitting up the phone number string into its components
                area, num = number.split("-")[0], number[number.find("-")+1:]

                # Insert the user into the database.
                users.insert({"name": name, "phone_num": {"area": area, "num": num}})
                print("User:", name, "inserted ")


        # Remove
        elif intent == "3":
            name = input("Who would you like to remove?: ")
            status = users.delete_one({"name": name})

            if status.deleted_count == 1:
                print(name, "removed successfully.")
            else:
                print(name, "not found")

        # Exit
        elif intent == "0":
            print("Goodbye.")
            break

        else:
            print("Unknown option:", intent)

        print()

if __name__ == "__main__":
    run()
