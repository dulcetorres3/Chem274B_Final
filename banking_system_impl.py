from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self.accounts = {} # Tracks account_id and balance
        self.outgoing_transactions = {} # Tracks account_id and total outgoing transactions for that account
        self.payment_counter = 0 # Incrementer used to track unique payments
        self.pending_cashbacks = [] # List of list to track cashback information (timestamp, account_id, payment_id, amount)
        self.payments = {} # Tracks account_ID and it's corresponding payment_IDs.
        self.balance_history = {}

    # TODO: implement interface methods here
    
    def create_account(self, timestamp: int, account_id: str) -> bool:
        # Return false if account already exists
        if account_id in self.accounts:
            return False
            
        
        # Initialize new account with balance of zero and return True
        self.accounts[account_id] = 0
        # Track timestamp when account was created 
        self.balance_history[account_id] = []
        self.balance_history[account_id].append((timestamp, 0))
        self.outgoing_transactions[account_id] = 0
        return True
        
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        
        # Process existing payments for cashback before running deposit operation
        self.process_cashback(timestamp)

        # Return None if account does not exist
        if account_id not in self.accounts:
            return None

        # Add given amount to provided account
        self.accounts[account_id] += amount

        #update balance history
        self.balance_history[account_id].append((timestamp, self.accounts[account_id]))
      
        # Return the new balance of the account
        return self.accounts[account_id]

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        
        # Process existing payments for cashback before running transfer operation
        self.process_cashback(timestamp)
        
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

        # Update outgoing transactions with transfered amount
        self.outgoing_transactions[source_account_id] += amount

        #update balance history
        self.balance_history[source_account_id].append((timestamp, self.accounts[source_account_id]))
        self.balance_history[target_account_id].append((timestamp, self.accounts[target_account_id]))

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

    def pay(self, timestamp:int , account_id: str, amount:int) -> str | None:

        # Process existing payments for cashback before running pay operation
        self.process_cashback(timestamp)

        # Return none if account id doesn't exist
        if account_id not in self.accounts:
            return None
        
        # Return none if account id has insufficient funds
        if self.accounts[account_id] < amount:
            return None
        
        # Update top spenders with the amount being paid
        self.outgoing_transactions[account_id] += amount

        # Increment payment counter to track payment ID
        self.payment_counter += 1

        # Create an account ID based on the payment counter
        payment_id = f"payment{self.payment_counter}"


        # Track pending cashbacks with the amount of cashback and the cashback time
        cashback = amount // 50 # Calculated cashback
        cashback_time = timestamp + 86400000 # 24 hours in ms + current timestamp
        self.pending_cashbacks.append((cashback_time, account_id, payment_id, cashback))

        # Withdraw ammount from account
        self.accounts[account_id] -= amount


        # Add a payment_ID to an account, and if account has no exisitng payments, initialize an empty list.
        if account_id not in self.payments:
            self.payments[account_id] = []
        self.payments[account_id].append(payment_id)

        #update balance history
        self.balance_history[account_id].append((timestamp, self.accounts[account_id]))

        # Return the payment_ID of the transaction
        return payment_id

    def process_cashback(self, timestamp: int):

        # Access the variables of the pending_cashbacks list
        for cashback_time, account_id, payment_id, cashback in list(self.pending_cashbacks):

            # Only apply cashback if the timestamp exceeds 24 hours for a payment_ID
            if timestamp >= cashback_time:
                
                # Add cashback amount
                self.accounts[account_id] += cashback

                # Remove the pending cashback transaction after it has been processed
                self.pending_cashbacks.remove((cashback_time, account_id, payment_id, cashback))
            #update balance history
            self.balance_history[account_id].append((timestamp, self.accounts[account_id]))

    """
    HELPER FUNCTION FOR BALANCE HISTORY
    def update_balance_history(self, account_id: str, timestamp: int):
        if account_id not in self.balance_history:
            self.balance_history[account_id] = []
        self.balance_history[account_id].append((timestamp, self.accounts[account_id]))
    """

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:

        # Process existing payments for cashback before running status operation
        self.process_cashback(timestamp)

        # Return none if account_id doesn't exist
        if account_id not in self.payments:
            return None
        
        # Return none if the given payment does not exist for the specified account
        if payment not in self.payments[account_id]:
            return None
        
        # Return none if the payment transaction was for an account
        # with a different identifier from account_id
        if payment not in self.payments.get(account_id, []):
            return None
        
        # Access varibales in the list of pending cashbacks and return "IN_PROGRESS" if the timestamp is less than 
        # the cashback time for a specific account id and payment id
        for cashback_time, cashback_account_id, cashback_payment_id, cashback_amount in self.pending_cashbacks:
            if cashback_account_id == account_id and cashback_payment_id == payment:
                if timestamp < cashback_time:
                    return "IN_PROGRESS"
                
        # If this point is reached, cashback has been successfully processed.
        return "CASHBACK_RECEIVED"
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        
        #check if account 1 is equal to account 2
        if account_id_1 == account_id_2:
            return False
        # check if account 1 exist
        if account_id_1 not in self.accounts:
            return False
        # check if account 2 exist
        if account_id_2 not in self.accounts: 
            return False

        # Cashback for account 2 refunded to account 1
        for i, (cashback_time, account_id, payment_id, cashback) in enumerate(self.pending_cashbacks):
            if account_id == account_id_2:
                self.pending_cashbacks[i] = (cashback_time, account_id_1, payment_id, cashback)
        
        # Update payment transactions
        self.payments[account_id_1] = self.payments.get(account_id_1, []) + self.payments.pop(account_id_2, [])
        
        # Add balance of account 2 to account 1
        self.accounts[account_id_1]+= self.accounts[account_id_2]
        
        #top spenders (account 2 in outgoing transactions)
        if account_id_2 in self.outgoing_transactions: 
            #add account 2 outgoing transactions to account 1
            self.outgoing_transactions[account_id_1] += self.outgoing_transactions[account_id_2]
            
        # delete merged account from account dictionary
        del self.accounts[account_id_2]

        # delete merged account from outgoing transactions
        del self.outgoing_transactions[account_id_2]

        #update balance history
        self.balance_history[account_id_1].append((timestamp, self.accounts[account_id_1]))

        # Balance history for account 2 goes into account 1
        self.balance_history[account_id_1].extend(self.balance_history[account_id_2])
        
        # Delete balance history for account 2
        del self.balance_history[account_id_2]
        
        # Successful merge
        return True
    
    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        # Process pending cashbacks, if applicable
        self.process_cashback(timestamp)
    
        if account_id not in self.balance_history:
            return None
        """""""""
        # account not exist at given time
        if self.balance_history[account_id][0][0] < time_at:
            return None
        """

        # get balance at time_at
        for time, balance in self.balance_history[account_id]:
            if time == time_at:
                return balance
        
        
if __name__ == "__main__":
    
    bs = BankingSystemImpl()

    print(bs.create_account(1, "account1"))
    print(bs.create_account(2, "account2"))
    print(bs.deposit(3, "account1", 500))
    print(bs.deposit(4, "account2", 600))
    print(bs.merge_accounts(5, "account1", "account2"))
    print(bs.get_balance(6, "account1", 3))
    print(bs.get_balance(7, "account1", 5))