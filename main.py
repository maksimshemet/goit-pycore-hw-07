from collections import UserDict
import datetime
import functools

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) >= 10): #should be at least 10 digits if we consider country codes
            raise ValueError("Phone number must be a 10-digit number.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones = [p for p in self.phones if p.value != phone_obj.value]
    
    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = Phone(old_phone)
        for i, p in enumerate(self.phones):
            if p.value == old_phone_obj.value:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone number not found.")
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def show_birthday(self):
        if self.birthday:
            return f"{self.name.value}'s birthday is on {self.birthday.value}"
        else:
            return f"No birthday recorded for {self.name.value}"

    def find_phone(self, phone):
        phone_obj = Phone(phone)
        for p in self.phones:
            if p.value == phone_obj.value:
                return p
        return None 

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def __str__(self):
        if len(self.data) == 0:
            return "No records"
        return "\n".join(f"{value}" for key, value in self.data.items())

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name, None)
    
    def get_upcoming_birthdays(self):
        today = datetime.datetime.today().date()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if record.birthday:
                birthday = datetime.datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                delta_days = (birthday_this_year - today).days
                
                if 0 <= delta_days <= 7:
                    congratulation_date = birthday_this_year
                    
                    if congratulation_date.weekday() == 5:  # Saturday
                        congratulation_date += datetime.timedelta(days=2)
                    elif congratulation_date.weekday() == 6:  # Sunday
                        congratulation_date += datetime.timedelta(days=1)
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                    })
        
        return upcoming_birthdays

def input_error(func):
    @functools.wraps(func)

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            if func.__name__ == "add_contact" or func.__name__ == "change_contact" and isinstance(e, IndexError):
                return "Give me name and phone please.\nExample - add John 1234567890 or change John 0987654321"
            elif func.__name__ == "get_contact":
                return "Contact not found."
            elif func.__name__ == "get_all":
                return "No contacts available."
            else:
                return "An error occurred. Please check your input."

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return record.show_birthday()


@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(str(record) for record in upcoming_birthdays)


@input_error
def edit_phone(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number updated for {name}."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return f"Phones for {name}: " + "; ".join(p.value for p in record.phones)


def parse_input(user_input):
    return user_input.split()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        try:
            command, *args = parse_input(user_input)
        except ValueError:
            command = None
            args = None

        match command:
            case "close" | "exit":
                print("Good bye!")
                break

            case "hello":
                print("How can I help you?")

            case "add":
                print(add_contact(args, book))

            case "change":
                print(edit_phone(args, book))

            case "phone":
                print(show_phone(args, book))

            case "all":
                print(book)

            case "add-birthday":
                print(add_birthday(args, book))

            case "show-birthday":
                print(show_birthday(args, book))

            case "birthdays":
                print(birthdays(book))

            case _:
                print("Invalid command.")


if __name__ == "__main__":
    main()
