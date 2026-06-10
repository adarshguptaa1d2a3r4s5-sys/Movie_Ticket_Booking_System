import qrcode
import io
import json
import base64

def generate_qr_base64(booking_reference, movie_title, seats):
    """
    Generates a QR Code as a base64-encoded PNG data URI containing the booking metadata.
    
    Format:
    {
      "booking_id": "MOV789123",
      "movie": "Avengers",
      "seats": ["A3","A4"]
    }
    """
    payload = {
        "booking_id": booking_reference,
        "movie": movie_title,
        "seats": seats
    }
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2
    )
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    
    base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_encoded}"

def generate_qr_image_bytes(booking_reference, movie_title, seats):
    """Generates and returns raw PNG bytes for a QR code (useful for ReportLab PDFs)."""
    payload = {
        "booking_id": booking_reference,
        "movie": movie_title,
        "seats": seats
    }
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2
    )
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()
