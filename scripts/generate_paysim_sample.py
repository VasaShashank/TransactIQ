import os
import random
import pandas as pd

def generate_sample_paysim(output_path: str, num_records: int = 1500):
    random.seed(42)

    customers = [f"C{random.randint(1000000, 9999999)}" for _ in range(300)]
    merchants = [f"M{random.randint(1000000, 9999999)}" for _ in range(100)]
    
    txn_types = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
    
    records = []

    # Generate standard PaySim transactions
    for step in range(1, 100):
        for _ in range(num_records // 100):
            ttype = random.choices(txn_types, weights=[0.4, 0.25, 0.25, 0.05, 0.05])[0]
            orig = random.choice(customers)
            dest = random.choice(merchants if ttype in ["PAYMENT", "CASH_OUT"] else customers)
            amount = round(random.uniform(10.0, 50000.0), 2)
            
            old_orig = round(random.uniform(amount, amount + 100000.0), 2)
            new_orig = round(old_orig - amount, 2)
            old_dest = round(random.uniform(0.0, 50000.0), 2)
            new_dest = round(old_dest + amount, 2)

            # Genuine fraud occurrence logic (high value transfer/cashout with balance clear)
            is_fraud = 0
            is_flagged = 0
            if ttype in ["TRANSFER", "CASH_OUT"] and amount > 200000.0 and random.random() < 0.15:
                is_fraud = 1
                if amount > 300000.0:
                    is_flagged = 1

            records.append({
                "step": step,
                "type": ttype,
                "amount": amount,
                "nameOrig": orig,
                "oldbalanceOrg": old_orig,
                "newbalanceOrig": new_orig,
                "nameDest": dest,
                "oldbalanceDest": old_dest,
                "newbalanceDest": new_dest,
                "isFraud": is_fraud,
                "isFlaggedFraud": is_flagged
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated PaySim dataset with {len(df)} transactions at {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "..", "paysim.csv")
    generate_sample_paysim(out_file)
