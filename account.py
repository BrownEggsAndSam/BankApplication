from people import People
import pandas as pd


class Account(object):
    """docstring for Account."""
    print()
    def __init__(self, arg):
        super(Account, self).__init__()
        self.arg = arg
        self.acc_id=0
        self.balance=0
        self.acc_type=""
   

    def deposit(self):
            amount = float(input("Enter amount to be deposited: "))
            self.balance += amount
            print("\n Amount Deposited:", amount)
    
    # Function to withdraw the amount
    def withdraw(self):
            amount = float(input("Enter amount to be withdrawn: "))
            if self.balance >= amount:
                self.balance -= amount
                print("\n You Withdrew:", amount)
            else:
                print("\n Insufficient balance  ")

    # Function to display the amount
    
    def transfer(self):

            print()

    def createAccount(self):
        input_value = int(input('Enter 1 to create a Checking Account,\n2 to create a Savings Account,\n3 to exit the application'))
        if input_value == 1:
            self.acc_Type = "Checking"
            self.acc_id = len(self.df_Accounts)+1
            self.balance = float(input('How much would you like to intially:'))
            df1 = pd.DataFrame(data=[[self.acc_id, self.username, self.acc_Type, self.balance]],columns=["Account Number", "Username","Account Type","Account Balance"],index=["Username"])
            self.df_Accounts = pd.concat([self.df_Accounts, df1], axis=0)

        elif input_value == 2:
            self.acc_Type = "Savings"
            self.acc_id = len(self.df_Accounts)+1
            try:
                self.balance = float(input('How much would you like to intially:'))
            except Exception as e:
                    print("Please enter a numeric value")
            df1 = pd.DataFrame(data=[[self.acc_id, self.username, self.acc_Type, self.balance]],columns=["Account Number", "Username","Account Type","Account Balance"],index=["Username"])
            self.df_Accounts = pd.concat([self.df_Accounts, df1], axis=0)

        elif input_value == 3:
            exit()

    def getAccount(self):
        print("Here is a list of all your accounts:")
        # print(self.df_Accounts['Username'].isin([self.username])) #Gives true statements
        print(self.df_Accounts[self.df_Accounts.Username.isin([self.username])])

