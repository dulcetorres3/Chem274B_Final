from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self.accounts = {} # Tracks account_id and balance
        self.payment_counter = 0 # Incrementer used to track unique payments
        self.pending_cashbacks = [] # List of list to track cashback information (timestamp, account_id, payment_id, amount)
        self.payments = {} # Tracks account_ID and it's corresponding payment_IDs.
        self.balance_history = {}
        self.merged_accounts = {}

    # TODO: implement interface methods here
    
    def create_account(self, timestamp: int, account_id: str) -> bool:
        print(f"---------------------------------------------------------------")
        print(f"CREATING {account_id}\n")
        # Return false if account already exists
        if account_id in self.accounts:
            return False
        # Initialize new account with balance of zero and return True
        self.accounts[account_id] = {
            "balance": 0,
            "outgoing": 0,
            "history": [(timestamp, 0)],
            
        }
        
        self.balance_history[account_id] = []

        self.update_balance_history(account_id, timestamp)

        return True

    def update_balance_history(self, account_id: str, timestamp: int):
        if account_id not in self.balance_history:
            self.balance_history = {}
        self.process_cashback(timestamp)
        history = list(self.accounts[account_id]["history"])
        self.balance_history[account_id].append((timestamp, history))

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # Return None if account does not exist
        if account_id not in self.accounts:
            return None
        # Process existing payments for cashback before running deposit operation
        self.process_cashback(timestamp)

        # Add given amount to provided account
        self.accounts[account_id]["balance"] += amount
        
        self.accounts[account_id]["history"].append((timestamp, self.accounts[account_id]["balance"]))
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
        
        # Process existing payments for cashback before running transfer operation



        self.process_cashback(timestamp)
        
    
        # trasfer funds from source to target
        self.accounts[source_account_id]["balance"] -= amount
        self.accounts[target_account_id]["balance"] += amount

        # Update outgoing transactions with transfered amount
        self.accounts[source_account_id]["outgoing"] += amount

        self.accounts[source_account_id]["history"].append((timestamp, self.accounts[source_account_id]["balance"]))
        self.accounts[target_account_id]["history"].append((timestamp, self.accounts[target_account_id]["balance"]))
        self.update_balance_history(source_account_id, timestamp)
        self.update_balance_history(target_account_id, timestamp)


        print(self.accounts[source_account_id])
        # return balance of source
        return self.accounts[source_account_id]["balance"]
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        print(f"---------------------------------------------------------------")
        print(f"MERGING {account_id_2} into {account_id_1} at timestamp {timestamp}\n")

        # Check account validity
        if account_id_1 == account_id_2 or account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False

        # Cashback for account 2 refunded to account 1
        for i, (cashback_time, account_id, payment_id, cashback) in enumerate(self.pending_cashbacks):
            if account_id == account_id_2:
                self.pending_cashbacks[i] = (cashback_time, account_id_1, payment_id, cashback)
        self.process_cashback(timestamp)
        
        # Update payment transactions
        self.payments[account_id_1] = self.payments.get(account_id_1, []) + self.payments.pop(account_id_2, [])

        if "original_history" not in self.accounts[account_id_1]:
            self.accounts[account_id_1]["original_history"] = list(self.accounts[account_id_1]["history"])

        # Add balance and outgoing transactions
        self.accounts[account_id_1]["balance"] += self.accounts[account_id_2]["balance"]
        self.accounts[account_id_1]["outgoing"] += self.accounts[account_id_2]["outgoing"]

        # Archive merged account's history sepcarately
        if "merged_from" not in self.accounts[account_id_1]:
            self.accounts[account_id_1]["merged_from"] = {}

        self.accounts[account_id_1]["merged_from"][account_id_2] = self.accounts[account_id_2]["history"]

        # Preserve original history of the target account
        original_history = list(self.accounts[account_id_1]["history"])  # Copy to preserve order
        self.accounts[account_id_1]["history"] = original_history + self.accounts[account_id_2]["history"]
        self.accounts[account_id_1]["history"].append((timestamp, self.accounts[account_id_1]["balance"]))
        self.accounts[account_id_1]["history"].sort()  # Ensure order

        # Add the merged account to the merged_accounts dictionary
        if account_id_2 not in self.merged_accounts:
            self.merged_accounts[account_id_2] = []
        
        # Store information about account_id_2 being merged into account_id_1
        self.merged_accounts[account_id_2].append((account_id_1, timestamp))

        # Mark merge timestamp
        self.accounts[account_id_1]["merged_timestamp"] = timestamp

        self.update_balance_history(account_id_1, timestamp)
        self.update_balance_history(account_id_2, timestamp)


        # Remove merged account
        del self.accounts[account_id_2]

        print(f"Account Info: {self.accounts[account_id_1]}")
        print(f"Balance History: {self.accounts[account_id_1]['merged_from']}")
        print(f"Original History: {self.accounts[account_id_1]['original_history']}")
        print(f"Merged Account: {self.merged_accounts[account_id_2]}")

        return True

    def get_balance_before(self, history: list, query_timestamp: int) -> int | None:
        """
        Retrieve the balance at the most recent timestamp before or equal to the given query timestamp.

        Args:
            history (list): A list of tuples, where each tuple contains a timestamp and account history.
            query_timestamp (int): The timestamp to query for the balance.

        Returns:
            int: The balance at the most recent timestamp before or equal to the query timestamp, or None if not found.
        """
        # Iterate over the history in reverse to find the most recent valid entry
        for timestamp, account_history in reversed(history):
            if timestamp <= query_timestamp:
                # Return the last balance from the account history at this timestamp
                if account_history:
                    return account_history[-1][1]  # The balance from the last entry in the history
        return None
    

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:

        if account_id not in self.accounts and account_id not in self.merged_accounts:
            return None
        
        self.process_cashback(timestamp)

        while account_id in self.merged_accounts:

            merged_time = self.merged_accounts[account_id][0][1]

            if time_at < merged_time:

                balance_history = self.balance_history.get(account_id, [])

                balance = self.get_balance_before(balance_history, time_at)

                return balance
            
            if time_at > merged_time and account_id in self.accounts:

                balance_history = self.balance_history.get(account_id, [])
                balance = self.get_balance_before(balance_history, timestamp)

                return balance

            else:

                return None
        
        if account_id in self.accounts: 

            account = self.accounts[account_id]

            merge_timestamp = account.get("merged_timestamp")

            # If merge timestamp exists and is after the queried timestamp, use original history
            if merge_timestamp:
                # If time of merge is after the queried timestamp, use original history
                if time_at < merge_timestamp:
                    # Select timestamp and balance from accounts original history
                    balance_history = self.balance_history.get(account_id, [])
                    balance = self.get_balance_before(balance_history, time_at)

                    return balance
                else:
                        
                    for time, balance in reversed(account["history"]):
                        if time <= time_at:
                            return balance
                
            
            else:
                print(self.accounts[account_id]["history"])
                for time, balance in reversed(self.accounts[account_id]["history"]):
                    if time <= time_at:
                        return balance

            return None

    def process_cashback(self, timestamp: int):
        print(f" Checking if cashback needs to be processed\n")
        # Access the variables of the pending_cashbacks list
        for cashback_time, account_id, payment_id, cashback in list(self.pending_cashbacks):

            # Only apply cashback if the timestamp exceeds 24 hours for a payment_ID
            if timestamp >= cashback_time:
                print("PROCESSING CASHBACK")
                # Add cashback amount
                self.accounts[account_id]["balance"] += cashback

                self.accounts[account_id]["history"].append((cashback_time, self.accounts[account_id]["balance"]))

                # Remove the pending cashback transaction after it has been processed
                self.pending_cashbacks.remove((cashback_time, account_id, payment_id, cashback))

    def pay(self, timestamp:int , account_id: str, amount:int) -> str | None:

        # DEBUG HEADER
        print(f"---------------------------------------------------------------")
        print(f"PAYING {amount} from {account_id}\n")

        # Process existing payments for cashback before running pay operation
        self.process_cashback(timestamp)

        # Return none if account id doesn't exist
        if account_id not in self.accounts:
            return None
        
        # Return none if account id has insufficient funds
        if self.accounts[account_id]["balance"] < amount:
            return None
        
        print(f" --- Successful Payment --- \n")
        

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

        # Update Balance History
        self.accounts[account_id]["history"].append((timestamp, self.accounts[account_id]["balance"]))

        self.update_balance_history(account_id, timestamp)

        print(self.accounts[account_id])
        # Return the payment_ID of the transaction
        return payment_id
    
    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:


        print(f"---------------------------------------------------------------")
        print(f"GETTING payment status for {payment} in {account_id}\n")
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

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        print(f"---------------------------------------------------------------")
        print(f"LISTING top {n} spenders\n")
        account_id = self.accounts
        self.process_cashback(timestamp)
        #sorted_trans = sorted(self.outgoing_transactions.items(), key=lambda item: item[1], reverse=True)
        sorted_trans = sorted(self.accounts.items(), key=lambda x: (-x[1]["outgoing"], x[0]))

        top_list = sorted_trans[:n]

        sorted_result = [f"{account_id}({data['outgoing']})" for account_id, data in top_list]

        print(f"Top {n} spenders: ")

        return sorted_result    

              
