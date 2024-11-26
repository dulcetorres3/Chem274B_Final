from banking_system import BankingSystem
from collections import defaultdict

class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self.accounts = {}
        self.outgoing_transactions = {}
        self.payments = {}
        self.payment_counter = 0
        self.cashback_schedule = defaultdict(list)

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

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        
        if account_id not in self.accounts or self.accounts[account_id] < amount:
            return None
        
        self.accounts[account_id] -= amount

        self.outgoing_transactions[account_id] += amount

        self.payment_counter += 1

        payment_id = f"payment{self.payment_counter}"

        self.payments[payment_id] = {
            "timestamp" : timestamp,
            "account_id" : account_id,
            "amount" : amount,
            "cashback" : amount // 50,
            "status" : "IN_PROGRESS"
        }

        cashback_time = timestamp + 86400000
        self.cashback_schedule[cashback_time].append(payment_id)

        return payment_id


    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        #sorted_trans = sorted(self.outgoing_transactions.items(), key=lambda item: item[1], reverse=True)
        sorted_trans = sorted(self.outgoing_transactions.items(), key=lambda x: (-int(x[1]), x[0]))

           
        if len(self.accounts) < n:
            top_list = sorted_trans
        else: 
            top_list = sorted_trans[:n]

        """""
        for i in range(len(top_list) - 1):
            if top_list[i][1] == top_list[i+1][1]:
                print(f"Account{i} : {top_list[i][1]} Account{i} : {top_list[i][1+1]}")
                #if top_list[i][0] < top_list[i+1][0]:
                   # top_list[i], top_list[i+1] = top_list[i+1], top_list[i]
            #if len(top_list) > 1:
                if top_list[i][0] < top_list[i+1][0]:
                    
                    top_list[i], top_list[i+1] = top_list[i+1], top_list[i]
        """

        sorted_result = [ f"{account_id}({outgoing})" for account_id, outgoing in top_list]

        return sorted_result

        
    

if __name__ == "__main__":
    
    bs = BankingSystemImpl()

    # Create account 1
    bs.create_account(1, "account1")

    # Deposit 100 dollars
    bs.deposit(2, "account1", 100)

    # Create account 2
    bs.create_account(3, "account2")

    # Transfer from account 1 to account 2
    print(bs.transfer(4, "account1", "account2", 50))

    # Print all accounts
    print(bs.accounts)

    bs.create_account(5, "account3")

    bs.deposit(6, "account3", 500)

    # Print the top 3 spenders
    print(bs.top_spenders(7, 3))


