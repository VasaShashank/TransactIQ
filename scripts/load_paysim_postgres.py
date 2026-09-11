import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.config import settings

def load_paysim_to_postgres(csv_path: str, chunk_size: int = 50000):
    if not os.path.exists(csv_path):
        print(f"Error: PaySim CSV not found at {csv_path}")
        return

    print(f"Connecting to PostgreSQL at {settings.get_database_url()}...")
    engine = create_engine(settings.get_database_url())

    # Ensure tables exist
    from app.core.database import Base
    from app.models import User, Account, Transaction, Case, AuditLog
    Base.metadata.create_all(bind=engine)

    print(f"Loading {csv_path} in chunks of {chunk_size}...")
    start_time = time.time()
    total_txns = 0

    with engine.begin() as conn:
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk_start = time.time()
            
            # Extract distinct accounts from nameOrig and nameDest
            orig_accounts = chunk[['nameOrig']].rename(columns={'nameOrig': 'id'})
            orig_accounts['node_type'] = orig_accounts['id'].apply(lambda x: 'MERCHANT' if x.startswith('M') else 'CUSTOMER')
            
            dest_accounts = chunk[['nameDest']].rename(columns={'nameDest': 'id'})
            dest_accounts['node_type'] = dest_accounts['id'].apply(lambda x: 'MERCHANT' if x.startswith('M') else 'CUSTOMER')

            all_accounts = pd.concat([orig_accounts, dest_accounts]).drop_duplicates(subset=['id'])

            # Upsert Accounts using raw SQL ON CONFLICT DO NOTHING
            account_records = all_accounts.to_dict(orient='records')
            conn.execute(
                text("""
                    INSERT INTO accounts (id, node_type)
                    VALUES (:id, :node_type)
                    ON CONFLICT (id) DO NOTHING
                """),
                account_records
            )

            # Insert Transactions
            txns = chunk.rename(columns={
                'nameOrig': 'orig_account_id',
                'nameDest': 'dest_account_id',
                'oldbalanceOrg': 'old_balance_orig',
                'newbalanceOrig': 'new_balance_orig',
                'oldbalanceDest': 'old_balance_dest',
                'newbalanceDest': 'new_balance_dest',
                'isFraud': 'is_fraud',
                'isFlaggedFraud': 'is_flagged_fraud'
            })
            
            txn_records = txns[[
                'step', 'type', 'amount', 'orig_account_id', 'dest_account_id',
                'old_balance_orig', 'new_balance_orig', 'old_balance_dest',
                'new_balance_dest', 'is_fraud', 'is_flagged_fraud'
            ]].to_dict(orient='records')

            conn.execute(
                text("""
                    INSERT INTO transactions (
                        step, type, amount, orig_account_id, dest_account_id,
                        old_balance_orig, new_balance_orig, old_balance_dest,
                        new_balance_dest, is_fraud, is_flagged_fraud
                    ) VALUES (
                        :step, :type, :amount, :orig_account_id, :dest_account_id,
                        :old_balance_orig, :new_balance_orig, :old_balance_dest,
                        :new_balance_dest, :is_fraud, :is_flagged_fraud
                    )
                """),
                txn_records
            )

            total_txns += len(chunk)
            print(f"Loaded chunk of {len(chunk)} txns ({total_txns} total) in {time.time() - chunk_start:.2f}s")

    print(f"Successfully loaded {total_txns} transactions into PostgreSQL in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "..", "paysim.csv")
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    load_paysim_to_postgres(csv_file)
