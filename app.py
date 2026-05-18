# ============================================================
#  SUNNAH MEAT — Flask Backend  v6.0
#  + Gmail Email Notifications
# ============================================================

from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps
import sqlite3, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "sunnah-meat-secret-2025-change-this!"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "SunnahMeat@2025"

# ──────────────────────────────────────────
#  EMAIL CONFIG  ← APNI VALUES YAHAN DALO
# ──────────────────────────────────────────
ADMIN_EMAIL      = "sunnahmeat804@gmail.com"   # jis email pe notification aaye
SENDER_EMAIL     = "sunnahmeat804@gmail.com"   # Gmail account (same rakh sakte ho)
SENDER_PASSWORD  = "jqlpcbticqsmpmhk"       # Gmail App Password (16 digits, spaces hataao)
EMAIL_ENABLED    = True                         # False karo agar temporarily band karna ho

# ──────────────────────────────────────────
#  EMAIL HELPER
# ──────────────────────────────────────────
def send_email(subject, body_html):
    if not EMAIL_ENABLED:
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['From']    = SENDER_EMAIL
        msg['To']      = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Email failed: {e}")  # app crash nahi hoga

def email_new_payment(data):
    """Customer ne screenshot submit kiya"""
    send_email(
        subject=f"🔔 New Payment — {data['program']} — {data['currency']} {data['amount']}",
        body_html=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
            <div style="background:#1B4332;padding:20px;border-radius:8px 8px 0 0">
                <h2 style="color:#E8B55A;margin:0">🔔 New Payment Received</h2>
                <p style="color:rgba(250,247,240,.7);margin:5px 0 0;font-size:13px">Sunnah Meat Admin Notification</p>
            </div>
            <div style="background:#fff;padding:24px;border:1px solid #ddd;border-top:none">
                <table style="width:100%;border-collapse:collapse;font-size:14px">
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060;width:140px"><b>Customer</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data['customer_name']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Phone</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data['customer_phone']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Email</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data.get('customer_email','—')}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Program</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data['program']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Amount</b></td>
                        <td style="padding:10px;color:#1B4332;font-weight:bold;font-size:16px">{data['currency']} {data['amount']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Method</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data['payment_method']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #f0f0f0">
                        <td style="padding:10px;color:#7A7060"><b>Txn Ref</b></td>
                        <td style="padding:10px;color:#1A1A1A">{data.get('transaction_ref','—')}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px;color:#7A7060"><b>Time</b></td>
                        <td style="padding:10px;color:#1A1A1A">{datetime.now().strftime('%d %b %Y, %H:%M')}</td>
                    </tr>
                </table>
                <div style="background:#FFF8EC;border:1px solid #E8B55A;border-radius:6px;padding:12px;margin:16px 0;font-size:13px;color:#7a4e00">
                    ⏱️ <b>10 minutes remaining</b> to verify this payment before timer expires.
                </div>
                <a href="http://127.0.0.1:5000/admin#payments"
                   style="display:inline-block;background:#1B4332;color:#fff;
                          padding:12px 24px;border-radius:5px;text-decoration:none;
                          font-weight:bold;font-size:14px">
                    → Open Admin Panel to Verify
                </a>
            </div>
            <div style="background:#f5f5f5;padding:12px;border-radius:0 0 8px 8px;font-size:11px;color:#999;text-align:center">
                Sunnah Meat Admin System • Auto-generated notification
            </div>
        </div>
        """
    )

def email_payment_verified(payment_id, customer_name, program, amount, currency):
    """Admin ne verify kiya — confirmation email"""
    send_email(
        subject=f"✅ Payment Verified — #{payment_id} — {customer_name}",
        body_html=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
            <div style="background:#27AE60;padding:20px;border-radius:8px 8px 0 0">
                <h2 style="color:#fff;margin:0">✅ Payment Verified</h2>
            </div>
            <div style="background:#fff;padding:24px;border:1px solid #ddd;border-top:none;font-size:14px">
                <p>Payment <b>#{payment_id}</b> for <b>{customer_name}</b> has been marked as <b>Verified</b>.</p>
                <p>Program: {program} | Amount: {currency} {amount}</p>
            </div>
        </div>
        """
    )

# ──────────────────────────────────────────
#  SCREENSHOT UPLOAD CONFIG
# ──────────────────────────────────────────
UPLOAD_FOLDER    = os.path.join('static', 'uploads', 'payments')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER']        = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']   = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    conn = sqlite3.connect("qurbani.db")
    conn.row_factory = sqlite3.Row
    return conn

