# encoding=utf8
import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import traceback
import datetime

def send_mail(report_name,execute_man,execute_time,case_total,pass_total,fail_total,skip_total,email_list):

    content = u'<!DOCTYPE html><html><head><meta charset="UTF-8"><title></title><style type="text/css">.t1 {background: greenyellow;width: 80px;text-align: center;}</style></head><body><h2 style="color: red;text-align: center;">自动化测试结果</h2><hr style="width: 400px;" /><table style="width: 400px;" border="1" cellspacing="0" cellpadding="0" align="center"><tr><td class="t1">报告名称</td><td colspan="3">'+str(report_name)+u'</td></tr><tr><td class="t1">执行人</td><td>'+str(execute_man)+u'</td><td class="t1">执行时间</td><td>'+str(execute_time)+u'</td></tr><tr><td class="t1">用例总数</td><td>'+str(case_total)+u'</td><td class="t1">成功</td><td>'+str(pass_total)+u'</td></tr><tr><td class="t1">失败</td><td style="background: red;">'+str(fail_total)+u'</td><td class="t1">跳过</td><td style="background: darkgray;">'+str(skip_total)+u'</td></tr></table></ hr></body></html>'
    msg_from = "493305356@qq.com"
    passwd = "tvlsudsnjizwbjjg"
    msg_to = email_list
    subject = "自动化测试报告--"

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(subject+str(datetime.datetime.now()), 'utf-8')
    msg['From'] = Header("493305356@qq.com", 'utf-8')
    # msg['To'] = Header("report", 'utf-8')
    msg['To'] = ','.join(msg_to) #msg[‘to’]=’,’.join(msg_to)，但是msg[[‘to’]并没有在后面被使用，这么写明显是不合理的，但是这就是stmplib的bug。你只有这样写才能群发邮件。


    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
        return "send success"
    except smtplib.SMTPException:
        print("发送失败"+str(traceback.format_exc()))
        return  "send fail"
    finally:
        s.quit()

if __name__ == "__main__":
    # send_mail("name", "OG", "122:32", "11", "10", "1", "0");
    # email_list = ['fzyzgongliping@126.com', '360393904@qq.com']
    email_list = ['1367775752@qq.com']

    send_mail(report_name="report_name", execute_man="OG", execute_time="1535", case_total="7",
              pass_total="3", fail_total="2", skip_total="1", email_list=email_list)
