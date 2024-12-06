from banking_system import BankingSystem
import time

class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self.accounts = {}
        self.outgoing_transactions = {}
        self.payment_transaction= {}
        #self.time = {}
        self.process_cashback = {}
        #self.payment = {}
        self.payment_id = 0

        #dictonary containing all of the information associated with a payment-- each entry in the dictionary is unqiue to an account_id and timestamp
        self.new_dict = {}
        #increment every time a valie payment initiated
        self.payment_number = 0



    # TODO: implement interface methods here
    
    def create_account(self, timestamp: int, account_id: str) -> bool:
        # Return false if account already exists
        if account_id in self.accounts:
            return False
            
        # Initialize new account with balance of zero and return True
        self.accounts[account_id] = 0
        self.outgoing_transactions[account_id] = 0
        return True
        
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
      
        
        # Return None if account does not exist
        if account_id not in self.accounts:
            return None
            
        # Add given amount to provided account
        self.accounts[account_id] += amount
      
        # Return the new balance of the account
        return self.accounts[account_id]

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        # return None if source account does not exist
        if source_account_id not in self.accounts or target_account_id not in self.accounts:
            return None
        
        # return None if target and soource ids are the same
        if target_account_id == source_account_id:
            return None
        
        # return None if source account has insufficient funds
        if self.accounts[source_account_id] < amount:
            return None 
        
        # trasfer funds from source to target
        self.accounts[source_account_id] -= amount
        self.accounts[target_account_id] += amount

        self.outgoing_transactions[source_account_id] += amount

        # return balance of source
        return self.accounts[source_account_id]

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        #sorted_trans = sorted(self.outgoing_transactions.items(), key=lambda item: item[1], reverse=True)
        sorted_trans = sorted(self.outgoing_transactions.items(), key=lambda x: (-int(x[1]), x[0]))
           
        if len(self.accounts) < n:
            top_list = sorted_trans
        else: 
            top_list = sorted_trans[:n]

        sorted_result = [ f"{account_id}({outgoing})" for account_id, outgoing in top_list]

        return sorted_result
    
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:

        #account check
        if account_id not in self.accounts:
            return None

        #insufficient funds check 
        if self.accounts[account_id] < amount:
            return None 
        

        # increment self.payemnt_number 
        self.payment_number+= 1

        #if payment new, add the info associated with payment to dictionary
        if (account_id, self.payment_number) not in self.new_dict:

            # Calculate Cashback amount
            cashback = round(amount * 0.02)

            self.new_dict[(account_id, self.payment_number)] = {
                "amount" : amount,
                "payment" : self.payment_number,
                "cashback" : cashback,
                "timestamp" : timestamp + 86400000,
                "processed" : False

            }

            # subtract amount from account balance
            self.accounts[account_id] -= amount

            # update outgoing transactions
            self.outgoing_transactions[account_id] += amount

            return (f"payment{self.payment_number}")
        
        #if payment had already been initialized in the dictionary, subtract payment_number 
        self.payment_number-= 1

        # if payment transaction already exists, check if timestamp wait time is fulfilled
        if (account_id, timestamp) in self.new_dict:

            # if 24 hours has passsed since the payment has been initiated, deposit cashback 
            if timestamp >= self.new_dict[(account_id, timestamp)]['timestamp']:
                self.accounts[account_id]+= self.new_dict[(account_id, timestamp)]['cashback']
                self.new_dict[(account_id, self.payment_number)]['processed'] = True



    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None :
        #account check 
        if account_id not in self.accounts:
            return None

        # split payment string into a list of characters
        characters = list(payment)

        # cast the last character into an integer
        index = len(characters) - 1
        payment_number = int(characters[index])
        print(f'payment string: {payment}, payment number: {payment_number}')



        # compare the last character with the payment attribute
        if (account_id, payment_number) not in self.new_dict:
            return None


        # Access cashback dictionary
        cashback_info = self.new_dict[(account_id, payment_number)]

        # determine ammount associated with payment
        amount = self.new_dict[(account_id, payment_number)]['amount']

        #print(f'Timestamp: {self.new_dict[(account_id, timestamp)]['timestamp']}')

        # call pay function if the timestamp is fulfilled
        if timestamp >= self.new_dict[(account_id, payment_number)]['timestamp']:
            self.pay(timestamp, account_id, amount)

        # Check whether cashback has already been processed
        if cashback_info["processed"] == True:
            return "CASHBACK_RECEIVED"
        else:
            return "IN_PROGRESS"

        """
        # This should add cashback amount to account balance
        if cashback_info["timestamp"] <= timestamp:
            self.accounts[account_id] += cashback_info["cashback"]
            cashback_info['processed'] = True
            return "CASHBACK_RECEIVED"
        """
        # If you get this far, payment is still in progress
        #return "IN_PROGRESS"

    """
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:

        #account check
        if account_id not in self.accounts:
            return None

        #insufficient funds check 
        if self.accounts[account_id] < amount:
            return None 
    
        # Calculate Cashback amount
        cashback = round(amount * 0.02)

        print(f'cashback: {cashback}')

        # Subtract amount from account balance
        self.accounts[account_id] -= amount 

        # Need to update top spenders
        self.outgoing_transactions[account_id] += amount

        # Increment payment ID
        self.payment_id += 1

        #cashback  waiting period
        wait_time = timestamp + 86400000

        # Dictionary to store cashback information
        # such as amount, account_id, timestamp, and processed status
        self.process_cashback[(account_id, self.payment_id)] = {
         "cashback" : cashback,
         "timestamp" : wait_time,
         "processed" : False }

        print(f'before cashback loop: {self.accounts[account_id]}')
        
        #if self.process_cashback[self.payment_id]["timestamp"] <= timestamp:
        if timestamp >= wait_time and not in self.process_cashback[self.payment_id]["processed"]:
            self.deposit(wait_time, account_id, cashback)
            self.accounts[account_id] += cashback
        
        print(f'after cashback loop: {self.accounts[account_id]}')
        
        # Initialize list if account not already in payment transaction
        if account_id not in self.payment_transaction:
            self.payment_transaction[account_id] = []
        # Record payment transaction
        self.payment_transaction[account_id].append(self.payment_id)

        return (f"payment{self.payment_id}")
        

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None :
        # account check 
        if account_id not in self.accounts:
            return None

        # split payment string into a list of characters
        characters = list(payment)

        # cast the last character into an integer
        index = len(characters) - 1
        payment_number = int(characters[index])
        print(f'payment string: {payment}, payment number: {payment_number}')
        
        # Check if account id has recorded payments
        if account_id not in self.payment_transaction:
            return None
        
        # compare the last character with the payment attribute
        if payment_number not in self.payment_transaction[account_id]:
            return None

        # payment for different account check
        #if self.payment_transaction[account_id] != payment_number:
            #return None

        # Access cashback dictionary
        cashback_info = self.process_cashback[(account_id, payment_number)]
        
        # Check whether cashback has already been processed
        if cashback_info["processed"] == True:
            return "CASHBACK_RECEIVED"

        # This should add cashback amount to account balance
        if cashback_info["timestamp"] <= timestamp:
            self.accounts[account_id] += cashback_info["cashback"]
            cashback_info['processed'] = True
            return "CASHBACK_RECEIVED"
            
        # If you get this far, payment is still in progress
        return "IN_PROGRESS"
    """        

if __name__ == "__main__":
    
    bs = BankingSystemImpl()

    
    bs.create_account(1, 'account1')
    print(bs.deposit(2, 'account1', 2000), 2000)
    print(bs.pay(3, 'account1', 100))
    print(bs.pay(4, 'account1', 200))
    print(bs.deposit(5, 'account1', 100), 1800)
    print(bs.get_payment_status(6, 'account1', 'payment1'))
    print(bs.get_payment_status(864000015, 'account1', 'payment1'))
    print(bs.pay(864000023, 'account1', 200))
    print(bs.get_payment_status(864000024, 'account1', 'payment1'))



