import os
from bank import Bank
from people import People

def main():
    print("**Welcome to the Banking Application.\nPlease select an option to continue\n")
    bb = Bank()
    while True:
        bb.loadApplicationData()
        print("1: Create an user profile")
        print("2: Log into your user profile")
        print("3: Exit Application")

        userInput = input("> ")

        if userInput == "1":
            bb.addUser()

        if userInput == "2":
            bb.getUser()

        elif userInput == "3":
            exit()

if __name__ == '__main__':
    main()
