

from flask import *
from flask_mysqldb import MySQL
from sympy import true
from wtforms import *
from passlib.hash import sha256_crypt
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logging" in session:

            return f(*args, **kwargs)
        else:
            flash("Admin səviyyəsində giriş edin!","danger")
            return redirect(url_for("sign"))
    return decorated_function


class RegisterForm(Form):
    username=StringField("Istifadeci kodunu daxil edin", validators=[validators.DataRequired(message="Istifadeci kodunu daxil edin")])
    name=StringField("Adinizi daxil edin",validators=[validators.DataRequired("Adi daxil edin")])
    surname=StringField("Soyadinizi daxil edin",validators=[validators.DataRequired(message="Soyadi daxil edin")])
    telephone=StringField("Telefon nomresini daxil edin",validators=[validators.DataRequired(message="Telefon nomresini daxil edin")])
    address=StringField("Unvan daxil edin",validators=[validators.DataRequired(message="Unvani daxil eidn")])
    storage=StringField("Verilen anbari daxil edin",validators=[validators.DataRequired(message="Verilen anbari daxil edin")])
    password=PasswordField("Parolu daxil edin",validators=[validators.DataRequired(message="Parolu daxil edin")])

class SignForm(Form):
    username=StringField("Admin Istifadecini daxil edin",validators=[validators.DataRequired(message="Admin istifadeci kodunu daxil et")])
    password=PasswordField("Parolunuzu daxil edin",validators=[validators.DataRequired(message="Admin parolunuzu daxil edin:")])

class PurchaseForm(Form):
    content=TextAreaField("Satış tərkibini yazın!",validators=[validators.DataRequired(message="Satış tərkibini daxil edin!")])
    cost=FloatField("Məhsul və məhsulların ümümi dəyərini daxil edin!",validators=[validators.DataRequired(message="Məhsul və məhsulların ümümi dəyərini daxil edin!")])
    bonusminus=FloatField("Müştərinin bonusundan çıxmaq istədiyiniz qiyməti yazın")

class DeptForm(Form):
    payment=FloatField("Ödəyəci məbləği daxil edin!")
    debt=FloatField("Müştərinin ümümi borcu")
    content=TextAreaField("Borc tərkibi")

class BonusForm(Form):
    bonus=FloatField("Müştərinin bonusu")

class SalaryForm(Form):
    salary=FloatField("Satıcının günlük hesabatını daxil edin:")


class CreateSalary(Form):
    username=StringField("Satıcının idendifikasiya kodunu yazın",validators=[validators.DataRequired(message="Satıcıya xüsusi identifikasiya kodu əlavə edin")])
    namesurname=StringField("Satıcının adı və soyadını daxil edin",validators=[validators.DataRequired(message="Satıcının adı və soyadını daxil edin")])


class SalaryGive(Form):
    salarygive=FloatField("Satıcıya veriləcək məbləği daxil edin",validators=[validators.DataRequired(message="Satıcıya veriləcək maaşı daxil edin")])
    content=TextAreaField("Tərkib və mueyyen qaytarmalar varsa qeyd edin")





app=Flask(__name__)
app.secret_key="mmuraz_997676799"


app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="Murazturkish3353592"
app.config["MYSQL_DB"]="bonus"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)

@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
@login_required
def register():
    form=RegisterForm(request.form)

    if request.method=="POST" and form.validate():
        
        username=form.username.data
        name=form.name.data
        surname=form.surname.data
        telephone=form.telephone.data
        address=form.address.data
        storage=form.storage.data
        password=form.password.data




        cursor=mysql.connection.cursor()

        sorgu1="Insert into users(Username,Name,Surname,Telephone,Address,Storage,Password) values(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sorgu1,(username,name,surname,telephone,address,storage,password))
        mysql.connection.commit()
        cursor.close()
        flash("Qeydiyyat uğurla yerinə yetirildi...","success")
        return redirect(url_for("index"))


        
    else:
        return render_template("register.html",form=form)
    