if __name__ == "__main__":
    
    bs = BankingSystemImpl()

    print(bs.create_account(1, 'account1'))
    print(bs.create_account(2, 'account4'))
    print(bs.create_account(3, 'account3'))
    print(bs.create_account(4, 'account2'))
    print(bs.deposit(5, "account1", 1000))
    print(bs.transfer(6, "account1", "account2", 500))
    print(bs.transfer(7, "account1", "account4", 100))
    print(bs.deposit(8, "account2", 1000))
    print(bs.transfer(9, 'account2', 'account2', 300))
    print(bs.deposit(10, 'account3', 1000))
    print(bs.transfer(11, 'account3', 'account2', 200))
    print(bs.pay(12, 'account3', 200))
    print(bs.deposit(13, 'account4', 1000))
    print(bs.pay(14, 'account4', 500))
    print(bs.get_payment_status(15, 'account3', 'payment1'))
    print(bs.get_payment_status(16, 'account4', 'payment2'))
    print(bs.top_spenders(17, 4))
    print(bs.merge_accounts(18, 'account2', 'account5'))
    print(bs.merge_accounts(19, 'account2', 'account3'))
    print(f"Account 3 Info: {bs.accounts['account2']["merged_from"]}")
    print(bs.top_spenders(20, 3))
    print(bs.merge_accounts(21, 'account2', 'account2'))
    print(bs.get_balance(22, 'account1', 17))
    print(bs.get_balance(23, 'account2', 3))
    print(bs.get_balance(24, 'account3', 20))
    #print(bs.get_balance(25, 'account4', 25))
    #print(bs.get_balance(26, 'account1', 15))
    #print(bs.get_balance(27, 'account2', 14))
    print(bs.get_balance(28, 'account3', 13))
    

    """


       
        self.assertEqual(self.system.get_balance(27, 'account2', 14), 1700)
        self.assertEqual(self.system.get_balance(28, 'account3', 13), 600)
        self.assertEqual(self.system.get_balance(29, 'account4', 12), 100)
        self.assertEqual(self.system.get_payment_status(86400012, 'account2', 'payment1'), 'CASHBACK_RECEIVED')
        self.assertEqual(self.system.get_payment_status(86400014, 'account4', 'payment2'), 'CASHBACK_RECEIVED')
        self.assertEqual(self.system.get_balance(86400015, 'account1', 86400014), 400)
        self.assertEqual(self.system.get_balance(86400016, 'account2', 86400014), 2304)
        self.assertIsNone(self.system.get_balance(86400017, 'account3', 86400014))
        self.assertEqual(self.system.get_balance(86400018, 'account4', 86400014), 610)

    """