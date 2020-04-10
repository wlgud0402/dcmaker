from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import make_response
from uuid import uuid1
import pymysql

app = Flask(__name__, static_folder="static", template_folder="templates")

def getConnection():
  connection = pymysql.connect(
    host='localhost',
    user='root',
    passwd='123',
    db='lesson2')
  return connection

#메인페이지
@app.route("/")
def main():
    return render_template("main.html")

#회원가입페이지
@app.route("/join")
def join():
    return render_template("join.html")

#회원가입정보 받아오는 페이지
@app.route("/join_process", methods=['POST'])
def join_process():
    connection = getConnection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    name = request.form['name']
    
    uuid = str(uuid1())

    sql = "INSERT INTO members(user_id, user_pw, name, uuid) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (user_id, user_pw, name, uuid))

    connection.commit()
    connection.close()

    response = make_response(redirect("/welcome"))
    response.set_cookie("uuid", uuid)

    return response

#welcome페이지 but 쿠키위조 체크
@app.route("/welcome")
def private():
    uuid = request.cookies.get("uuid")

    if uuid == None:
        return redirect("/rejoin")

    connection = getConnection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    sql = "SELECT * FROM members where uuid=%s"
    cursor.execute(sql, (uuid))

    row = cursor.fetchone()
    connection.close()

    if row == None:
        return redirect("/warning")
    else:
        return render_template("welcome.html", member = row)

#쿠키를 위조했을때 들어오는 경고 페이지
@app.route("/warning")
def warning():
    return render_template("warning.html")

#쿠키가 제대로 발급 안되서 다시 가입해야하는 rejoin페이지
@app.route("/rejoin")
def rejoin():
    return render_template("rejoin.html")
#로그인페이지
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_process", methods=['POST'])
def login_process():
    connection = getConnection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    user_id = request.form['user_id']
    user_pw = request.form['user_pw']

    sql = "SELECT * FROM members where user_id=%s"
    cursor.execute(sql, (user_id))

    row = cursor.fetchone()
    connection.close()

    if row == None:
        return redirect("/noid")
    
    if row['user_pw'] == user_pw:
        connection = getConnection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        uuid = str(uuid1())
        response = make_response(redirect("/welcome"))
        response.set_cookie("uuid", uuid)

        sql = "UPDATE members SET uuid=%s where user_id=%s"
        cursor.execute(sql, (uuid, user_id))

        connection.commit()
        connection.close()

        return response
    else:
        return redirect("/wrongpw")
    
@app.route("/noid")
def noid():
    return render_template("noid.html")

@app.route("/wrongpw")
def wrong():
    return render_template("wrongpw.html")

#########################################################################################################################################
#글쓰기기능

@app.route("/write")
def write():
    return render_template("write.html")

@app.route("/post", methods=['POST'])
def post():
    uuid = request.cookies.get("uuid")

    if uuid == None:
        return redirect("/relogin")

    title = request.form['title']
    content = request.form['content']

    connection = getConnection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    sql = "SELECT * FROM members where uuid=%s"
    cursor.execute(sql, (uuid))

    row = cursor.fetchone()
    connection.close()

    if row == None:
        return redirect("/warning")
    else:
        connection = getConnection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "INSERT INTO boards(title, content, member_id) VALUES (%s, %s, %s)"
        cursor.execute(sql, (title, content, row['id']))

        connection.commit()
        connection.close()

        return redirect("/board")

#위의 INSERT 부분을 보면 알겠지만 boards테이블의 member_id 는 members테이블의 id 를 삽입한 것이다
#members 테이블에 있는 3번 유저가 글을 100개를 작성했을 경우 boards테이블에 있는 member_id 는 3이 100개가 있는 것이다.
@app.route("/board")
def boards():
    # uuid = request.cookies.get("uuid")

    connection = getConnection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT boards.id, boards.title, boards.content, members.name from boards join members on boards.member_id = members.id"

    cursor.execute(sql)
    rows = cursor.fetchall()
    connection.close()

    return render_template("board.html", boards=rows)


app.run(port=3000, debug=True)