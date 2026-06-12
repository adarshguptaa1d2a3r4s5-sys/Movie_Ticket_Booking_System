import io
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort, send_file
from flask_login import login_required, current_user

from models.db import db
from models.show import Show
from models.seat import Seat
from models.booking import Booking
from utils.price_calculator import calculate_booking_price
from utils.qr_generator import generate_qr_base64, generate_qr_image_bytes
from utils.pdf_generator import generate_ticket_pdf

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/show/<int:show_id>')
@login_required
def seat_selection(show_id):
    show = Show.query.get_or_404(show_id)
    
    # Automatically clear/expire old locks across the whole show to keep database clean
    now = datetime.utcnow()
    expired_seats = Seat.query.filter(
        Seat.show_id == show_id,
        Seat.locked_until < now,
        Seat.is_booked == False
    ).all()
    for s in expired_seats:
        s.locked_by_user_id = None
        s.locked_until = None
    db.session.commit()
    
    # Query all seats for this show
    seats = Seat.query.filter_by(show_id=show_id).order_by(Seat.seat_number).all()
    
    # Group seats by row (A, B, C, D, E)
    rows = {}
    for seat in seats:
        row_letter = seat.seat_number[0]
        if row_letter not in rows:
            rows[row_letter] = []
        rows[row_letter].append(seat)
        
    return render_template(
        'seat_selection.html',
        show=show,
        rows=rows,
        current_time=now
    )

@booking_bp.route('/book/lock-seats', methods=['POST'])
@login_required
def lock_seats():
    data = request.get_json() or {}
    show_id = data.get('show_id')
    seat_ids = data.get('seat_ids', [])
    
    if not show_id or not seat_ids:
        return jsonify({'success': False, 'message': 'Invalid parameters.'}), 400
        
    # Fetch show and seats
    seats = Seat.query.filter(Seat.id.in_(seat_ids), Seat.show_id == show_id).all()
    if len(seats) != len(seat_ids):
        return jsonify({'success': False, 'message': 'Some selected seats are invalid.'}), 400
        
    now = datetime.utcnow()
    # Check if any seat is already booked or locked by another user
    for seat in seats:
        if seat.is_booked:
            return jsonify({'success': False, 'message': f'Seat {seat.seat_number} is already booked.'}), 400
        if seat.is_currently_locked() and seat.locked_by_user_id != current_user.id:
            return jsonify({'success': False, 'message': f'Seat {seat.seat_number} is currently locked by another customer.'}), 400
            
    # Apply 5-minute lock
    lock_time = now + timedelta(minutes=5)
    for seat in seats:
        seat.locked_by_user_id = current_user.id
        seat.locked_until = lock_time
        
    db.session.commit()
    return jsonify({
        'success': True,
        'locked_until': lock_time.isoformat() + 'Z',
        'message': 'Seats locked successfully.'
    })

@booking_bp.route('/book/unlock-seats', methods=['POST'])
@login_required
def unlock_seats():
    data = request.get_json() or {}
    show_id = data.get('show_id')
    seat_ids = data.get('seat_ids', [])
    
    if not show_id or not seat_ids:
        return jsonify({'success': False, 'message': 'Invalid parameters.'}), 400
        
    seats = Seat.query.filter(
        Seat.id.in_(seat_ids), 
        Seat.show_id == show_id, 
        Seat.locked_by_user_id == current_user.id
    ).all()
    
    for seat in seats:
        seat.locked_by_user_id = None
        seat.locked_until = None
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Seats unlocked successfully.'})

@booking_bp.route('/book/checkout', methods=['POST'])
@login_required
def checkout():
    show_id = request.form.get('show_id')
    selected_seat_ids = request.form.getlist('seat_ids')
    
    if not show_id or not selected_seat_ids:
        flash('Please select at least one seat to proceed.', 'warning')
        return redirect(url_for('movies.home'))
        
    show = Show.query.get_or_404(show_id)
    seat_ids = [int(sid) for sid in selected_seat_ids]
    
    # Verify locks are still active and valid
    seats = Seat.query.filter(Seat.id.in_(seat_ids), Seat.show_id == show_id).all()
    now = datetime.utcnow()
    
    for seat in seats:
        if seat.is_booked:
            flash(f'Seat {seat.seat_number} is already booked.', 'danger')
            return redirect(url_for('booking.seat_selection', show_id=show_id))
        # If lock has expired or is held by someone else
        if seat.locked_by_user_id != current_user.id or (seat.locked_until and seat.locked_until < now):
            flash(f'Your hold on seat {seat.seat_number} has expired. Please select your seats again.', 'danger')
            return redirect(url_for('booking.seat_selection', show_id=show_id))
            
    # Secure price calculations
    price_details = calculate_booking_price(seats)
    
    # Create Pending Booking
    # Create Pending Booking without kwargs to avoid init errors
    booking = Booking()
    booking.user_id = current_user.id
    booking.show_id = show.id
    booking.booking_reference = Booking.generate_reference()
    booking.total_price = price_details['grand_total']
    booking.payment_status = 'Pending'
    
    # Associate locked seats with the booking
    booking.seats.extend(seats)
    db.session.add(booking)
    db.session.commit()
    
    return redirect(url_for('booking.payment_gateway', booking_id=booking.id))

