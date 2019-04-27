#! /usr/bin/env python3
"""e Flask and then add images to a database.
"""

import MySQLdb
import private_no_share_dangerous_passwords as pnsdp
import json
import random
import requests
import time
from flask import Flask, request, render_template, url_for, redirect, make_response, g
app = Flask(__name__)

globalThreadId=0


def get_db():
	#The DB is storest in the application contect.
	db = MySQLdb.connect(host=pnsdp.DB_HOST,user=pnsdp.DB_USER,passwd=pnsdp.DB_PASSWORD, db=pnsdp.DB_DATABASE)
	return db

def execute_sql_insert(database, sql, val=None):
	cursor=database.cursor()
	if val == None:
		cursor.execute(sql)
	else:
		cursor.execute(sql, val)
	database.commit()
	cursor.close()
	database.close()

def execute_sql_select(database, sql):
	cursor=database.cursor()
	cursor.execute(sql)
	allSelects = cursor.fetchall()
	cursor.close()
	database.close()
	return allSelects

	
@app.route('/', methods=['GET','POST'])
def index():
	if "userName" in request.form.keys():
		#Create the form before loading the page
		userName = request.form["userName"]
		postString = request.form["postString"]
		id = random.randint(0,10000)
		sql = """INSERT INTO threads (threadId, threadContent, threadAuthor, threadLikes) VALUES (%s,%s, %s, %s)""" 
		val = (id, postString, userName, "0")
		execute_sql_insert(get_db(), sql,val)
		
	sql = """SELECT * FROM threads WHERE threadId IS NOT NULL;"""
	sqlTot = execute_sql_select(get_db(),sql)
	totList = []
	for row in sqlTot:
		id=int(row[0])
		post=row[1]
		author=row[2]
		likes=int(row[3])
		lineString={"id":id,"likes":likes,"author":author,"message":post}
		totList.append(lineString)
	
	'''TESTING LOCALLY: 
	totList=[]
	likes=1
	post="TestMessage"
	author="Brendan"
	id=-1
	lineString={"id":id,"likes":likes,"author":author,"message":post}
	totList.append(lineString)
	totList.append(lineString)'''
	return render_template("index.html", totStr="",list=totList)

@app.route('/thread', methods=['GET','POST'])
def thread():
	if "userName" in request.form.keys():
		#Add the comment to the DB then load the rest of page
		#Get the data from form
		userName = request.form["userName"]
		postString = request.form["postString"]
		threadid = request.form["id"]
		commentID = random.randint(1,10000)
		sql = """INSERT INTO comments (threadId,commentID, commentContent, commentAuthor, commentLikes) VALUES (%s,%s,%s,%s,%s)""" 
		val =  (threadid,commentID,postString,userName,"0")
		execute_sql_insert(get_db(), sql, val)
	print("Inside Thread Redirect")	
	print(request.form)
	#All the code to generate the comments, and message  for a specific thread
	global globalThreadId
	if globalThreadId == 0:#request.form["id"] is not None:
		threadid = request.form["id"]
	else:
		print("Inside Else")
		global globalThreadId
		threadid = globalThreadId
	sql = """SELECT * FROM comments WHERE threadId=%s;""" % (threadid)
	sqlTot = execute_sql_select(get_db(),sql)
	totList = []
	for row in sqlTot:
		commentId=row[1]
		comment=row[2]
		author=row[3]
		likes=int(row[4])
		lineString={"likes":likes,"author":author,"comment":comment,"commentid":commentId}
		totList.append(lineString)

	sql = """ SELECT threadContent FROM threads WHERE threadId=%s;""" % (threadid)
	sqlMessage=execute_sql_select(get_db(),sql)
	sqlMessage=sqlMessage[0][0]
	''' TESTING LOCALLY:
	totList=[]
	likes=1
	comment="TestMessage"
	author="Brendan"
	threadid=-1
	commentid=1
	lineString={"threadid":id,"likes":likes,"author":author,"comment":comment,"commentid":commentid}
	totList.append(lineString)'''
	return render_template("thread.html",msg=sqlMessage,listcomment=totList,threadid=threadid)

@app.route("/createthread", methods=['GET','POST'])
def create_thread():
	return render_template("create_thread.html")

@app.route("/createcomment", methods=['GET','POST'])
def create_comment():
	threadid=request.form["id"]
	return render_template("create_comment.html",threadid=threadid)


#Updates database and then redirects to the original Page.
@app.route('/upvote_thread', methods=["GET","POST"])
def upvote_thread():
	id=request.form["id"]	#Need to get the id num from form.
	sql = """UPDATE threads SET threadLikes = threadLikes + 1 WHERE threadId=%s""" % id
	execute_sql_insert(get_db(), sql, None)
	return redirect(url_for("index"), code =303)

@app.route('/upvote_comment', methods=["GET","POST"])
def upvote_comment():
	idf=request.form["id"]	#need to get the id from form.
	id=idf.split(',')[0]
	global globalThreadId 
	globalThreadId= idf.split(',')[1]
	sql ="""UPDATE comments  SET commentLikes = commentLikes + 1 WHERE commentID=%s""" % id
	execute_sql_insert(get_db(), sql, None)
	return redirect(url_for("thread"), 303)

if __name__=='__main__':
	app.run(host='0.0.0.0',port=80)
