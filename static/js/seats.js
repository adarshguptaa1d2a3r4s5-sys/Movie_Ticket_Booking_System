// state variables
let selectedSeats = [];
const maxSeats = 10;
const GST_RATE = 0.18;
const CONVENIENCE_FEE = 30.0;

document.addEventListener('DOMContentLoaded', () => {
    const seatNodes = document.querySelectorAll('.seat-node.available');
    
    seatNodes.forEach(node => {
        node.addEventListener('click', () => {
            const seatId = parseInt(node.getAttribute('data-seat-id'));
            const seatNumber = node.getAttribute('data-seat-number');
            const seatType = node.getAttribute('data-seat-type');
            const seatPrice = parseFloat(node.getAttribute('data-seat-price'));
            
            toggleSeatSelection(node, seatId, seatNumber, seatType, seatPrice);
        });
    });
    
    // Page lock countdown timer (if on seat page or payment page)
    initializeCountdownTimer();
});

function toggleSeatSelection(node, seatId, seatNumber, seatType, seatPrice) {
    const index = selectedSeats.findIndex(s => s.id === seatId);
    
    if (index > -1) {
        // Deselect seat
        selectedSeats.splice(index, 1);
        node.classList.remove('selected');
        
        // Optionally emit unlock request immediately to release resources
        releaseSeatLock(seatId);
    } else {
        // Limit maximum seats
        if (selectedSeats.length >= maxSeats) {
            alert(`You can select a maximum of ${maxSeats} seats per booking.`);
            return;
        }
        
        // Select seat
        selectedSeats.push({
            id: seatId,
            number: seatNumber,
            type: seatType,
            price: seatPrice
        });
        node.classList.add('selected');
        
        // Lock seat immediately in backend
        acquireSeatLock(seatId);
    }
    
    updatePricingBreakdown();
}

function acquireSeatLock(seatId) {
    const showId = document.getElementById('show-id-val').value;
    fetch('/book/lock-seats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            show_id: parseInt(showId),
            seat_ids: [seatId]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            // Backend rejected lock (e.g. already taken)
            alert(data.message || 'Seat is currently unavailable.');
            // Remove seat visually
            const node = document.querySelector(`.seat-node[data-seat-id="${seatId}"]`);
            if (node) {
                node.classList.remove('selected');
                node.classList.add('booked');
            }
            selectedSeats = selectedSeats.filter(s => s.id !== seatId);
            updatePricingBreakdown();
        }
    })
    .catch(err => {
        console.error('Lock error:', err);
    });
}

function releaseSeatLock(seatId) {
    const showId = document.getElementById('show-id-val').value;
    fetch('/book/unlock-seats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            show_id: parseInt(showId),
            seat_ids: [seatId]
        })
    })
    .catch(err => console.error('Unlock error:', err));
}

function updatePricingBreakdown() {
    const selectedListEl = document.getElementById('selected-seats-list');
    const subtotalEl = document.getElementById('price-subtotal');
    const gstEl = document.getElementById('price-gst');
    const convenienceEl = document.getElementById('price-conv');
    const totalEl = document.getElementById('price-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const seatInputsContainer = document.getElementById('seat-inputs-container');
    
    // Clear dynamic inputs
    seatInputsContainer.innerHTML = '';
    
    if (selectedSeats.length === 0) {
        selectedListEl.innerText = 'None';
        subtotalEl.innerText = '₹0.00';
        gstEl.innerText = '₹0.00';
        convenienceEl.innerText = '₹0.00';
        totalEl.innerText = '₹0.00';
        checkoutBtn.disabled = true;
        return;
    }
    
    // Sort selected seats by row/col for clean formatting
    selectedSeats.sort((a, b) => a.number.localeCompare(b.number));
    
    // Format list
    const seatNames = selectedSeats.map(s => s.number).join(', ');
    selectedListEl.innerText = seatNames;
    
    // Calculate values
    let subtotal = 0;
    selectedSeats.forEach(s => {
        subtotal += s.price;
        
        // Append input to checkout form
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'seat_ids';
        hiddenInput.value = s.id;
        seatInputsContainer.appendChild(hiddenInput);
    });
    
    const gst = subtotal * GST_RATE;
    const grandTotal = subtotal + gst + CONVENIENCE_FEE;
    
    // Update DOM
    subtotalEl.innerText = `₹${subtotal.toFixed(2)}`;
    gstEl.innerText = `₹${gst.toFixed(2)}`;
    convenienceEl.innerText = `₹${CONVENIENCE_FEE.toFixed(2)}`;
    totalEl.innerText = `₹${grandTotal.toFixed(2)}`;
    checkoutBtn.disabled = false;
}

// Countdown timer helper
function initializeCountdownTimer() {
    const timerDisplay = document.getElementById('countdown-timer');
    if (!timerDisplay) return;
    
    let timeRemaining = parseInt(timerDisplay.getAttribute('data-seconds-left')) || 300;
    
    const timerInterval = setInterval(() => {
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            timerDisplay.innerText = "00:00";
            alert("Your seat hold has expired. Page will reload to reset seat states.");
            window.location.reload();
            return;
        }
        
        timeRemaining--;
        
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        
        const minutesStr = String(minutes).padStart(2, '0');
        const secondsStr = String(seconds).padStart(2, '0');
        
        timerDisplay.innerText = `${minutesStr}:${secondsStr}`;
    }, 1000);
}
