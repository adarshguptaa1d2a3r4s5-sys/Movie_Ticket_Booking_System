SEAT_PRICES = {
    'Regular': 200.0,
    'Premium': 350.0,
    'Recliner': 600.0
}

def calculate_seat_price(seat_type):
    """Returns the base price of a seat given its type."""
    return SEAT_PRICES.get(seat_type, 200.0)

def calculate_booking_price(seats_list):
    """
    Calculates detailed pricing for a booking given a list of seat objects or dictionaries containing seat_type.
    
    Returns a dict with:
        subtotal: Sum of individual seat prices
        gst: 18% of subtotal
        convenience_fee: Flat ₹30 fee
        grand_total: subtotal + gst + convenience_fee
    """
    if not seats_list:
        return {
            'subtotal': 0.0,
            'gst': 0.0,
            'convenience_fee': 0.0,
            'grand_total': 0.0
        }
        
    subtotal = 0.0
    for seat in seats_list:
        # Support both objects and dictionaries
        if hasattr(seat, 'seat_type'):
            subtotal += calculate_seat_price(seat.seat_type)
        elif isinstance(seat, dict):
            subtotal += calculate_seat_price(seat.get('seat_type', 'Regular'))
        else:
            subtotal += 200.0  # Default fallback
            
    gst = round(subtotal * 0.18, 2)
    convenience_fee = 30.0
    grand_total = round(subtotal + gst + convenience_fee, 2)
    
    return {
        'subtotal': round(subtotal, 2),
        'gst': gst,
        'convenience_fee': convenience_fee,
        'grand_total': grand_total
    }
