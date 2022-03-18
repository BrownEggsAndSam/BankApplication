from people import People
import pandas as pd


class Account(object):
    """docstring for Account."""
    print()
    def __init__(self, arg):
        super(Account, self).__init__()
        self.arg = arg
        self.acc_id=int(0)
        self.balance=float(0)
        self.acc_type=""
   
    def createAccount(self):
        input_value = int(input('1.Create a Checking Account.\n2.Create a Savings Account.\n3.Exit application.'))
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
        df1 = self.df_Accounts.loc[self.df_Accounts['Username']==self.username]
        print(df1.to_string(index=False))

    def deposit(self):
            df1 = self.df_Accounts.loc[self.df_Accounts['Username']==self.username]
            print(df1)
            userInput = int(input("Select an account you would like to deposit into\n>"))
            df1 = df1.loc[df1['Account Number']==userInput]
            df1 = df1.reset_index(drop=True)
            print(df1)
            self.balance = df1.iloc[0,3]
            print(self.balance)
            #Want to record this transaction later on.
            amount = float(input("Enter amount to be deposited: "))
            self.balance += amount
            print("\n Amount Deposited:", amount)
            print("\n New balance:", self.balance)
            #Need to record new balance into amount. 
    
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