# ──────────────────────────────────────────
#  DATABASE INIT
# ──────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("qurbani.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT, phone TEXT, address TEXT,
            animal   TEXT, payment TEXT, date TEXT,
            status   TEXT DEFAULT 'Pending'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS program_requests (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT, email TEXT, phone TEXT, country TEXT,
            program TEXT, amount TEXT, message TEXT,
            date    TEXT, status TEXT DEFAULT 'Pending'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name   TEXT NOT NULL,
            customer_phone  TEXT NOT NULL,
            customer_email  TEXT,
            program         TEXT NOT NULL,
            amount          TEXT NOT NULL,
            currency        TEXT DEFAULT 'USD',
            payment_method  TEXT NOT NULL,
            transaction_ref TEXT,
            screenshot_path TEXT,
            submitted_at    TEXT NOT NULL,
            expires_at      TEXT NOT NULL,
            status          TEXT DEFAULT 'Pending',
            admin_note      TEXT,
            verified_at     TEXT
        )
    """)

    c.execute("PRAGMA table_info(bookings)")
    if 'status' not in [r[1] for r in c.fetchall()]:
        c.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Pending'")

    conn.commit()
    conn.close()

init_db()

# ──────────────────────────────────────────
#  LOGIN REQUIRED
# ──────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated

# ──────────────────────────────────────────
#  HOME
# ──────────────────────────────────────────
@app.route('/')
def home():
    return render_template("index.html")

# ──────────────────────────────────────────
#  PAYMENT PAGE
# ──────────────────────────────────────────
@app.route('/payment')
def payment_page():
    program  = request.args.get('program', 'General Donation')
    amount   = request.args.get('amount', '50')
    currency = request.args.get('currency', 'USD')
    return render_template("payment.html", program=program, amount=amount, currency=currency)

# ──────────────────────────────────────────
#  SUBMIT PAYMENT SCREENSHOT
# ──────────────────────────────────────────
@app.route('/submit-payment', methods=['POST'])
def submit_payment():
    if 'screenshot' not in request.files:
        return redirect('/payment?error=no_file')

    file = request.files['screenshot']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect('/payment?error=invalid_file')

    filename   = secure_filename(f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    filepath   = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    web_path   = filepath.replace('\\', '/')

    now      = datetime.now()
    expires  = now + timedelta(minutes=10)

    form_data = {
        'customer_name':  request.form.get('customer_name',''),
        'customer_phone': request.form.get('customer_phone',''),
        'customer_email': request.form.get('customer_email',''),
        'program':        request.form.get('program',''),
        'amount':         request.form.get('amount',''),
        'currency':       request.form.get('currency','USD'),
        'payment_method': request.form.get('payment_method',''),
        'transaction_ref':request.form.get('transaction_ref',''),
    }

    conn = sqlite3.connect("qurbani.db")
    c    = conn.cursor()
    c.execute("""
        INSERT INTO payments
        (customer_name, customer_phone, customer_email, program,
         amount, currency, payment_method, transaction_ref,
         screenshot_path, submitted_at, expires_at, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        form_data['customer_name'], form_data['customer_phone'],
        form_data['customer_email'], form_data['program'],
        form_data['amount'], form_data['currency'],
        form_data['payment_method'], form_data['transaction_ref'],
        web_path,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        expires.strftime("%Y-%m-%d %H:%M:%S"),
        'Pending'
    ))
    payment_id = c.lastrowid
    conn.commit()
    conn.close()

    # ── EMAIL NOTIFICATION TO ADMIN ──
    email_new_payment(form_data)

    return redirect(f'/payment-status/{payment_id}')

# ──────────────────────────────────────────
#  PAYMENT STATUS
# ──────────────────────────────────────────
@app.route('/payment-status/<int:payment_id>')
def payment_status(payment_id):
    conn    = get_db()
    payment = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
    conn.close()
    if not payment:
        return redirect('/')
    now     = datetime.now()
    expires = datetime.strptime(payment['expires_at'], "%Y-%m-%d %H:%M:%S")
    expired = now > expires
    return render_template("payment_status.html", payment=payment,
                           expired=expired, now=now.strftime("%Y-%m-%d %H:%M:%S"))

# ──────────────────────────────────────────
#  API: PAYMENT STATUS POLLING
# ──────────────────────────────────────────
@app.route('/api/payment-status/<int:payment_id>')
def api_payment_status(payment_id):
    conn    = get_db()
    payment = conn.execute(
        "SELECT status, expires_at, admin_note FROM payments WHERE id=?", (payment_id,)
    ).fetchone()
    conn.close()
    if not payment:
        return jsonify({'status': 'Not Found'})
    now          = datetime.now()
    expires      = datetime.strptime(payment['expires_at'], "%Y-%m-%d %H:%M:%S")
    seconds_left = max(0, int((expires - now).total_seconds()))
    return jsonify({
        'status':       payment['status'],
        'seconds_left': seconds_left,
        'expired':      now > expires,
        'admin_note':   payment['admin_note'] or ''
    })

