from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a random secure string

# ---------------- DB CONNECTION ---------------- #
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="77601",
        database="echallan",
        autocommit=False  # Kept False so transaction rollback works correctly
    )

# Helper function to protect police routes
def is_logged_in():
    return session.get('logged_in') == True

# ---------------- HOME ---------------- #
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- USER SEARCH ---------------- #
@app.route('/search', methods=['POST'])
def search():
    reg_no = request.form['reg_no'].strip().upper()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Challan WHERE reg_no=%s", (reg_no,))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('result.html', data=data, reg_no=reg_no)

# ---------------- PAYMENT DASHBOARD ---------------- #
@app.route('/payment', methods=['POST'])
def payment():
    challan_id = request.form['challan_id']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Challan WHERE id=%s", (challan_id,))
    challan = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('payment.html', challan=challan)

# ---------------- POLICE LOGIN ---------------- #
@app.route('/police', methods=['GET', 'POST'])
def police_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.login_id, p.username, pd.officer_name
            FROM Police p
            INNER JOIN Police_Details pd ON p.police_id = pd.police_id
            WHERE p.username=%s AND p.password=%s
        """, (username, password))

        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['login_id'] = user['login_id']
            session['officer_name'] = user['officer_name']
            return redirect(url_for('police_dashboard'))
        else:
            return render_template('police_login.html', error="Invalid Credentials")

    return render_template('police_login.html')


# ---------------- POLICE DASHBOARD ---------------- #
@app.route('/police_dashboard')
def police_dashboard():
    if not is_logged_in():
        return redirect(url_for('police_login'))
        
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Fetch up to 50 recent records to show on the dashboard summary table
        cursor.execute("SELECT * FROM Challan ORDER BY id DESC LIMIT 50")
        challans = cursor.fetchall()
    except Exception as e:
        print("DASHBOARD DATA FETCH ERROR:", e)
        challans = []
    finally:
        cursor.close()
        db.close()

    # Pass profile details along with table data to align with dashboard.html variables
    return render_template(
        'police_dashboard.html', 
        officer_name=session.get('officer_name'), 
        login_id=session.get('login_id'),
        username=session.get('username'),
        challans=challans
    )

# ---------------- ADD CHALLAN ---------------- #
@app.route('/add', methods=['POST'])
def add():
    if not is_logged_in():
        return "Unauthorized Access", 403

    db = get_db_connection()
    cursor = db.cursor()

    try:
        reg_no = request.form['reg_no'].strip().upper()
        violation = request.form['violation']
        location = request.form['location']
        fine = request.form['fine']

        # Check registered vehicle
        cursor.execute("SELECT * FROM RegisteredVehicle WHERE reg_no=%s", (reg_no,))
        vehicle = cursor.fetchone()

        if not vehicle:
            return """
            <script>
                alert('Vehicle Not Registered ❌');
                window.location.href='/police_dashboard';
            </script>
            """

        # Add challan
        cursor.execute(
            """
            INSERT INTO Challan (reg_no, violation, location, fine, status)
            VALUES (%s, %s, %s, %s, 'Unpaid')
            """,
            (reg_no, violation, location, fine)
        )
        db.commit()

        return """
        <script>
            alert('Challan Added Successfully ✅');
            window.location.href='/police_dashboard';
        </script>
        """

    except Exception as e:
        print("ERROR ADDING CHALLAN:", e)
        db.rollback()
        return """
        <script>
            alert('Error Adding Challan ❌');
            window.location.href='/police_dashboard';
        </script>
        """
    finally:
        cursor.close()
        db.close()

# ---------------- PAYMENT PROCESS (USER) ---------------- #
@app.route('/pay', methods=['POST'])
def pay():
    challan_id = request.form.get('challan_id')
    mode = request.form.get('mode')

    if not challan_id or not mode:
        return "<h2>Invalid Payment Details ❌</h2><a href='/'>Go Home</a>"

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        # 1. Fetch challan data first to verify entry details
        cursor.execute("SELECT reg_no, violation, fine FROM Challan WHERE id=%s", (challan_id,))
        challan = cursor.fetchone()

        if not challan:
            return "<h2>Challan Not Found ❌</h2><a href='/'>Go Home</a>"

        vehicle_no = challan['reg_no']
        violation = challan['violation']
        fine = challan['fine']

        # 2. Update the Challan Status
        cursor.execute(
            "UPDATE Challan SET status='Paid', payment_mode=%s WHERE id=%s",
            (mode, challan_id)
        )

        # 3. Record the Transaction inside Payment Table
        cursor.execute(
            """
            INSERT INTO Payment (challan_id, reg_no, amount, payment_mode, transaction_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (challan_id, vehicle_no, fine, mode, f"TXN{challan_id}")
        )
        
        db.commit()

    except Exception as e:
        print("DATABASE ERROR DURING USER PAYMENT:", e)
        db.rollback()
        return "<h2>Payment Failed Due to a Server Error ❌</h2><a href='/'>Go Home</a>"
    finally:
        cursor.close()
        db.close()

    return f"""
    <script>
    alert(
        'Payment Successful ✅\\n\\n'
        + 'Challan ID : {challan_id}\\n'
        + 'Vehicle No : {vehicle_no}\\n'
        + 'Violation : {violation}\\n'
        + 'Fine : ₹ {fine}\\n'
        + 'Payment Mode : {mode}'
    );
    window.location.href='/search_result/{vehicle_no}';
    </script>
    """ 

# ---------------- SEARCH RESULT REDIRECT ---------------- #
@app.route('/search_result/<reg_no>')
def search_result(reg_no):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Challan WHERE reg_no=%s", (reg_no,))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('result.html', data=data, reg_no=reg_no)
    
# ---------------- POLICE CASH PAYMENT ---------------- #
@app.route('/police_pay', methods=['POST'])
def police_pay():
    if not is_logged_in():
        return "Unauthorized Access", 403

    challan_id = request.form['challan_id']
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE Challan SET status='Paid', payment_mode='Cash' WHERE id=%s", (challan_id,))
        cursor.execute(
            """
            INSERT INTO Payment (challan_id, reg_no, amount, payment_mode, transaction_id)
            SELECT id, reg_no, fine, 'Cash', %s FROM Challan WHERE id=%s
            """,
            (f"CASH{challan_id}", challan_id)
        )
        db.commit()

        return """
        <script>
            alert('Cash Payment Successful ✅');
            window.location.href='/police_dashboard';
        </script>
        """

    except Exception as e:
        print("ERROR PROCESSING CASH PAYMENT:", e)
        db.rollback()
        return """
        <script>
            alert('Payment Failed ❌');
            window.location.href='/police_dashboard';
        </script>
        """
    finally:
        cursor.close()
        db.close()

# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('police_login'))

# ---------------- RUN APP ---------------- #
if __name__ == '__main__':
    app.run(debug=True)