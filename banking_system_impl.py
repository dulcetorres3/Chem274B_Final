from banking_system import BankingSystem
import time

class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self.accounts = {}
        self.outgoing_transactions = {}
        self.payment_transaction= {}
        self.time = {}
        self.process_cashback = {}
        self.payment = {}
        self.payment_id = 0


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
        self.process_cashback[self.payment_id] = {
         "cashback" : cashback,
         "account_id" : account_id,
         "timestamp" : wait_time,
         "processed" : False }


        """
        print(f'before cashback loop: {self.accounts[account_id]}')
        
        #if self.process_cashback[self.payment_id]["timestamp"] <= timestamp:
        if timestamp >= wait_time:
        self.deposit(wait_time, account_id, cashback)
            self.accounts[account_id] += cashback
        
        print(f'after cashback loop: {self.accounts[account_id]}')
        """

        self.payment_transaction[self.payment_id]= account_id

        return (f"payment{self.payment_id}")
        


    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None :
        #account check 
        if account_id not in self.accounts:
            return None
        """
        # split payment string into a list of characters
        characters = list(payment)

        # cast the last character into an integer
        index = len(characters) - 1
        payment_number = int(characters[index])
        print(f'payment string: {payment}, payment number: {payment_number}')
        """

        payment_number = int(payment[7:])
        payment_id = f"payment{payment_number}"
        
        
        # compare the last character with the payment attribute
        if payment_number not in self.payment_transaction:
            return None

        # payment for different account check
        if self.payment_transaction[payment_number] != account_id:
            return None

        # Access cashback dictionary
        cashback_info = self.process_cashback[payment_id]
        
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