# ──────────────────────────────────────────
#  QURBANI BOOKING
# ──────────────────────────────────────────
@app.route('/book', methods=['POST'])
def book():
    conn = sqlite3.connect("qurbani.db")
    c    = conn.cursor()
    c.execute(
        "INSERT INTO bookings (name,phone,address,animal,payment,date,status) VALUES (?,?,?,?,?,?,?)",
        (request.form['name'], request.form['phone'], request.form['address'],
         request.form['animal'], request.form['payment'],
         datetime.now().strftime("%Y-%m-%d %H:%M"), 'Pending')
    )
    conn.commit()
    conn.close()
    return redirect('/?booked=1')

# ──────────────────────────────────────────
#  PROGRAM REQUEST
# ──────────────────────────────────────────
@app.route('/program-request', methods=['POST'])
def program_request():
    conn = sqlite3.connect("qurbani.db")
    c    = conn.cursor()
    c.execute(
        "INSERT INTO program_requests (name,email,phone,country,program,amount,message,date,status) VALUES (?,?,?,?,?,?,?,?,?)",
        (request.form.get('name',''), request.form.get('email',''),
         request.form.get('phone',''), request.form.get('country',''),
         request.form.get('program',''), request.form.get('amount',''),
         request.form.get('message',''),
         datetime.now().strftime("%Y-%m-%d %H:%M"), 'Pending')
    )
    conn.commit()
    conn.close()
    return redirect('/?submitted=1')

# ──────────────────────────────────────────
#  ADMIN LOGIN / LOGOUT
# ──────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if (request.form.get('username') == ADMIN_USERNAME and
                request.form.get('password') == ADMIN_PASSWORD):
            session['logged_in'] = True
            return redirect('/admin')
        error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')

# ──────────────────────────────────────────
#  ADMIN PANEL
# ──────────────────────────────────────────
@app.route('/admin')
@login_required
def admin():
    conn             = get_db()
    bookings         = conn.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall()
    requests         = conn.execute("SELECT * FROM program_requests ORDER BY id DESC").fetchall()
    payments         = conn.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
    pending_payments = conn.execute(
        "SELECT COUNT(*) as cnt FROM payments WHERE status='Pending'"
    ).fetchone()['cnt']
    conn.close()
    now = datetime.now()
    return render_template("admin.html", bookings=bookings, requests=requests,
                           payments=payments, pending_payments=pending_payments, now=now)

# ──────────────────────────────────────────
#  ADMIN: VERIFY PAYMENT
# ──────────────────────────────────────────
@app.route('/admin/verify-payment/<int:payment_id>', methods=['POST'])
@login_required
def verify_payment(payment_id):
    action     = request.form.get('action')
    admin_note = request.form.get('admin_note', '')

    if action == 'verify':   new_status = 'Verified'
    elif action == 'reject': new_status = 'Rejected'
    else: return redirect('/admin')

    conn = get_db()
    row  = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
    conn.close()

    conn = sqlite3.connect("qurbani.db")
    conn.execute("""
        UPDATE payments SET status=?, admin_note=?, verified_at=? WHERE id=?
    """, (new_status, admin_note, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), payment_id))
    conn.commit()
    conn.close()

    # ── EMAIL on verify only ──
    if action == 'verify' and row:
        email_payment_verified(
            payment_id,
            row['customer_name'],
            row['program'],
            row['amount'],
            row['currency']
        )

    return redirect('/admin#payments')

# ──────────────────────────────────────────
#  ADMIN: DELETE PAYMENT
# ──────────────────────────────────────────
@app.route('/admin/delete-payment/<int:payment_id>')
@login_required
def delete_payment(payment_id):
    conn = get_db()
    row  = conn.execute("SELECT screenshot_path FROM payments WHERE id=?", (payment_id,)).fetchone()
    conn.close()
    if row and row['screenshot_path'] and os.path.exists(row['screenshot_path']):
        os.remove(row['screenshot_path'])
    conn = sqlite3.connect("qurbani.db")
    conn.execute("DELETE FROM payments WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()
    return redirect('/admin#payments')

# ──────────────────────────────────────────
#  EXISTING ADMIN ACTIONS
# ──────────────────────────────────────────
@app.route('/deliver/<int:id>')
@login_required
def deliver(id):
    conn = sqlite3.connect("qurbani.db")
    conn.execute("UPDATE bookings SET status='Delivered' WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/request-done/<int:id>')
@login_required
def request_done(id):
    conn = sqlite3.connect("qurbani.db")
    conn.execute("UPDATE program_requests SET status='Completed' WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    conn = sqlite3.connect("qurbani.db")
    conn.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/delete-request/<int:id>')
@login_required
def delete_request(id):
    conn = sqlite3.connect("qurbani.db")
    conn.execute("DELETE FROM program_requests WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect('/admin')

# ──────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)