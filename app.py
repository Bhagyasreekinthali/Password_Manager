from flask import Flask, request, render_template_string, redirect, url_for, session
from cryptography.fernet import Fernet
import random
import string

app = Flask(__name__)
app.secret_key = "password-manager-demo-secret-key"


# ---------------- ENCRYPTION ----------------

try:
    with open("secret.key", "rb") as file:
        encryption_key = file.read()
except FileNotFoundError:
    encryption_key = Fernet.generate_key()

    with open("secret.key", "wb") as file:
        file.write(encryption_key)

cipher = Fernet(encryption_key)


def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(password):
    try:
        return cipher.decrypt(password.encode()).decode()
    except:
        return password


# ---------------- MASTER PASSWORD ----------------

def get_master_password():
    try:
        with open("master_password.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "123456"


def save_master_password(password):
    with open("master_password.txt", "w") as file:
        file.write(password)


# ---------------- ACCOUNTS ----------------

def load_accounts():
    accounts = []

    try:
        with open("accounts.txt", "r") as file:
            for line in file:
                parts = line.strip().split("|")

                if len(parts) == 3:
                    website = parts[0]
                    username = parts[1]
                    password = decrypt_password(parts[2])

                    accounts.append({
                        "website": website,
                        "username": username,
                        "password": password
                    })

    except FileNotFoundError:
        pass

    return accounts


def save_accounts(accounts):
    with open("accounts.txt", "w") as file:
        for account in accounts:
            encrypted_password = encrypt_password(account["password"])

            file.write(
                f'{account["website"]}|'
                f'{account["username"]}|'
                f'{encrypted_password}\n'
            )


# ---------------- PASSWORD STRENGTH ----------------

def password_strength(password):

    score = 0

    if len(password) >= 12:
        score += 1

    if any(char.isupper() for char in password):
        score += 1

    if any(char.islower() for char in password):
        score += 1

    if any(char.isdigit() for char in password):
        score += 1

    if any(char in "@#$%!" for char in password):
        score += 1

    if score >= 5:
        return "Strong"

    elif score >= 3:
        return "Medium"

    else:
        return "Weak"


# ---------------- HTML ----------------

PAGE = """
<!DOCTYPE html>
<html>

<head>

<title>Password Manager</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #dbeafe, #eef2ff);
    margin: 0;
    padding: 30px;
    color: #1e293b;
}

.container {
    max-width: 950px;
    margin: auto;
}

h1 {
    text-align: center;
    color: #1e3a8a;
}

h2 {
    color: #1e40af;
}

.card {
    background: white;
    padding: 25px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.12);
}

input {
    width: 95%;
    padding: 11px;
    margin: 7px 0;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

button {
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background: #2563eb;
    color: white;
    margin: 5px;
}

button:hover {
    background: #1d4ed8;
}

.danger {
    background: #dc2626;
}

.danger:hover {
    background: #b91c1c;
}

.green {
    background: #16a34a;
}

.account-card {
    background: #f8fafc;
    padding: 20px;
    margin: 15px 0;
    border-radius: 12px;
    border-left: 5px solid #2563eb;
}

.message {
    padding: 12px;
    background: #dcfce7;
    color: #166534;
    border-radius: 8px;
}

.error {
    padding: 12px;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 8px;
}

.password {
    font-family: monospace;
    letter-spacing: 2px;
}

.logout {
    float: right;
    background: #64748b;
}

.strength {
    font-weight: bold;
}

</style>

<script>

function togglePassword(number, password, button) {

    const passwordElement =
        document.getElementById("password" + number);

    if (passwordElement.textContent === "****") {

        passwordElement.textContent = password;
        button.textContent = "Hide Password";

    } else {

        passwordElement.textContent = "****";
        button.textContent = "Show Password";

    }
}


function copyPassword(password) {

    navigator.clipboard.writeText(password);

    alert("Password copied to clipboard!");

}

</script>

</head>


<body>

<div class="container">

<h1>🔐 Password Manager</h1>


{% if session.get("logged_in") %}

<a href="/logout">
<button class="logout">Logout</button>
</a>


<div class="card">

<h2>Welcome</h2>

<p>Your passwords are protected using encryption.</p>

</div>


<div class="card">

<h2>➕ Add Account</h2>

<form method="POST" action="/add">

<input
type="text"
name="website"
placeholder="Website"
required
>

<input
type="text"
name="username"
placeholder="Username"
required
>

<input
type="password"
name="password"
placeholder="Password"
required
>

<button type="submit">Add Account</button>

</form>

</div>


<div class="card">

<h2>🔎 Search Account</h2>

<form method="GET" action="/">

<input
type="text"
name="search"
placeholder="Search website"
value="{{ search }}"
>

<button type="submit">Search</button>

</form>

</div>


<div class="card">

<h2>📋 Your Accounts</h2>

{% if accounts %}

{% for account in accounts %}

<div class="account-card">

<p>
<b>Website:</b>
{{ account.website }}
</p>

<p>
<b>Username:</b>
{{ account.username }}
</p>

<p>
<b>Password:</b>

<span
class="password"
id="password{{ loop.index }}"
>
****
</span>

<button
type="button"
onclick='togglePassword(
{{ loop.index }},
{{ account.password|tojson }},
this
)'
>
Show Password
</button>

<button
type="button"
class="green"
onclick='copyPassword(
{{ account.password|tojson }}
)'
>
Copy Password
</button>

</p>


<form
method="POST"
action="/delete"
style="display:inline;"
>

<input
type="hidden"
name="website"
value="{{ account.website }}"
>

<button
class="danger"
type="submit"
>
Delete
</button>

</form>


<form
method="POST"
action="/update"
>

<input
type="hidden"
name="old_website"
value="{{ account.website }}"
>

<input
type="text"
name="username"
placeholder="New username"
required
>

<input
type="password"
name="password"
placeholder="New password"
required
>

<button type="submit">
Update
</button>

</form>

</div>

{% endfor %}

{% else %}

<p>No accounts found.</p>

{% endif %}

</div>


<div class="card">

<h2>🔑 Generate Password</h2>

<form method="POST" action="/generate">

<input
type="number"
name="length"
placeholder="Password length"
min="6"
value="12"
required
>

<button type="submit">
Generate
</button>

</form>

{% if generated_password %}

<p>
<b>Generated Password:</b>
</p>

<p class="password">
{{ generated_password }}
</p>

<p>
<b>Strength:</b>
<span class="strength">
{{ generated_strength }}
</span>
</p>

{% endif %}

</div>


<div class="card">

<h2>🛡️ Password Strength Checker</h2>

<form method="POST" action="/strength">

<input
type="password"
name="password"
placeholder="Enter password"
required
>

<button type="submit">
Check Strength
</button>

</form>

{% if checked_strength %}

<p>
Password Strength:
<b>{{ checked_strength }}</b>
</p>

{% endif %}

</div>


<div class="card">

<h2>🔐 Change Master Password</h2>

<form method="POST" action="/change-master">

<input
type="password"
name="new_password"
placeholder="New master password"
required
>

<input
type="password"
name="confirm_password"
placeholder="Confirm master password"
required
>

<button type="submit">
Change Password
</button>

</form>

</div>


{% else %}


<div class="card">

<h2>🔒 Master Login</h2>

<form method="POST" action="/login">

<input
type="password"
name="password"
placeholder="Enter master password"
required
>

<button type="submit">
Login
</button>

</form>

{% if error %}

<p class="error">
{{ error }}
</p>

{% endif %}

</div>


{% endif %}


{% if message %}

<div class="message">
{{ message }}
</div>

{% endif %}


</div>

</body>

</html>
"""


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET"])
def home():

    if not session.get("logged_in"):

        return render_template_string(
            PAGE,
            error="",
            message="",
            accounts=[],
            search="",
            generated_password="",
            generated_strength="",
            checked_strength=""
        )


    accounts = load_accounts()

    search = request.args.get("search", "")

    if search:

        accounts = [
            account
            for account in accounts
            if search.lower() in account["website"].lower()
        ]


    return render_template_string(
        PAGE,
        error="",
        message="",
        accounts=accounts,
        search=search,
        generated_password="",
        generated_strength="",
        checked_strength=""
    )


@app.route("/login", methods=["POST"])
def login():

    password = request.form["password"]

    if password == get_master_password():

        session["logged_in"] = True

        return redirect(url_for("home"))

    return render_template_string(
        PAGE,
        error="Incorrect master password!",
        message="",
        accounts=[],
        search="",
        generated_password="",
        generated_strength="",
        checked_strength=""
    )


# ---------------- ADD ACCOUNT ----------------

@app.route("/add", methods=["POST"])
def add_account():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    website = request.form["website"]
    username = request.form["username"]
    password = request.form["password"]

    accounts = load_accounts()

    for account in accounts:

        if account["website"].lower() == website.lower():

            return render_template_string(
                PAGE,
                error="Account already exists!",
                message="",
                accounts=accounts,
                search="",
                generated_password="",
                generated_strength="",
                checked_strength=""
            )


    accounts.append({
        "website": website,
        "username": username,
        "password": password
    })

    save_accounts(accounts)

    return redirect(url_for("home"))


# ---------------- DELETE ACCOUNT ----------------

@app.route("/delete", methods=["POST"])
def delete_account():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    website = request.form["website"]

    accounts = load_accounts()

    accounts = [
        account
        for account in accounts
        if account["website"].lower() != website.lower()
    ]

    save_accounts(accounts)

    return redirect(url_for("home"))


# ---------------- UPDATE ACCOUNT ----------------

@app.route("/update", methods=["POST"])
def update_account():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    old_website = request.form["old_website"]
    username = request.form["username"]
    password = request.form["password"]

    accounts = load_accounts()

    for account in accounts:

        if account["website"].lower() == old_website.lower():

            account["username"] = username
            account["password"] = password

            break

    save_accounts(accounts)

    return redirect(url_for("home"))


# ---------------- GENERATE PASSWORD ----------------

@app.route("/generate", methods=["POST"])
def generate_password():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    length = int(request.form["length"])

    if length < 6:
        length = 6

    characters = (
        string.ascii_letters
        + string.digits
        + "@#$%!"
    )

    password = ""

    for i in range(length):
        password += random.choice(characters)

    strength = password_strength(password)

    accounts = load_accounts()

    return render_template_string(
        PAGE,
        error="",
        message="",
        accounts=accounts,
        search="",
        generated_password=password,
        generated_strength=strength,
        checked_strength=""
    )


# ---------------- STRENGTH CHECKER ----------------

@app.route("/strength", methods=["POST"])
def check_strength():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    password = request.form["password"]

    strength = password_strength(password)

    accounts = load_accounts()

    return render_template_string(
        PAGE,
        error="",
        message="",
        accounts=accounts,
        search="",
        generated_password="",
        generated_strength="",
        checked_strength=strength
    )


# ---------------- CHANGE MASTER PASSWORD ----------------

@app.route("/change-master", methods=["POST"])
def change_master():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    accounts = load_accounts()

    if new_password != confirm_password:

        return render_template_string(
            PAGE,
            error="Master passwords do not match!",
            message="",
            accounts=accounts,
            search="",
            generated_password="",
            generated_strength="",
            checked_strength=""
        )


    save_master_password(new_password)

    return render_template_string(
        PAGE,
        error="",
        message="Master password changed successfully!",
        accounts=accounts,
        search="",
        generated_password="",
        generated_strength="",
        checked_strength=""
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- START APP ----------------

if __name__ == "__main__":
    app.run(debug=True)