@booking_bp.route('/book/payment-gateway/<int:booking_id>')
@login_required
def payment_gateway(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Safety checks
    if booking.user_id != current_user.id:
        abort(403)
    if booking.payment_status != 'Pending':
        flash('This booking is already processed.', 'info')
        return redirect(url_for('auth.profile'))
        
    price_breakdown = calculate_booking_price(booking.seats)
    
    # Calculate remaining lock time in seconds
    now = datetime.utcnow()
    min_lock_time = None
    for seat in booking.seats:
        if seat.locked_until:
            if min_lock_time is None or seat.locked_until < min_lock_time:
                min_lock_time = seat.locked_until
                
    remaining_seconds = 300  # Default 5 minutes
    if min_lock_time:
        diff = min_lock_time - now
        remaining_seconds = max(0, int(diff.total_seconds()))
        
    if remaining_seconds <= 0:
        # Lock expired already! Clean up and reject checkout
        for seat in booking.seats:
            seat.locked_by_user_id = None
            seat.locked_until = None
        db.session.delete(booking)
        db.session.commit()
        flash('Payment time limit exceeded. Please select seats again.', 'danger')
        return redirect(url_for('booking.seat_selection', show_id=booking.show_id))
        
    return render_template(
        'payment_gateway.html',
        booking=booking,
        price=price_breakdown,
        remaining_seconds=remaining_seconds
    )

@booking_bp.route('/book/pay/<int:booking_id>', methods=['POST'])
@login_required
def process_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
        
    payment_method = request.form.get('payment_method')
    payment_action = request.form.get('action')  # 'success' or 'cancel'
    
    if payment_action == 'success':
        # Confirm booking
        booking.payment_status = 'Confirmed'
        
        # Confirm booked seats and release hold parameters
        for seat in booking.seats:
            seat.is_booked = True
            seat.locked_by_user_id = None
            seat.locked_until = None
            
        db.session.commit()
        
        # Simulating console logs / notification reminders
        print(f"[NOTIFICATION] Booking confirmation sent to {current_user.email} for Reference: {booking.booking_reference}")
        print(f"[REMINDER] Show reminder: '{booking.show.movie.title}' is scheduled at {booking.show.show_time.strftime('%I:%M %p')} on {booking.show.show_date.strftime('%B %d, %Y')} at {booking.show.theatre.name}.")
        
        flash('Payment Successful! Your tickets have been booked.', 'success')
        return redirect(url_for('booking.booking_confirmation', booking_id=booking.id))
    else:
        # Customer cancelled payment or payment failed
        # Free locked seats
        for seat in booking.seats:
            seat.locked_by_user_id = None
            seat.locked_until = None
            
        db.session.delete(booking)
        db.session.commit()
        
        flash('Payment cancelled or transaction failed. Seats have been unlocked.', 'warning')
        return redirect(url_for('booking.seat_selection', show_id=booking.show_id))

@booking_bp.route('/book/confirmation/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
        
    if booking.payment_status != 'Confirmed':
        flash('Please complete payment first.', 'warning')
        return redirect(url_for('booking.payment_gateway', booking_id=booking.id))
        
    # Generate Base64 QR code for direct inline display
    seats_list = [s.seat_number for s in booking.seats]
    qr_code_base64 = generate_qr_base64(booking.booking_reference, booking.show.movie.title, seats_list)
    
    price_details = calculate_booking_price(booking.seats)
    
    return render_template(
        'booking_confirmation.html',
        booking=booking,
        qr_code=qr_code_base64,
        price=price_details
    )

@booking_bp.route('/book/ticket/<int:booking_id>/download')
@login_required
def download_ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Admins can download any ticket; standard users can only download their own
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    if booking.payment_status != 'Confirmed':
        flash('Ticket has not been confirmed.', 'danger')
        return redirect(url_for('auth.profile'))
        
    # Generate QR bytes
    seats_list = [s.seat_number for s in booking.seats]
    qr_bytes = generate_qr_image_bytes(booking.booking_reference, booking.show.movie.title, seats_list)
    
    # Generate PDF
    pdf_data = generate_ticket_pdf(booking, qr_bytes)
    
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"ticket_{booking.booking_reference}.pdf"
    )

@booking_bp.route('/book/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
        
    # Check if show time has passed
    show_datetime = datetime.combine(booking.show.show_date, booking.show.show_time)
    if show_datetime < datetime.utcnow():
        flash('Cannot cancel a show that has already started or ended.', 'danger')
        return redirect(url_for('auth.profile'))
        
    if booking.payment_status != 'Confirmed':
        flash('Only confirmed bookings can be cancelled.', 'danger')
        return redirect(url_for('auth.profile'))
        
    # Cancel the booking
    booking.payment_status = 'Cancelled'
    
    # Free the booked seats
    for seat in booking.seats:
        seat.is_booked = False
        seat.locked_by_user_id = None
        seat.locked_until = None
        
    db.session.commit()
    
    # Simulating cancellation email console logging
    print(f"[NOTIFICATION] Booking Cancellation processed for Reference: {booking.booking_reference}. Refund initiated.")
    
    flash('Booking cancelled successfully. Refund will be processed back to your original payment method.', 'success')
    return redirect(url_for('auth.profile'))