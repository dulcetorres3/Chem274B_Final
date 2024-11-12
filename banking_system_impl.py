from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # Dictionary containing account_id (key) and amount (value)
        self.accounts = {}

    # TODO: implement interface methods here
    def create_account(self, timestamp: int, account_id: str) -> bool:
        
        # Return false if account already exists
        if account_id in self.accounts:
            return False
            
        # Initialize new account with balance of zero and return True
        self.accounts[account_id] = 0
        return True
        
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
      
        # Return None if account does not exist
        if account_id not in self.accounts:
            return None
            
        # Add given amount to provided account
        self.accounts[account_id] += amount
      
        # Return the new balance of the account
        return self.accounts[account_id]
          