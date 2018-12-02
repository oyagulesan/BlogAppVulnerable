from flask import Flask, render_template, json, request, redirect, session, jsonify
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import os
import uuid

mysql = MySQL()
app = Flask(__name__)
app.config.from_object('config')

mysql.init_app(app)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
    return json.dumps({'filename':f_name})

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showAddBlog')
def showAddBlog():
    if session.get('user'):
        return render_template('addBlog.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/addUpdateLike',methods=['POST'])
def addUpdateLike():
    try:
        if session.get('user'):
            _blogId = request.form['blog']
            _like = request.form['like']
            _user = session.get('user')
           

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_AddUpdateLikes',(_blogId,_user,_like))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getBlogComments')
def getBlogComments():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetCommentsByBlogId', (_id,))
            comments = cursor.fetchall()
            comments_dict = []
            for comment in comments:
                comment_dict = {
                        'Id': comment[1],
                        'Comment': blog[1],
                        'UserId': blog[2],
                        'Comment': blog[3]}
                comments_dict.append(comment_dict)
            return json.dumps(comments_dict)
        else:
            print("error : getBlog()")
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))


@app.route('/getAllBlogs')
def getAllBlogs():
    try:
        if session.get('user'):
            _user = session.get('user');
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetAllBlogs', (_user,))
            result = cursor.fetchall()
            blogs_dict = []
            for blog in result:
                blog_dict = {
                        'Id': blog[0],
                        'Title': blog[1],
                        'Description': blog[2],
                        'FilePath': blog[3],
                        'SumLikes' : blog[4],
                        'HasLikes' : blog[5],
                        'UserName': blog[6]}
                blogs_dict.append(blog_dict)       
 
            return json.dumps(blogs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/showDashboard')
def showDashboard():
    if session.get('user'):
        return render_template('dashboard.html')
    else:
        return render_template('error.html', error='Unauthorized Access')


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/deleteBlog', methods=['POST'])
def deleteBlog():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteBlog', (_id, _user))
            result = cursor.fetchall()

            if len(result) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/getBlogById',methods=['POST'])
def getBlogById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetBlogById',(_id,_user))
            result = cursor.fetchall()

            blog = []
            #blog.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2]})
            blog.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2],'FilePath':result[0][3],'Private':result[0][4],'Done':result[0][5]})

            return json.dumps(blog)
        else:
            print("fail getBlogById()")
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/getBlog')
def getBlog():
    try:
        if session.get('user'):
            _user = session.get('user')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetBlogByUser',(_user,))
            blogs = cursor.fetchall()
            blogs_dict = []
            for blog in blogs:
                blog_dict = {
                        'Id': blog[0],
                        'Title': blog[1],
                        'Description': blog[2],
                        'Date': blog[4]}
                blogs_dict.append(blog_dict)
            return json.dumps(blogs_dict)
        else:
            print("error : getBlog()")
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/addBlog',methods=['POST'])
def addBlog():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')

            if request.form.get('filePath') is None:
                _filePath = ''
            else:
                _filePath = request.form.get('filePath')
            if request.form.get('private') is None:
                _private = 0
            else:
                _private = 1
            if request.form.get('done') is None:
                _done = 0
            else:
                _done = 1            

            conn = mysql.connect()
            cursor = conn.cursor()
            #cursor.callproc('sp_addBlog',(_title,_description,_user))
            cursor.callproc('sp_addBlog',(_title,_description,_user,_filePath,_private,_done))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/updateBlog', methods=['POST'])
def updateBlog():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _description = request.form['description']
            _blog_id = request.form['id']
            _filePath = request.form['filePath']
            _isPrivate = 0 #request.form['isPrivate']
            _isDone = 0 #request.form['isDone']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_updateBlog',(_title,_description,_blog_id,_user,_filePath,_isPrivate,_isDone))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
    except Exception as e:
        print('................')
        print(e)
        return json.dumps({'status':'Unauthorized access'})
    finally:
        cursor.close()
        conn.close()

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
               
        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
                #return redirect('/showDashboard')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')          

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                print("..... sign up called...")
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                print("..... sign up called...fail....")
                return json.dumps({'error':str(data[0])})
        else:
            print("..... sign up called...fail...... else.")
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        print("..... sign up called.. exception.", e, len(_hashed_password))
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
