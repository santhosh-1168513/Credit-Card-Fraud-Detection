"""
Sample Data Generator
Generate sample transaction data for testing and training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_sample_transactions(num_samples=1000, fraud_rate=0.05, output_file='sample_transactions.csv'):
    """
    Generate sample transaction data with fraud labels
    
    Args:
        num_samples (int): Number of transactions to generate
        fraud_rate (float): Proportion of fraudulent transactions
        output_file (str): Output CSV filename
    """
    np.random.seed(42)
    random.seed(42)
    
    # Merchants
    legitimate_merchants = [
        'Amazon', 'Walmart', 'Target', 'Best Buy', 'Costco',
        'Starbucks', 'McDonald\'s', 'Shell Gas', 'Chevron',
        'Apple Store', 'Home Depot', 'CVS Pharmacy'
    ]
    
    suspicious_merchants = [
        'Unknown Merchant', 'Cash Advance', 'Foreign Exchange',
        'Online Casino', 'Crypto Exchange'
    ]
    
    # Locations
    legitimate_locations = [
        'New York, NY', 'Los Angeles, CA', 'Chicago, IL',
        'Houston, TX', 'Phoenix, AZ', 'Philadelphia, PA',
        'San Antonio, TX', 'San Diego, CA', 'Dallas, TX',
        'San Jose, CA', 'Austin, TX', 'Jacksonville, FL'
    ]
    
    high_risk_locations = [
        'Lagos, Nigeria', 'Moscow, Russia', 'Kiev, Ukraine',
        'Unknown Location', 'Offshore'
    ]
    
    transactions = []
    
    # Calculate number of fraud and legitimate transactions
    num_fraud = int(num_samples * fraud_rate)
    num_legitimate = num_samples - num_fraud
    
    # Generate legitimate transactions
    for i in range(num_legitimate):
        transaction_id = f'TXN{i+1:05d}'
        
        # Normal spending patterns
        amount = np.random.lognormal(mean=4, sigma=1.5)  # Mean ~$55
        amount = round(max(5, min(amount, 2000)), 2)  # Cap at $2000
        
        merchant = random.choice(legitimate_merchants)
        location = random.choice(legitimate_locations)
        
        # Random timestamp within last 30 days, mostly during business hours
        days_ago = random.randint(0, 30)
        hour = random.choices(
            range(24),
            weights=[1,1,1,1,1,1,3,5,8,10,10,10,10,10,8,8,8,8,5,3,3,2,2,1],
            k=1
        )[0]
        minute = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hour, minutes=minute)
        
        card_number = f'****{random.randint(1000, 9999)}'
        
        is_fraud = 0
        
        transactions.append({
            'transaction_id': transaction_id,
            'amount': amount,
            'merchant': merchant,
            'location': location,
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            'card_number': card_number,
            'is_fraud': is_fraud
        })
    
    # Generate fraudulent transactions
    for i in range(num_fraud):
        transaction_id = f'TXN{num_legitimate + i + 1:05d}'
        
        # Fraud patterns
        fraud_type = random.choice(['high_amount', 'suspicious_merchant', 'late_night', 'high_risk_location'])
        
        if fraud_type == 'high_amount':
            # Unusually high amounts
            amount = round(random.uniform(3000, 10000), 2)
            merchant = random.choice(legitimate_merchants + suspicious_merchants)
            location = random.choice(legitimate_locations)
            hour = random.randint(0, 23)
            
        elif fraud_type == 'suspicious_merchant':
            # Suspicious merchants
            amount = round(random.uniform(500, 5000), 2)
            merchant = random.choice(suspicious_merchants)
            location = random.choice(legitimate_locations + high_risk_locations)
            hour = random.randint(0, 23)
            
        elif fraud_type == 'late_night':
            # Late night transactions
            amount = round(random.uniform(200, 3000), 2)
            merchant = random.choice(legitimate_merchants)
            location = random.choice(legitimate_locations)
            hour = random.randint(1, 5)  # 1 AM - 5 AM
            
        else:  # high_risk_location
            # High-risk locations
            amount = round(random.uniform(100, 5000), 2)
            merchant = random.choice(legitimate_merchants + suspicious_merchants)
            location = random.choice(high_risk_locations)
            hour = random.randint(0, 23)
        
        days_ago = random.randint(0, 30)
        minute = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hour, minutes=minute)
        
        card_number = f'****{random.randint(1000, 9999)}'
        
        is_fraud = 1
        
        transactions.append({
            'transaction_id': transaction_id,
            'amount': amount,
            'merchant': merchant,
            'location': location,
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            'card_number': card_number,
            'is_fraud': is_fraud
        })
    
    # Shuffle transactions
    random.shuffle(transactions)
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    # Print statistics
    print(f"✅ Generated {num_samples} sample transactions")
    print(f"📊 Statistics:")
    print(f"   - Total transactions: {len(df)}")
    print(f"   - Legitimate: {num_legitimate} ({(num_legitimate/num_samples)*100:.1f}%)")
    print(f"   - Fraudulent: {num_fraud} ({(num_fraud/num_samples)*100:.1f}%)")
    print(f"   - Amount range: ${df['amount'].min():.2f} - ${df['amount'].max():.2f}")
    print(f"   - Average amount: ${df['amount'].mean():.2f}")
    print(f"📁 Saved to: {output_file}")
    
    return df


def generate_test_data(num_samples=100, output_file='test_transactions.csv'):
    """
    Generate test transaction data without fraud labels
    
    Args:
        num_samples (int): Number of transactions to generate
        output_file (str): Output CSV filename
    """
    df = generate_sample_transactions(num_samples, fraud_rate=0.10, output_file=output_file)
    
    # Remove is_fraud column for testing
    df_test = df.drop('is_fraud', axis=1)
    df_test.to_csv(output_file, index=False)
    
    print(f"\n✅ Generated {num_samples} test transactions (without labels)")
    print(f"📁 Saved to: {output_file}")
    
    return df_test


if __name__ == '__main__':
    print("=" * 60)
    print("FraudGuard - Sample Data Generator")
    print("=" * 60)
    print()
    
    # Generate training data (with labels)
    print("1️⃣  Generating TRAINING data (with fraud labels)...")
    print("-" * 60)
    generate_sample_transactions(
        num_samples=1000,
        fraud_rate=0.05,
        output_file='training_data.csv'
    )
    
    print()
    print("-" * 60)
    
    # Generate test data (without labels)
    print("\n2️⃣  Generating TEST data (without fraud labels)...")
    print("-" * 60)
    generate_test_data(
        num_samples=100,
        output_file='test_transactions.csv'
    )
    
    print()
    print("=" * 60)
    print("✨ Data generation complete!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Train model: curl -X POST -F 'file=@training_data.csv' http://localhost:5000/api/train")
    print("   2. Test predictions: curl -X POST -F 'file=@test_transactions.csv' http://localhost:5000/api/predict")
    print()