import requests  
from lxml import etree
import MySQLdb
import sys
import settings
reload(sys)  
sys.setdefaultencoding('utf8')


headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-US,en;q=0.5',
	'Host': 'elective.pku.edu.cn',
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
	'Accept-Encoding': 'gzip, deflate',
	# 'Referer': 'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/CourseQueryController.jpf',
	'Referer': 'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/getCurriculmByForm.do',
	'Cookie': settings.Cookie,
	'Connection': 'keep-alive'
	}

def get(url, datas=None):
	response = requests.get(url, params=datas, headers=headers)
	content = response.text
	# print content
	return content

def post(url, datas=None):
	response = requests.post(url, params=datas, headers=headers)
	return response.text


def parse(url):
	content = get(url)
	tree = etree.HTML(content)
	title = tree.xpath('//title/text()')
	print 'title: ' + title[0].encode('utf-8')
	options = tree.xpath('//select/option/text()')
	i = 0
	for option in options:
		if i > 0 and i < 46:
			print("%d\t %s\n" % (i, option.encode('utf-8')))
			# with open("./school.data", 'a+') as f:
				# f.write("%s\n" % option.encode('utf-8'))
		i = i + 1

def parse_get_query(url):
	content = get(url)
	tree = etree.HTML(content)
	with open('./course.data', 'w') as f:
		f.truncate()
	courses = tree.xpath("//td[@class='datagrid']/span/text()")
	for course in courses:
		print course
		# with open('./course.data', 'a+') as f:
		# 	f.write("%s\n" % course)

def u2s(s):
	return s.encode("utf-8")

def crawl_undergraduate():
	# data.data stores the index of all schools
	for line in open("./data.data", "r"):
		line = line.strip("\n")
		# line = u2s(line)
		print line
		data = "wlw-radio_button_group_key%3A%7BactionForm.courseSettingType%7D=speciality&%7BactionForm.courseID%7D=&wlw-select_key"\
		"%3A%7BactionForm.deptID%7DOldValue=true&wlw-select_key%3A%7BactionForm.deptID%7D=001&%7BactionForm.credits%7D=&wlw-select_key"\
		"%3A%7BactionForm.grade%7DOldValue=true&wlw-select_key%3A%7BactionForm.grade%7D=&%7BactionForm.courseName%7D=&wlw-select_key"\
		"%3A%7BactionForm.courseDay%7DOldValue=true&wlw-select_key%3A%7BactionForm.courseDay%7D=&wlw-select_key%3A%7BactionForm.courseTime"\
		"%7DOldValue=true&wlw-select_key%3A%7BactionForm.courseTime%7D=&wlw-select_key%3A%7BactionForm.studentType%7DOldValue=true&wlw-"\
		"select_key%3A%7BactionForm.studentType%7D=&deptIdHide=" + line
		parse_post_query(url, data)


def parse_post_query(url, datas=None):
	content = post(url, datas)
	tree = etree.HTML(content)
	# with open('./course.data', 'w') as f:
	# 	f.write(content)
	tds = tree.xpath("//td[@colspan='12'][@align='right']/text()")
	try:
		pages = u2s(tds[0]).split("of")[-1].strip(" ")
		# print 'pages: ' + pages
		with open('./course1.data', 'w') as f:
			f.write(pages)
		res = pages.split("First")[0].strip(" ")
		res = res[0]
		c = int(res)
		print 'page counts: %d' % c
		# crawl page
		for i in range(c + 1):
			url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp?"\
			"netui_row=syllabusListGrid;%d" % (i * 50)
			handler(get(url))
	except Exception, e:
		print e
	# courses = tree.xpath("//td[@class='datagrid']/span/text()")
	# for course in courses:
	# 	print course


def handler(content):
	tree = etree.HTML(content)
	trs = tree.xpath("//tr[@class='datagrid-even'] | //tr[@class='datagrid-odd']")

	i = 0

	db = MySQLdb.connect(host="localhost",user="root",passwd="123",db="palmpku",charset='utf8')
	for tr in trs:
		i = i + 1
		tds = tr.xpath("td/span")
		print i
		cursor = db.cursor()

		fields = []
		for index in range(10):
			if tds[index].text != None:
				fields.append(u2s(tds[index].text))
			else:
				fields.append("")
		sql = "select 1 from undergraduate_course where name='%s' and teacher='%s' and classno='%s'" % (fields[0], fields[3], fields[4])
		cursor.execute(sql)
		if not cursor.fetchone():
			sql = "insert into undergraduate_course(name, type, xuefen, teacher, classno, school, major, grade, timeaddress, beizhu) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
				fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8], fields[9])
			print sql
			try:
			   cursor.execute(sql)
			   db.commit()
			   print 'insert successfully'
			except Exception,e:
				print Exception,":",e
				print 'insert failed'
	   			db.rollback()
   		else:
   			print "already exsit"
	db.close()	

def resovle_db():
	db = MySQLdb.connect(host="localhost", user="root", passwd="123",db="palmpku",charset="utf8")
	cursor = db.cursor()
	count = 0
	for i in range(1, 3821):
		sql = "update new_course set term = '161' where id = %d" % i
		try:
			cursor.execute(sql)
			db.commit()
		except Exception, e:
			print Exception, ":", e
		# sql = "select * from course where id = %d" % i
		# cursor.execute(sql)
		# ret = cursor.fetchone()
		# if ret != None:
		# 	new_sql = "insert into new_course(id, name, type, xuefen, teacher, classno, school, major, grade, timeaddress, beizhu, is_graduate) values (%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % (
		# 		2219 + count, ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7], ret[8], ret[9], ret[10], 1)
		# 	print new_sql
		# 	count += 1
		# 	try:
		# 		cursor.execute(new_sql)
		# 		db.commit()
		# 		print 'insert successfully'
		# 	except Exception, e:
		# 		print Exception,":",e
		# 		print 'insert failed'
	 #   			db.rollback()

			
	print count

if __name__ == '__main__':
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/CourseQueryController.jpf"
	url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/getCurriculmByForm.do"
	
	# for i in range(50):
	# 	url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp?"\
	# 	"netui_row=syllabusListGrid;%d" % (i * 50)
	# 	print url

	# crawl_undergraduate()

	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp"
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp?"\
	# "netui_row=syllabusListGrid;0"
	# parse_get_query(url)
	resovle_db()