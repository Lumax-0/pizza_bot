from flask import Flask, render_template, request, redirect, url_for
from database import get_bookings, init_db, delete_booking

app = Flask(__name__)

init_db()

@app.route('/')
def bookings():
    data = get_bookings() # заявки
    return render_template('bookings.html', bookings=data)

@app.route('/delete/<int:booking_id>', methods=['POST'])
def delete(booking_id):
    delete_booking(booking_id)
    return redirect(url_for('bookings'))

if __name__ == "__main__":
    app.run(debug=True)