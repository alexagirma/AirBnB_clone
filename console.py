#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
        return retl


class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB command interpreter.
    Attributes:
        prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            argl = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", argl[1])
            if match is not None:
                command = [argl[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in argdict.keys():
                    call = "{} {}".format(argl[0], command[1])
                    return argdict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Create a new class instance and print its id.
        """
        argl = parse(arg)
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(argl[0])().id)
            storage.save()

    def do_show(self, arg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        argl = parse(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(argl[0], argl[1])])

    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        argl = parse(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(argl[0], argl[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argl = parse(arg)
        if len(argl) > 0 and argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            for obj in storage.all().values():
                if len(argl) > 0 and argl[0] == obj.__class__.__name__:
                    objl.append(obj.__str__())
                elif len(argl) == 0:
                    objl.append(obj.__str__())
            print(objl)

    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl = parse(arg)
        count = 0
        for obj in storage.all().values():
            if argl[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        argl = parse(arg)
        objdict = storage.all()

        if len(argl) == 0:
            print("** class name missing **")
            return False
        if argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(argl) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
            return False
        if len(argl) == 2:
            print("** attribute name missing **")
            return False
        if len(argl) == 3:
            try:
                type(eval(argl[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(argl) == 4:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            if argl[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[argl[2]])
                obj.__dict__[argl[2]] = valtype(argl[3])
            else:
                obj.__dict__[argl[2]] = argl[3]
        elif type(eval(argl[2])) == dict:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            for k, v in eval(argl[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
#!/usr/bin/python3
"""Program called console.py that contains the entry point of the command
interpreter.
"""
import cmd
import os
from models.base_model import BaseModel
from models import storage

# TODO: refactor delete, create, update, print in storage


class HBNBCommand(cmd.Cmd):
    """Class to manage the console and all the commands built to the project"""
    prompt = '(hbnb)'
    valid_classes = ['BaseModel', 'User', 'Amenity', 'Review', 'State', 'City',
                     'Place']

    ERROR_CLASS_NAME = '** class name missing **'
    ERROR_CLASS = "** class doesn't exist **"
    ERROR_ID = "** instance id missing **"
    ERROR_ID_NOT_FOUND = "** no instance found **"
    ERROR_ATTR = "** attribute name missing **"
    ERROR_ATTR_VALUE = "** value missing **"

    def cmd_cls_args_split(self, command, class_name):
        """Auxiliary function to update the command-line interpreter. This
        function manages and reorders the input of the console to allow the
        functions to work with a formatted command line.
        """
        if command.find("(") != -1:
            attr_name = ''
            value = ''

            args_split = command.split('(')
            command = args_split[0]
            args_split[1] = args_split[1].replace(')', '')
            args_split[1] = args_split[1].replace('"', '')
            args = args_split[1].split(',')
            id_number = args[0].strip(" ")
            if len(args) > 1:
                attr_name = args[1].strip(" ")
            if len(args) > 2:
                value = args[2].strip(" ")
            return '{} {} {} {} "{}"'.format(command, class_name, id_number,
                                             attr_name, value)

        elif class_name in HBNBCommand.valid_classes:
            return "{} {}".format(command, class_name)

    def onecmd(self, line: str) -> bool:
        """Updating the command line interpreter to allow this usage:
        <class name>.<command>() or <class name>.<command>("args")
        """
        line_split = line.split(".")
        # Class.command
        if len(line_split) > 1:
            class_name = line_split[0]
            command = line_split[1].replace('()', '')
            # parameters
            line = self.cmd_cls_args_split(command, class_name)

        return super().onecmd(line)

    def validate_len_args(self, arg):
        """Validates if the command receives the class_name argument"""
        if len(arg) == 0:
            print(HBNBCommand.ERROR_CLASS_NAME)
            return False
        return True

    def validate_class_name(self, arg):
        """Validates if the class_name argument is a valid class"""
        args = arg.split(' ')
        class_name = args[0]
        if class_name not in HBNBCommand.valid_classes:
            print(HBNBCommand.ERROR_CLASS)
            return False
        return class_name

    def validate_id(self, arg):
        """Validates if the command receives an id_number argument """
        args = arg.split(' ')
        if len(args) < 2:
            print(HBNBCommand.ERROR_ID)
            return False
        id_number = args[1]
        return id_number

    def validate_attr(self, arg):
        """Validates if the command receives an attribute argument"""
        args = arg.split(' ')
        if len(args) < 3:
            print(HBNBCommand.ERROR_ATTR)
            return False
        attribute = args[2]
        return attribute

    def validate_attr_value(self, arg):
        """Validates if attribute value exists"""
        args = arg.split(' ')
        if len(args) < 4:
            print(HBNBCommand.ERROR_ATTR_VALUE)
            return False
        attr_value = args[3]
        return attr_value

    def do_EOF(self, arg):
        """ Quits with new line <end of file>
        Usage: Ctrl + d """
        print()
        return True

    def emptyline(self):
        """ None """
        pass

    def do_quit(self, arg):
        """ Quits the console
        Usage: quit """
        return True

    def do_create(self, arg):
        """ Creates new elements
        Usage: create <class_name> or <class_name>.create()
        """
        if not self.validate_len_args(arg):
            return

        class_name = self.validate_class_name(arg)
        if not class_name:
            return

        storage.create(class_name)

    def do_show(self, arg):
        """ Shows an element by id_number
        Usage: show <class_name> <id> or <class_name>.show("<id>")
        """
        if not self.validate_len_args(arg):
            return

        class_name = self.validate_class_name(arg)
        if not class_name:
            return

        id_number = self.validate_id(arg)
        if not id_number:
            return
        objects = storage.all()
        key = "{}.{}".format(class_name, id_number)
        try:
            print(objects[key])
        except:
            print(HBNBCommand.ERROR_ID_NOT_FOUND)

    def do_destroy(self, arg):
        """ Deletes elements in storage
        Usage: destroy <class_name> <id> or <class_name>.destroy("<id>")
        """
        if not self.validate_len_args(arg):
            return

        class_name = self.validate_class_name(arg)
        if not class_name:
            return

        id_number = self.validate_id(arg)
        if not id_number:
            return

        objects = storage.all()
        key = "{}.{}".format(class_name, id_number)

        try:
            del objects[key]
            storage.save()
        except:
            print(HBNBCommand.ERROR_ID_NOT_FOUND)

    def do_all(self, arg):
        """ Prints all elements in storage by class name
         Usage: all or all <class_name> or <class_name>.all()
        """
        class_name = None
        if len(arg) > 0:
            class_name = self.validate_class_name(arg)
            if not class_name:
                return
            # filter data
        storage.print(class_name)

    def do_update(self, arg):
        """ Updates info in storage
        Usage: update <class_name> <id> <attribute_name> <attribute_value>
        or <class_name>.update("<id>", "<attribute_name>", "<attribute_value>")
        """
        if not self.validate_len_args(arg):
            return
        class_name = self.validate_class_name(arg)
        if not class_name:
            return
        id_number = self.validate_id(arg)
        if not id_number:
            return

        attribute = self.validate_attr(arg)
        if not attribute:
            return
        attr_value = self.validate_attr_value(arg)
        if not attr_value:
            return
        try:
            objects = storage.all()
            key = "{}.{}".format(class_name, id_number)
            obj = objects[key]
        except:
            print(HBNBCommand.ERROR_ID_NOT_FOUND)
            return

        # obj[attribute] = attr_value
        attr_value = attr_value.strip('"')

        if attr_value.isdigit():
            attr_value = int(attr_value)
        else:
            try:
                attr_value = float(attr_value)
            except:
                pass

        setattr(obj, attribute, attr_value)
        obj.save()

    def do_clear(self, _):
        """Clears the terminal
        Usage: clear
        """
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('cls')

    def do_count(self, arg):
        """ Retrieves the number of instances of a specific class
        Usage: <class_name>.count()
        """
        if not self.validate_len_args(arg):
            return
        class_name = self.validate_class_name(arg)
        if not class_name:
            return

        class_list = storage.filter_by_class(class_name)
        print(len(class_list))

if __name__ == '__main__':
    HBNBCommand().cmdloop()
