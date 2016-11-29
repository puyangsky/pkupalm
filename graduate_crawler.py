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
	courses = tree.xpath("//td[@class='datagrid']/span/text()")
	with open('./course.data', 'w') as f:
		f.truncate()
	for course in courses:
		print course
		with open('./course.data', 'a+') as f:
			f.write("%s\n" % course)

def u2s(s):
	return s.encode("utf-8")

def parse_post_query(url, datas=None):
	content = post(url, datas)
	# with open('./tmp.html', 'w') as f:
	# 	f.write(content)
	tree = etree.HTML(content)
	# courses = tree.xpath("//td[@class='datagrid']/span/text()")
	trs = tree.xpath("//tr[@class='datagrid-even'] | //tr[@class='datagrid-odd']")
	# print type(trs)
	# with open('./course.data', 'w') as f:
	# 	f.truncate()
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



if __name__ == '__main__':
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/CourseQueryController.jpf"
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/getCurriculmByForm.do"
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp?"\
	# "netui_row=syllabusListGrid;50"
	for i in range(50):
		url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp?"\
		"netui_row=syllabusListGrid;%d" % (i * 50)
		print url
		parse_post_query(url)
	# url = "http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/courseQuery/queryCurriculum.jsp"
	# parse_get_query(url)