@app.route("/sign",methods=["GET","POST"])
def sign():
    form=SignForm(request.form)

    username=form.username.data
    password_entered=form.password.data


    if request.method=="POST" and form.validate():
        cursor=mysql.connection.cursor()
        sorgu="Select * from admin where Username=%s"
        result=cursor.execute(sorgu,(username,))

        if result>0:
            data=cursor.fetchone()
            real_password=data["Password"]

            if real_password==password_entered:
                flash("Giriş uğurla başa çatdı","success")
                
                session["logging"]=True
                session["author"]=username

                return redirect(url_for("index"))
            
            else:
                flash("İstifadəçi kodu və ya parolunuz səfdir...","danger")
                return redirect(url_for("sign"))


        else:
            flash("İstifadəçi tapılmadı məlumatları düzgün daxil edin...","danger")
            return redirect(url_for("sign"))




    else:
        return render_template("sign.html",form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Admin səviyyəsindən çıxış edildi...","danger")
    return redirect(url_for("index"))

@app.route("/search",methods=["GET","POST"])
@login_required
def search():
    if request.method=="GET":
        flash("İcazən yoxdu sistem adminstrasiyası ilə əlaqə saxlayın","info")
        return redirect(url_for("index"))
    else:
        keyword=request.form.get("keyword")
        
        cursor=mysql.connection.cursor()

        sorgu="Select * from Users where Username like '%"+keyword+"%'"
        
        result=cursor.execute(sorgu)

        if result==0:
            flash("Belə bir istifadəçi tapılmadı əgər sistemdə müəyyən problemlərlə qarşılaşsanız sistem administrasiyası ilə əlaqə saxlayın","danger")
            return redirect(url_for("index"))
        else:
            data=cursor.fetchall()

            return render_template("intent.html",datam=data)

@app.route("/searchname",methods=["GET","POST"])
@login_required
def searchname():
    if request.method=="GET":
        flash("İstifadəçiyə icazə yoxdur...","danger")
        return redirect(url_for("index"))
    else:
        keyword=request.form.get("keyword")
        
        cursor=mysql.connection.cursor()

        sorgu="Select * from Users where Name like '%"+keyword+"%'"
        
        result=cursor.execute(sorgu)

        if result==0:
            flash("Belə bir istifadəçi tapılmadı əgər sistemdə müəyyən problemlərlə qarşılaşsanız sistem administrasiyası ilə əlaqə saxlayın","danger")
            return redirect(url_for("index"))
        else:
            data=cursor.fetchall()

            return render_template("intent.html",datam=data)


@app.route("/searchphone",methods=["GET","POST"])
@login_required
def searchphone():
    if request.method=="GET":
        flash("İstifadəçiyə icazə yoxdur...","danger")
        return redirect(url_for("index"))
    else:
        keyword=request.form.get("keyword")
        
        cursor=mysql.connection.cursor()

        sorgu="Select * from Users where Telephone like '%"+keyword+"%'"
        
        result=cursor.execute(sorgu)

        if result==0:
            flash("Belə bir istifadəçi tapılmadı əgər sistemdə müəyyən problemlərlə qarşılaşsanız sistem administrasiyası ilə əlaqə saxlayın","danger")
            return redirect(url_for("index"))
        else:
            data=cursor.fetchall()

            return render_template("intent.html",datam=data)

@app.route("/<string:id>",methods=["GET","POST"])
@login_required
def profile(id):
    if request.method=="POST":
        flash("İcazən olmayan əməliyyat etdin əgər bir problem yaranarsa sistem administrasiyası ilə əlaqə saxlayın","danger")
        return redirect(url_for("index"))
    else:
        cursor=mysql.connection.cursor()

        sorgu="Select * From Users where Username=%s"
        result=cursor.execute(sorgu,(id,))

        cursor2=mysql.connection.cursor()
        sorgu2="Select * from purchase where Username=%s order by ID desc"
        result2=cursor2.execute(sorgu2,(id,))

        cursor3=mysql.connection.cursor()
        sorgu3="Select * from bonus where Username=%s"
        result3=cursor3.execute(sorgu3,(id,))

        cursor4=mysql.connection.cursor()
        sorgu4="Select * from debt where Username=%s"
        result4=cursor4.execute(sorgu4,(id,))

        cursor5=mysql.connection.cursor()
        sorgu5="Select * from debt_transictions where Username=%s order by ID desc"
        result5=cursor5.execute(sorgu5,(id,))

        cursor6=mysql.connection.cursor()
        sorgu6="Select * from qaytarma where Username=%s order by ID desc"
        result6=cursor6.execute(sorgu6,(id,))




        if result==0:
            flash("Belə bir istifadəçi tapılmadı əgər sistemdə müəyyən problemlərlə qarşılaşsanız sistem administrasiyası ilə əlaqə saxlayın","danger")
            return redirect(url_for("index"))
        else:
            data=cursor.fetchall()

            purchase=cursor2.fetchall()

            bonus=cursor3.fetchone()

            debt=cursor4.fetchone()

            debt_transictions=cursor5.fetchall()

            returning=cursor6.fetchall()

            return render_template("profile.html",username=id,datam=data,purchases=purchase,bonusm=bonus,debt=debt,debt_transictions=debt_transictions,returning=returning)

@app.route("/<string:id>/purchase",methods=["GET","POST"])
@login_required
def purchase(id):
    form=PurchaseForm(request.form)
    author=session["author"]

    cursor5=mysql.connection.cursor()
    sorgu5="Select * from bonus where Username=%s"
    result5=cursor5.execute(sorgu5,(id,))

    if result5==0:
        bonus_my={"Bonus":0}
        
    else:
        bonus_my=cursor5.fetchone()
        


    if request.method=="POST" and form.validate():
        content=form.content.data
        cost=form.cost.data
        bonusminus=form.bonusminus.data

        cursor=mysql.connection.cursor()
        sorgu="Insert into purchase(Username,Author,Content,Cost,Bonus_Minus,Current_Bonus) values(%s,%s,%s,%s,%s,%s)"
        

        #Bonus Hesablayici ve yoxlama presoduru yerine yetiren
        cursor2=mysql.connection.cursor()
        sorgu1="Select * from bonus where Username=%s"
        result=cursor2.execute(sorgu1,(id,))

        if result==0:
            sorgu2="Insert into bonus(Username,Bonus) values(%s,%s)"
            bonusfirst=(cost*5)/100
            cursor2.execute(sorgu2,(id,bonusfirst))
            mysql.connection.commit()
            cursor2.close()
            bonusminus=0
            current_bonus=0
            cursor.execute(sorgu,(id,session["author"],content,cost,bonusminus,current_bonus))
            mysql.connection.commit()
            cursor.close()

            
        else:
            data=cursor2.fetchone()
            bonusreal=data["Bonus"]
            current_bonus=data["Bonus"]

            if bonusreal==bonusminus or bonusreal>bonusminus:

                bonusreal=bonusreal-bonusminus
                bonusplus=(cost*5)/100
                bonus=bonusplus+bonusreal
                sorgu3="Update bonus set Bonus=%s where Username=%s"
                cursor2.execute(sorgu3,(bonus,id))
                mysql.connection.commit()
                cursor2.close()
                cursor.execute(sorgu,(id,session["author"],content,cost,bonusminus,current_bonus))
                mysql.connection.commit()
                cursor.close()


                
            
            else:
                bonusminus=0
                cursor.execute(sorgu,(id,session["author"],content,cost,bonusminus,current_bonus))
                mysql.connection.commit()
                cursor.close()
                flash("Bonusundan çıxılmadı kifayət qədər bonusu olmadığı üçün","danger")
                return redirect(url_for("index"))
            



        flash("Satış uğurla qeydə alındı","success")
        return redirect(url_for("index"))



    else:
        return render_template("purchase.html",form=form,id=id,bonus_my=bonus_my)


@app.route("/<string:id>/debtgive",methods=["GET","POST"])
@login_required
def deptgive(id):
    form=DeptForm(request.form)
    author=session["author"]
    #payment=FloatField("Ödəyəci məbləği daxil edin!")
    #dept=FloatField("Müştərinin ümümi borcu")
    #content=TextAreaField("Borc tərkibi")

    if request.method=="POST":
        payment=form.payment.data
        debt=form.debt.data
        content=form.content.data

        cursor=mysql.connection.cursor()
        sorgu="Select * from debt where Username=%s"
        result=cursor.execute(sorgu,(id,))
        

        if result==0:
            cursor2=mysql.connection.cursor()
            sorgu2="Insert into debt(Username,Debt) values(%s,%s)"
            cursor3=mysql.connection.cursor()
            sorgu3="Insert into debt_transictions(Username,Author,Payment,Debt,Content) values(%s,%s,%s,%s,%s)"
            debt_current=debt-payment
            cursor2.execute(sorgu2,(id,debt_current))
            cursor3.execute(sorgu3,(id,session["author"],payment,debt,content))
            mysql.connection.commit()
            cursor2.close()
            cursor3.close()
            flash(f"Müştərinin borcu yaradıldı qalan borcu {debt_current}","success")
            return redirect(url_for("index"))
        
        else:
            result=cursor.fetchone()
            debt_current=result["Debt"]
            cursor2=mysql.connection.cursor()
            sorgu2="Insert into debt_transictions(Username,Author,Payment,Debt,Content) values(%s,%s,%s,%s,%s)"
            
            debt_current=debt+debt_current
            cursor2.execute(sorgu2,(id,session["author"],payment,debt_current,content))
            mysql.connection.commit()
            cursor2.close()

            debt_current=debt_current-payment
            cursor3=mysql.connection.cursor()
            sorgu3="Update debt set debt=%s where Username=%s"
            cursor3.execute(sorgu3,(debt_current,id))
            mysql.connection.commit()
            cursor3.close()


            flash(f"Borc uğurla ödəndi müştərinin ümümi qalan borcu {debt_current}","success")
            return redirect(url_for("index"))






    else:
        return render_template("debt.html",form=form)


@app.route("/<string:id>/debttake",methods=["GET","POST"])
@login_required
def debttake(id):

    form=DeptForm(request.form)

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from debt where Username=%s"
    result1=cursor1.execute(sorgu1,(id,))

    if result1==0:
        flash("Müştərinin borcu yoxdur","success")
        return redirect(url_for("index"))

    else:
        data1=cursor1.fetchone()


    if request.method=="POST":
        payment=form.payment.data

        cursor2=mysql.connection.cursor()
        sorgu2="Select * from debt where Username=%s"
        result2=cursor2.execute(sorgu2,(id,))

        current_cursor2=cursor2.fetchone()
        old_debt=current_cursor2["Debt"]

        current_debt=old_debt-payment

        cursor3=mysql.connection.cursor()
        sorgu3="Insert into debt_transictions(Username,Author,Payment) values(%s,%s,%s)"
        cursor3.execute(sorgu3,(id,session["author"],payment))
        
        mysql.connection.commit()
        cursor3.close()

        cursor4=mysql.connection.cursor()
        sorgu4="Update debt set Debt=%s where Username=%s"
        cursor4.execute(sorgu4,(current_debt,id))
        mysql.connection.commit()
        cursor4.close()

        flash(f"Müştərinin borcu {current_debt} qaldı","success")
        return redirect(url_for("index"))


    else:
        return render_template("debttake.html",data=data1,form=form)




@app.route("/telephones")
@login_required
def telephones():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from users"
    result=cursor1.execute(sorgu1)
    data=cursor1.fetchall()

    cursor1.close()

    return render_template("telephones.html",data=data,result=result)

@app.route("/debts")
@login_required
def debts():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from debt"
    result1=cursor1.execute(sorgu1)

    data=cursor1.fetchall()

    cursor1.close()

    return render_template("debts.html",data=data,result1=result1)

@app.route("/recentorder",methods=["GET","POST"])
@login_required
def recentorder():

    if request.method=="POST":
        date_min=request.form.get("date-min")
        date_max=request.form.get("date-max")

        cursor1=mysql.connection.cursor()
        sorgu1="Select * from purchase Where Author=%s and Time Between %s and %s"
        result1=cursor1.execute(sorgu1,(session["author"],date_min,date_max))
        data1=cursor1.fetchall()
        cursor1.close()
        return render_template("recentorder.html",result1=result1,data1=data1)

    else:

        author=session["author"]
        cursor1=mysql.connection.cursor()
        sorgu1="Select * from purchase where Author=%s order by ID desc"
        result1=cursor1.execute(sorgu1,(author,))
        data1=cursor1.fetchall()
        cursor1.close()

        return render_template("recentorder.html",result1=result1,data1=data1)

@app.route("/recentorders",methods=["GET","POST"])
@login_required
def recentorders():


    if request.method=="POST":
        date_min=request.form.get("date-min")
        date_max=request.form.get("date-max")

        cursor1=mysql.connection.cursor()
        sorgu1="Select * from purchase Where Time Between %s and %s"
        result1=cursor1.execute(sorgu1,(date_min,date_max))
        data1=cursor1.fetchall()
        cursor1.close()
        return render_template("recentorder.html",result1=result1,data1=data1)

    else:

        cursor1=mysql.connection.cursor()
        sorgu1="Select * from purchase order by ID desc"
        result1=cursor1.execute(sorgu1)
        data1=cursor1.fetchall()
        cursor1.close()

        return render_template("recentorder.html",result1=result1,data1=data1)


@app.route("/<string:id>/returning",methods=["GET","POST"])
@login_required
def returning(id):
    form=PurchaseForm(request.form)

    if request.method=="POST" and form.validate():
        content=form.content.data
        cost=form.cost.data
        cost=round(cost)
        author=session["author"]
        
        cursor3=mysql.connection.cursor()
        sorgu3="Insert into qaytarma(Username,Author,Cost,Content) values(%s,%s,%s,%s)"
        cursor3.execute(sorgu3,(id,session["author"],cost,content))


        mysql.connection.commit()
        cursor3.close()

        bonus_minus=(cost*5)/100

        cursor2=mysql.connection.cursor()
        sorgu2="Select * from bonus where Username=%s order by ID desc"
        result=cursor2.execute(sorgu2,(id,))
        data=cursor2.fetchone()
        real_bonus=data["Bonus"]
        cursor2.close()

        real_bonus=real_bonus-bonus_minus

        cursor3=mysql.connection.cursor()
        sorgu3="Update bonus set Bonus=%s where Username=%s"
        cursor3.execute(sorgu3,(real_bonus,id))
        mysql.connection.commit()
        cursor3.close()

        flash(f"İstifadəçinin bonusu {real_bonus} manat təşkil edir.","success")
        return redirect(url_for("index"))



    
    else:
        return render_template("returning.html",form=form)


@app.route("/salaryies",methods=["GET","POST"])
@login_required
def salaryies():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from salary"
    cursor1.execute(sorgu1)

    data=cursor1.fetchall()

    cursor1.close()
    

    if request.method=="POST":
        flash("İstifadəçi üçün icazəsi olmayan əməliyyat etdin:")
    
    else:
        return render_template("salaryies.html",data=data)


@app.route("/createsalaryies",methods=["GET","POST"])
@login_required
def createsalaryies():
    form=CreateSalary(request.form)

    if request.method=="POST" and form.validate():
        username=form.username.data
        namesurname=form.namesurname.data
        salary=0

        cursor1=mysql.connection.cursor()
        sorgu1="Select Username from salary where Username=%s"
        result=cursor1.execute(sorgu1,(username,))
        cursor1.close()

        if result==0:
            cursor2=mysql.connection.cursor()
            sorgu2="Insert into salary(Username,NameSurname,Salary) values(%s,%s,%s)"
            cursor2.execute(sorgu2,(username,namesurname,salary))

            mysql.connection.commit()
            cursor2.close()
            
            flash("Satıcı yaradıldı","success")
            return redirect(url_for("index"))

        else:
            flash("Bu istifadəçi kodlu satıcı var yeni istifadəçi kod daxil et unikal kod üçün","danger")
            return redirect(url_for("index"))


    else:
        return render_template("createsalary.html",form=form)

@app.route("/salaryies/<string:id>",methods=["GET","POST"])
@login_required
def salarydaily(id):
    form=SalaryForm(request.form)

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from salary where Username=%s"
    result=cursor1.execute(sorgu1,(id,))

    if result==0:
        flash("Belə bir satıcı tapılmadı","danger")
        return redirect(url_for("index"))
    
    else:
        data=cursor1.fetchone()
        username=data["Username"]
        namesurname=data["NameSurname"]
        current_salary=data["Salary"]
        cursor1.close()

    if request.method=="POST" and form.validate():
        salary=form.salary.data

        cursor2=mysql.connection.cursor()
        sorgu2="Insert into salary_transictions(NameSurname,Daily_Cost,Username,Author) values(%s,%s,%s,%s)"
        cursor2.execute(sorgu2,(namesurname,salary,id,session["author"]))
        mysql.connection.commit()
        cursor2.close()

        salary_calc=(salary*1)/100

        balance=salary_calc+current_salary

        cursor3=mysql.connection.cursor()
        sorgu3="Update salary set Salary=%s where Username=%s"
        cursor3.execute(sorgu3,(balance,id))
        mysql.connection.commit()
        cursor3.close()

        flash(f"Hesabına mədaxil edildi: Hal hazırki balansın {balance} təşkil edir","success")
        return redirect(url_for("index"))



    else:
        return render_template("salarydaily.html",form=form,data=data)

@app.route("/salarystatus")
@login_required
def salarystatus():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from salary"

    cursor1.execute(sorgu1)

    data=cursor1.fetchall()
    cursor1.close()

    return render_template("salarystatus.html",data=data)

@app.route("/salarystatus/<string:id>",methods=["GET","POST"])
@login_required
def salarystatusstring(id):

    form=SalaryGive(request.form)

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from salary_transictions where Username=%s order by ID desc"

    cursor1.execute(sorgu1,(id,))
    data=cursor1.fetchall()
    cursor1.close()

    

    if request.method=="POST" and form.validate():
        salarygiv=form.salarygive.data
        content=form.content.data

        cursor1=mysql.connection.cursor()
        sorgu1="Select  * from salary where Username=%s"
        cursor1.execute(sorgu1,(id,))
        datas=cursor1.fetchone()
        satici=datas["NameSurname"]
        real_salary=datas["Salary"]

        cursor1.close()

        balance=real_salary-salarygiv


        cursor2=mysql.connection.cursor()
        sorgu2="Insert into salary_transictions(NameSurname,Username,Content,Author) values(%s,%s,%s,%s)"
        cursor2.execute(sorgu2,(satici,id,content,session["author"]))
        mysql.connection.commit()
        cursor2.close()

        cursor3=mysql.connection.cursor()
        sorgu3="Update salary set Salary=%s where Username=%s"
        cursor3.execute(sorgu3,(balance,id))
        mysql.connection.commit()
        cursor3.close()

        flash(f"{satici} Balansında {balance} manat təşkil edir.")
        return redirect(url_for("index"))





        


    else:
        return render_template("salarygive.html",form=form,data=data)


@app.route("/returning")
@login_required
def returningall():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from qaytarma"
    cursor1.execute(sorgu1)
    data=cursor1.fetchall()

    return render_template("returnall.html",data=data)


@app.route("/<string:id>/edit",methods=["GET","POST"])
@login_required
def editing(id):

    form=PurchaseForm()

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from purchase where ID=%s"
    cursor1.execute(sorgu1,(id,))

    data=cursor1.fetchone()

    cursor1.close()

    form.content.data=data["Content"]
    form.cost.data=data["Cost"]

    if request.method=="POST":
        form=PurchaseForm(request.form)
        content=form.content.data
        cost=form.cost.data

        cursor2=mysql.connection.cursor()
        sorgu2="Update purchase set Content=%s,Cost=%s where ID=%s"
        cursor2.execute(sorgu2,(content,cost,id))

        mysql.connection.commit()
        cursor2.close()

        flash("Dəyişmə uğurla yerinə yetirildi","success")
        return redirect(url_for("index"))

    else:
        return render_template("editing.html",form=form)

@app.route("/<string:id>/delete",methods=["GET","POST"])
@login_required
def deletes(id):

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from purchase where ID=%s"
    cursor1.execute(sorgu1,(id,))
    data=cursor1.fetchone()
    content=data["Content"]
    cost=data["Cost"]
    old_time=data["Time"]
    old_author=data["Author"]

    cursor1.close()

    cursor2=mysql.connection.cursor()
    sorgu2="Insert into deletes(Author,Content,Cost,Old_Author,Old_Time) values(%s,%s,%s,%s,%s)"
    cursor2.execute(sorgu2,(session["author"],content,cost,old_author,old_time))
    mysql.connection.commit()
    cursor2.close()

    cursor3=mysql.connection.cursor()
    sorgu3="Delete from purchase where ID=%s"
    cursor3.execute(sorgu3,(id,))
    mysql.connection.commit()
    cursor3.close()

    flash("Satışdan silinərək silmə statusuna keçdi","success")
    return redirect(url_for("index"))

@app.route("/recentdeletes")
@login_required
def recentdeletes():

    cursor1=mysql.connection.cursor()
    sorgu1="Select * from deletes order by ID desc"
    cursor1.execute(sorgu1)
    data=cursor1.fetchall()
    cursor1.close()

    return render_template("recentdeletes.html",data=data)



@app.route("/allusers")
@login_required
def allusers():
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from users"
    cursor1.execute(sorgu1)
    data=cursor1.fetchall()

    return render_template("allusers.html",data=data)


@app.route("/allusers/edit/<string:id>",methods=["GET","POST"])
@login_required
def editusers(id):
    form=RegisterForm()
    cursor1=mysql.connection.cursor()
    sorgu1="Select * from users where Username=%s"
    cursor1.execute(sorgu1,(id,))
    data=cursor1.fetchone()
    cursor1.close()

    form.name.data=data["Name"]
    form.surname.data=data["Surname"]
    form.telephone.data=data["Telephone"]
    form.address.data=data["Address"]
    form.storage.data=data["Storage"]


    if request.method=="POST":
        form=RegisterForm(request.form)
        name=form.name.data
        surname=form.surname.data
        telephone=form.telephone.data
        address=form.address.data
        storage=form.storage.data

        cursor2=mysql.connection.cursor()
        sorgu2="Update users set Name=%s, Surname=%s, Telephone=%s, Address=%s, Storage=%s where Username=%s"
        cursor2.execute(sorgu2,(name,surname,telephone,address,storage,id))

        mysql.connection.commit()
        cursor2.close()

        flash("Məlumatlar dəyişildi","success")
        return redirect(url_for("index"))

    else:
        return render_template("usersedit.html",data=data,form=form)




