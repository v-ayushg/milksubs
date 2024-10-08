from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Route to handle subscription form submission
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    vacation_dates_str = data.get('vacation_dates', [])

    try:
        # Validate and parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        if end_date < start_date:
            return jsonify({"error": "End date cannot be before start date."}), 400

        # Convert vacation dates to datetime objects
        vacation_dates = []
        for vac_date_str in vacation_dates_str:
            vac_date = datetime.strptime(vac_date_str, '%Y-%m-%d')
            vacation_dates.append(vac_date)

        # Calculate initial subscription days
        total_days = (end_date - start_date).days + 1  # Include both start and end date

        # Adjust subscription duration by adding vacation days
        num_vacation_days = len(vacation_dates)
        adjusted_end_date = end_date + timedelta(days=num_vacation_days)

        # Generate the list of subscription dates including extensions
        adjusted_total_days = (adjusted_end_date - start_date).days + 1
        subscription_dates = [start_date + timedelta(days=i) for i in range(adjusted_total_days)]

        # Exclude vacation dates from delivery days
        delivery_days = [date for date in subscription_dates if date not in vacation_dates]

        # Calculate the final number of valid delivery days
        subscription_duration_days = len(delivery_days)

        # Format vacation dates for display
        vacation_dates_str = ', '.join([vac.strftime('%d %b %Y') for vac in vacation_dates])

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format."}), 400

    # Confirmation message with adjusted end date and vacation dates
    confirmation_message = f"Subscription for {subscription_duration_days} day(s) confirmed from {start_date.strftime('%d %b %Y')} to {adjusted_end_date.strftime('%d %b %Y')}."
    
    if vacation_dates:
        confirmation_message += f" Milk will not be delivered on: {vacation_dates_str}."

    return jsonify({"message": confirmation_message})

if __name__ == '__main__':
    app.run(debug=True)
