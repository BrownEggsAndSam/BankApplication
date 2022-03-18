from account import Account
from people import People
import pandas as pd
import os


class Bank(object):
    """docstring for Bank."""

    def __init__(self):
        super(Bank, self).__init__()
        self.acct_id=0 
        self.df_userID = pd.DataFrame(columns=["Username", "Pin Number"],index=["Username"])
        self.df_Accounts = pd.DataFrame(columns=["Account Number", "Username","Account Type","Account Balance"],index=["Username"])
    

    def loadApplicationData(self):
        saveFile = True
        if saveFile is not False:
            if not os.path.exists('./SaveFiles'):
                os.makedirs('SaveFiles')
            elif not os.path.exists('./SaveFiles/bankingApp.xlsx'):
                self.df_userID.to_excel("./SaveFiles/bankingApp.xlsx")
            else:
                xls = pd.ExcelFile('./SaveFiles/bankingApp.xlsx')
                df1 = pd.read_excel(xls, 'Sheet1')
                df2 = pd.read_excel(xls, 'Sheet2')
                self.df_userID = pd.concat([self.df_userID, df1], axis=0, ignore_index=True)
                self.df_Accounts = pd.concat([self.df_Accounts, df2], axis=0, ignore_index=True)
                

    def addUser(self):
            print("Give Username:")
            username = input("> ")
            userCheck = [username]
            if userCheck != self.df_userID.isin([username]).any().any():
                try:
                    pin = int(input('Give Pin:'))
                except Exception as e:
                    print("Please enter a numeric value")
            df1 = pd.DataFrame(data=[[username,pin]],columns=["Username", "Pin Number"])
            self.df_userID = pd.concat([self.df_userID, df1], axis=0, ignore_index=True)
            print(self.df_userID)

    def getUser(self):
        print("Give Username:")
        self.username = input("> ")

        try:
            pin = int(input('Give Pin:\n> '))
            user = self.df_userID.loc[(self.df_userID["Username"]==self.username)]
            user = People(user["Username"].item(),int(user["Pin Number"].item()))
        except Exception as e:
            print("Please enter a numeric value")

        # Trobleshooting
        # if int(user2["Pin Number"].item()) == int(pin):
        #     print("workingreallygooodhereson")
        # else: 
        #     print("notrunning")    
        # #print(user)
        # print(user.auth(pin)) 
        # #user = self.df_userID.isin([username]).any()
        
        if user.auth(pin):
            print("**Access granted**\n\nWelcome back " + self.username + ".\nPlease select an about your bank accounts option to continue.\n")
            while True:
                input_value = int(input('1. Display bank accounts menu.\n2. Create a new checkings/savings account.\n> '))
                if input_value == 1:

                    print('**Bank accounts menu**\n\n')
                    Account.getAccount(self)
                    input_value = int(input('1. Deposit money to an account.\n2. Withdraw money from an account.\n3. Transfer money between accounts.\n> '))
                    if input_value == 1:
                        Account.deposit(self)
                    elif input_value == 2:
                        Account.withdraw(self)
                    elif input_value == 3:
                        Account.transfer(self)
                elif input_value == 2:
                    Account.createAccount(self)
                elif input_value == 3:
                    exit()
                else:
                    print('Please enter a valid input.')
        else:
            print('Incorrect pin, please try again')
