class FraudService:

    def evaluate(self, amount: float):
        score = 0
        if amount > 5000:
            score += 80
        if amount > 1000:
            score += 40
        if score >= 70:
            return score, "DECLINE"
        if score >= 40:
            return score, "REVIEW"
        return score, "APPROVE"