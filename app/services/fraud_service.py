def calculate_fraud_score(amount, country):
    score = 0

    if amount > 1000:
        score += 50

    if country != "SG":
        score += 30

    return min(score, 100)