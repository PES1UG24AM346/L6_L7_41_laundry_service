INCLUDED_KG = {"regular": 5, "delicate": 3, "bedding": 8}


def extra_weight_charge(garment_type, weight_kg, speed, is_member):
    if garment_type not in INCLUDED_KG:
        raise ValueError("unknown garment type")
    if weight_kg < 0:
        raise ValueError("invalid weight")
    included = INCLUDED_KG[garment_type]
    if is_member and garment_type != "bedding":
        included += 2
    extra = weight_kg - included
    if extra <= 0:
        return 0
    if speed == "standard":
        rate = 30
    else:
        rate = 50
    if extra > 10:
        rate = rate + 15
        if speed == "express":
            rate += 10
    return extra * rate


def order_acceptable(weight_kg, items, is_delicate):
    if is_delicate:
        return items <= 5
    if weight_kg > 25:
        return False
    return items <= 40


def dropoff_status(minutes_before_closing, has_bedding, is_express):
    if has_bedding:
        cutoff = 90
    else:
        cutoff = 60
    if is_express:
        cutoff += 30
    if minutes_before_closing >= cutoff:
        return "accepted"
    elif minutes_before_closing >= cutoff - 20:
        return "late"
    return "rejected"
