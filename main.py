import os
from bank import Bank
from people import People

def main():
    print("Hi, welome, select an option")
    bb = Bank()
    while True:
        bb.loadApplicationData()
        print("1: create an account")
        print("2: get an account")
        print("3: exit")

        userInput = input("> ")

        if userInput == "1":
            bb.addUser()

        if userInput == "2":
            bb.getUser()

        elif userInput == "3":
            exit()

if __name__ == '__main__':
    main()
