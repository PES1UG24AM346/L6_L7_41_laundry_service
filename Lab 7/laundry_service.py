import math


def parse_order(text):
    """
    Parses a garment and weight string formatted as 'garment:weight'.
    Returns (garment_title, weight_in_kg) or None if input is invalid.
    """
    if not isinstance(text, str):
        return None
    try:
        parts = text.split(':')
        if len(parts) != 2:
            return None
        garment = parts[0].strip().title()
        if not garment:
            return None
        weight = float(parts[1].strip())
        if math.isnan(weight) or math.isinf(weight) or weight < 0:
            return None
        return garment, weight
    except Exception:
        return None


def weight_average(weights_csv):
    """
    Computes integer average of comma-separated weights.
    Returns integer average or 0 if input is invalid or empty.
    """
    if not isinstance(weights_csv, str):
        return 0
    try:
        parts = weights_csv.split(',')
        values = []
        for r in parts:
            s = r.strip()
            if not s:
                continue
            val = int(s)
            if val < 0:
                return 0
            values.append(val)
        if not values:
            return 0
        return sum(values) // len(values)
    except Exception:
        return 0


def payable_charge(text):
    """
    Calculates total payable charge after 18% tax and discount from 'charge|discount'.
    Returns max(total, 0) or 0 on invalid input.
    """
    if not isinstance(text, str):
        return 0
    try:
        parts = text.split('|')
        if len(parts) != 2:
            return 0
        charge = float(parts[0].strip())
        discount = float(parts[1].strip())
        if math.isnan(charge) or math.isnan(discount) or math.isinf(charge) or math.isinf(discount):
            return 0
        if charge < 0 or discount < 0:
            return 0
        total = charge * 1.18 - discount
        return max(total, 0)
    except Exception:
        return 0


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter garment:weight in kg (e.g. regular:6): ")
    result = parse_order(user_input)
    print("Garment and Weight:", result)

    print("\n==== Running weight_average ====")
    user_input = input("Enter garment weights as CSV (e.g. 3,5,8): ")
    result = weight_average(user_input)
    print("Average Weight:", result)

    print("\n==== Running payable_charge ====")
    user_input = input("Enter charge|discount (e.g. 300|40): ")
    result = payable_charge(user_input)
    print("Payable Charge:", result)


if __name__ == "__main__":
    main()
