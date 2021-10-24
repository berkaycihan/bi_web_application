from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators #Formlar için gerekli
from passlib.hash import sha256_crypt #parolalalarımızı encrypt etmemiz için


#kendi class'ımızı 'Form' class'ından miras alıp türetiyoruz.
class RegisterForm(Form): 
    name = StringField("Name Surname",validators=[validators.Length(min=3,max=25)]) 
    email = StringField("E-mail",validators=[validators.Email(message="invalid e-mail"),validators.DataRequired(message="e-mail needed")])
    password = PasswordField("Password",validators=[validators.DataRequired(message="password needed"),validators.EqualTo(fieldname="confirm",message="not equal")])
    confirm = PasswordField("Confirm Password") 

class LoginForm(Form): 
    email = StringField("E-mail",validators=[validators.Email(message="invalid e-mail"),validators.DataRequired(message="e-mail needed")])
    password = PasswordField("Password",validators=[validators.DataRequired(message="password needed")])
     


app = Flask(__name__)
app.secret_key="colins_bi1" #flash mesajlarını yayınlamamız için secret key atamalıyız.ne atadığımı çok önemli değil

#flask-mysql configurations
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root' #default "root":""
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="colins_bi1"

app.config['MYSQL_CURSORCLASS']="DictCursor" #Veritabanından sözlük veri yapısıyla almak için

#mysql'i dahil etmek için mysql objesi oluşturmamız gerekir.
mysql=MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/reports/<string:id>")
def detail(id):
    return "Reports ID: " + id

#sign in 
@app.route("/register",methods =["GET","POST"] )
def register():
    form = RegisterForm(request.form)
    if request.method=="POST" and form.validate():

        #Bu kısımda mysql veritabanına kayıt işlemi yapıyoruz
        name = form.name.data #string cinsinden almak için .data yazdık
        email = form.email.data
        password = sha256_crypt.encrypt( form.password.data ) #parolamızı şifreleyerek kaydediyoruz

        cursor = mysql.connection.cursor() #cursor nesnesi oluşturuyoruz

        sorgu = "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(name,email,password)) #cursor'umuza sorgu giriyoruz 
        #tek bir değer girseydik (name,) şeklindeki virgül eklememiz gerekirdi.(demet veri yapısı)

        mysql.connection.commit() #veritabanında değişiklik yaptıktan sonra commit etmemiz gerekir.

        #Son olarak mysql veritabanı cursorumuzu kapatıyoruz
        cursor.close()
        
        
        flash("The process has been completed successfully. Please login now.","primary")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)

#login page
@app.route("/login",methods=["GET","POST"])
def login():
    loginform = LoginForm(request.form)
    if request.method=="POST" and loginform.validate():
        email=loginform.email.data
        password_entered = loginform.password.data

        cursor=mysql.connection.cursor()

        sorgu = "SELECT * FROM users WHERE email = %s "  
        result = cursor.execute(sorgu,(email,))

        if result > 0 :
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
               flash(" Hello "+data['name']+". Welcome to Colin's BI.","success")
               
               session['logged_in'] = True #başarıyla giriş yapınca session atıyoruz.
               session['email'] = email

               return redirect(url_for("index"))
            else:
                 flash("Wrong password or email.","danger")
                 return redirect(url_for("login"))

        else:
            flash("There is no such a user.","danger")
            return redirect(url_for("login"))

        #flash(" Hello "+loginform.name.data+". Welcome to Colin's BI.","success")
        #flash(" Hello Berkay Cihan. Welcome to Colin's BI.","success")
        #return redirect(url_for("index"))
    
    else:
        return render_template("login.html",loginform=loginform)
    #logout işlemi
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
if __name__ == "__main__":
    app.run(debug=True)


