# Dokumentasjon til bok oversetter
## Beskrivelse
Dette er en nettside der man kan registrere en bruker, og logge inn med brukeren for å få tilgang til innholdet. Når brukeren er logget inn, kan man gå inn på oversetter siden, der man skriver en tilfeldig bok man vil få oversettes, og kan man vegle noen forskjellige språk til oversetteren. Når man bestiller det, blir man sendt til en side der man blir bekrefta at bestillingen har blitt sendt.  
Hvis man er logget inn med brukernavn Geir Petter Torgersen, har man tilgang til adminsiden, der man kan se brukere, og bestillinger som brukere har sendt inn. Man kan også slette brukere og bestillinger om man ønsker fra siden.  
Dette er laget med Flask og mariadb database

## Database
Detabasen er laget i MariaDb. Den har 2 tabeller, "user", som inneholder brukere, og "bestillinger", som inneholder bestillinger. 
  
  MariaDb databasen er lokalt på pc-en så jeg bruker localhost til å bruke den. Dette er hvordan den blir kobla til:
``` python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'jakob-flask',
    'password': '123',
    'database': 'bok_oversetter'
}
```

Dette er hvordan tabellene er bygget opp:
``` sql
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
```
``` sql
CREATE TABLE bestillinger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    bok VARCHAR(255) NOT NULL,
    bestill VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
```
Dette er hovedmåten jeg henter, legger til og sletter fra databasen i Python koden. Jeg trenger bare å 
``` Python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM user WHERE id = %s"(brukerid,))
conn.commit()
cursor.close()
conn.close()
```
## Logg inn
For innlogging bruker jeg flask_login biblioteket.
På register siden, så har jeg en form som sender inn en POST request med brukernavn og passord, det blir da lagt til å databasen:
``` python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
       
        return redirect(url_for('login'))
       
    return render_template('register.html')
```
I Logg inn siden, så sender det en POST request som sjekker om brukernavnet og passordet jeg la sendte, har en bruker koblet til i databasen, også logger den meg inn om det er riktig:
``` python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):   
            user_obj = User(id=user[0], username=user[1])
            login_user(user_obj)
            return redirect(url_for('home'))
            
    return render_template('login.html')
```
Jeg har også en logg ut knapp som logger ut brukeren:
``` python
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
```
## Admin side
Jeg har ikke laget roller til brukerene, så jeg valgte å gi tilgang til admin siden, til brukeren som heter "Geir Petter Torgersen":
``` python
@app.route('/adminside')
@login_required
def adminside():
    
    if current_user.username != "Geir Petter Torgersen":  
        return redirect(url_for('home'))  

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password, created_at FROM user")
    users = cursor.fetchall()
    cursor.execute("SELECT id, username, bok, bestill, created_at FROM bestilling")
    bestillinger = cursor.fetchall()

    cursor.close()
    conn.close()
     
    return render_template('adminside.html', users=users, bestillinger=bestillinger)
```
I admin siden, så henter jeg dataen fra begge tabellene, og legger de inn i siden. Fra siden kan jeg også slette dataen:
``` python
@app.route('/delete', methods=['POST'])
def slett():
    navn = request.form['navn']
    brukerid = request.form['brukerid']
    if navn != "Geir Petter Torgersen":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (brukerid,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('adminside'))
    else:
        return redirect(url_for('adminside'))
```
Her har jeg også gjort at man ikke kan slette brukeren til Geir.
## Bestilling
I bestiling siden, kan man skrive en frivillig bok man vil få oversettes, også kan man velge mellom 6 språk. Når man sender det, blir det sendt en POST request, som legger til dataen i bestilling tabellen:
``` python
@app.route('/oversetter', methods=['GET', 'POST'])
@login_required
def oversetter():
    if request.method == 'POST':
        username = current_user.username  
        bok = request.form['bok']
        bestilling = request.form['bestilling']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bestilling (username, bok, bestill) VALUES (%s, %s, %s)", (username, bok, bestilling))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('kvittering'))

    return render_template('bestill.html')
```
Formen:
``` html
<form method="POST" action="{{url_for('oversetter')}}">
        <p>Hvilken bok:</p>
        <input type="text" name="bok">
        <p>Hva er din bestilling:</p>
        <select name="bestilling" id="">
            <option value="Engelsk">Engelsk</option>
            <option value="Spansk">Spansk</option>
            <option value="Fransk">Fransk</option>
            <option value="Tysk">Tysk</option>
            <option value="Arabisk">Arabisk</option>
            <option value="Russisk">Russisk</option>
        </select>
        <button type="submit">Lagre bestilling</button>
    </form>
```
Når dataen blir lagt inn i tabellen, så går det til kvittering siden, som bare sier at bestillingen har blitt sendt, og at Geir kan se den.

## Ting
Stylingen er AI generert, med  det er fordi det ikke var hovedpoenget med dette prosjektet, og jeg ville ikke bruke for mye tid på dette.
Jeg er fornøyd med nettsiden, og den funker akkuratt som den skal.
