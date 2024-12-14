from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        self.accounts = {} # Tracks account_id, balance, outgoing transactions, and history
        self.payment_counter = 0 # Incrementer used to track unique payments
        self.pending_cashbacks = [] # List of list to track cashback information (timestamp, account_id, payment_id, amount)
        self.payments = {} # Tracks account_ID and it's corresponding payment_IDs.
        self.balance_history = {} # Tracks balance history of an account at a specific time
        self.merged_accounts = {} # Tracks which accounts have been merged, and the timestamp of the merge

    def create_account(self, timestamp: int, account_id: str) -> bool:

        # Return false if account already exists
        if account_id in self.accounts:
            return False
        # Initialize new account with balance of zero and return True
        self.accounts[account_id] = {
            "balance": 0,
            "outgoing": 0,
            "history": [(timestamp, 0)],
            
        }
        
        # Initializes the balance history of an account as an empty list, which will store tuples
        self.balance_history[account_id] = []

        # Updates the balance of the account with a tuple containing the account history and it's corresponding timestamp
        self.update_balance_history(account_id, timestamp)

        # Returns true if account creation is successful
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # Return None if account does not exist
        if account_id not in self.accounts:
            return None
        
        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)

        # Add given amount to provided account
        self.accounts[account_id]["balance"] += amount

        # Updates account history
        self.accounts[account_id]["history"].append((timestamp, self.accounts[account_id]["balance"]))

        # Updates balance history
        self.update_balance_history(account_id, timestamp)

        # Return balance of account_id
        return self.accounts[account_id]["balance"]

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:

        # return None if source account does not exist
        if source_account_id not in self.accounts or target_account_id not in self.accounts:
            return None
    
        # return None if target and soource ids are the same
        if target_account_id == source_account_id:
            return None
        
        # return None if source account has insufficient funds
        if self.accounts[source_account_id]["balance"] < amount:
            return None 
        
        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)
        
    
        # trasfer funds from source to target
        self.accounts[source_account_id]["balance"] -= amount
        self.accounts[target_account_id]["balance"] += amount

        # Update outgoing transactions with transfered amount
        self.accounts[source_account_id]["outgoing"] += amount

        # Update account histories for target and source account
        self.accounts[source_account_id]["history"].append((timestamp, self.accounts[source_account_id]["balance"]))
        self.accounts[target_account_id]["history"].append((timestamp, self.accounts[target_account_id]["balance"]))

        # Update balance histories for target and source account
        self.update_balance_history(source_account_id, timestamp)
        self.update_balance_history(target_account_id, timestamp)

        # Return balance of source
        return self.accounts[source_account_id]["balance"]
    
    def top_spenders(self, timestamp: int, n: int) -> list[str]:

        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)

        # Sort outgoing transactions by decreasing amounts
        sorted_trans = sorted(self.accounts.items(), key=lambda x: (-x[1]["outgoing"], x[0]))

        # Store a list of the top n values
        top_list = sorted_trans[:n]

        # Sort the top_list
        sorted_result = [f"{account_id}({data['outgoing']})" for account_id, data in top_list]

        # Return the sorted top_list
        return sorted_result  
    
    def pay(self, timestamp:int , account_id: str, amount:int) -> str | None:
        
        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)

        # Return none if account id doesn't exist
        if account_id not in self.accounts:
            return None
        
        # Return none if account id has insufficient funds
        if self.accounts[account_id]["balance"] < amount:
            return None

        # Update top spenders with the amount being paid
        self.accounts[account_id]["outgoing"] += amount

        # Increment payment counter to track payment ID
        self.payment_counter += 1

        # Create an account ID based on the payment counter
        payment_id = f"payment{self.payment_counter}"

        # Track pending cashbacks with the amount of cashback and the cashback time
        cashback = amount // 50 # Calculated cashback
        cashback_time = timestamp + 86400000 # 24 hours in ms + current timestamp
        self.pending_cashbacks.append((cashback_time, account_id, payment_id, cashback))

        # Withdraw ammount from account
        self.accounts[account_id]["balance"] -= amount
        
        # Add a payment_ID to an account, and if account has no exisitng payments, initialize an empty list.
        if account_id not in self.payments:
            self.payments[account_id] = []
        self.payments[account_id].append(payment_id)

        # Update account history
        self.accounts[account_id]["history"].append((timestamp, self.accounts[account_id]["balance"]))

        # Update balance history
        self.update_balance_history(account_id, timestamp)

        # Return the payment_ID of the transaction
        return payment_id
    
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

        # Check account validity
        if account_id_1 == account_id_2 or account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False

        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)

        # Cashback for account 2 refunded to account 1
        for i, (cashback_time, account_id, payment_id, cashback) in enumerate(self.pending_cashbacks):
            if account_id == account_id_2:
                self.pending_cashbacks[i] = (cashback_time, account_id_1, payment_id, cashback)

        # Update payment transactions
        self.payments[account_id_1] = self.payments.get(account_id_1, []) + self.payments.pop(account_id_2, [])

        # Update merged balance
        self.accounts[account_id_1]["balance"] += self.accounts[account_id_2]["balance"]

        # Update merged outgoing transactions
        self.accounts[account_id_1]["outgoing"] += self.accounts[account_id_2]["outgoing"]

        # Update merged history of account_id_1
        self.accounts[account_id_1]["history"].append((timestamp, self.accounts[account_id_1]["balance"]))
        self.accounts[account_id_1]["history"].sort()

        # Add the merged account to the merged_accounts dictionary
        if account_id_2 not in self.merged_accounts:
            self.merged_accounts[account_id_2] = []
        
        # Store information about account_id_2 being merged into account_id_1
        self.merged_accounts[account_id_2].append((account_id_1, timestamp))

        # Update balance histories for account_id_1 and account_id_2
        self.update_balance_history(account_id_1, timestamp)
        self.update_balance_history(account_id_2, timestamp)

        # Remove merged account
        del self.accounts[account_id_2]

        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:

        # Return none if account id is not found in accounts or merged accounts
        if account_id not in self.accounts and account_id not in self.merged_accounts:
            return None
        
        # Check if cashback needs to be processed, and if so apply cashback
        self.process_cashback(timestamp)

        # If account has been merged, it should be stored in merged_accounts
        while account_id in self.merged_accounts:

            # Time at which merge occured
            merged_time = self.merged_accounts[account_id][0][1]

            # If queried time is before the merge occured...
            if time_at < merged_time:

                # Instantiate balance history of the account as 'balance_history'
                balance_history = self.balance_history.get(account_id, [])

                # Use 'get_balance_before' to grab the balance at the provided timestamp 'time_at'
                balance = self.get_balance_before(balance_history, time_at)

                # Return the balance
                return balance
            
            # If queried time is after the merge
            if time_at > merged_time and account_id in self.accounts:

                balance_history = self.balance_history.get(account_id, [])
                balance = self.get_balance_before(balance_history, timestamp)

                return balance
            
            else:
                return None
        
        # If account has not been merged, it should still be in the accounts dictionary
        if account_id in self.accounts: 

            # Store account id dictionary as account
            account = self.accounts[account_id]

            # Grab the merged timestamp, if it exists. (This would exist if an account was merged into this account)
            merge_timestamp = account.get("merged_timestamp")

            # If merge timestamp exists, this indicates an account has been merged into account_id
            if merge_timestamp:

                # If time_at is BEFORE that merge occured...
                if time_at < merge_timestamp:

                    # Store the balance history...
                    balance_history = self.balance_history.get(account_id, [])

                    # ... and the balance from before the accounts were merged.
                    balance = self.get_balance_before(balance_history, time_at)

                    # Return the balance
                    return balance
                
                # If the accounts have been merged into account_it, but the time_at is AFTER the merge occured...
                else:
                    
                    # Grab the balance from the merged history, and return the balance.
                    for time, balance in reversed(account["history"]):
                        if time <= time_at:
                            return balance
            
            # If merge_timestamp does not exist, this indicates no accounts have been merged into account_id
            else:

                # Grab the balance from the current account history, and return the balance.
                for time, balance in reversed(self.accounts[account_id]["history"]):
                    if time <= time_at:
                        return balance

            # At this point, account_id probably does not exist anywhere.
            return None  

    def get_balance_before(self, history: list, time_at: int) -> int | None:
        # Iterate over the history in reverse to find the most recent valid entry
        for timestamp, account_history in reversed(history):
            if timestamp <= time_at:
                # Return the last balance from the account history at this timestamp
                if account_history:
                    return account_history[-1][1]  # The balance from the last entry in the history
        return None

    def process_cashback(self, timestamp: int):

        # Access the variables of the pending_cashbacks list
        for cashback_time, account_id, payment_id, cashback in list(self.pending_cashbacks):

            # Only apply cashback if the timestamp exceeds 24 hours for a payment_ID
            if timestamp >= cashback_time:

                # Add cashback amount
                self.accounts[account_id]["balance"] += cashback

                self.accounts[account_id]["history"].append((cashback_time, self.accounts[account_id]["balance"]))

                # Remove the pending cashback transaction after it has been processed
                self.pending_cashbacks.remove((cashback_time, account_id, payment_id, cashback))

    def update_balance_history(self, account_id: str, timestamp: int):
        # If account_id does not already have a balance history, initialize an empty dictionary
        if account_id not in self.balance_history:
            self.balance_history = {}

        # Store the history of account
        history = list(self.accounts[account_id]["history"])

        # Append the timestamp and associated account history to the balance history dictionary.
        self.balance_history[account_id].append((timestamp, history))      
