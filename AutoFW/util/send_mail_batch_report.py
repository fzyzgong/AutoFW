#encoding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_mail(report_name,execute_man,execute_time,case_total,pass_total,fail_total,skip_id):
    content = u'<!DOCTYPE html><html><head><meta charset="UTF-8"><title></title><style type="text/css">.t1 {background: greenyellow;width: 80px;text-align: center;}</style></head><body><table style="width: 400px;" border="1" cellspacing="0" cellpadding="0"><tr><td class="t1">报告名称</td><td colspan="3">'+report_name+'</td></tr><tr><td class="t1">执行人</td><td>'+execute_man+'</td><td class="t1">执行时间</td><td>'+execute_time+'</td></tr><tr><td class="t1">用例总数</td><td>'+case_total+'</td><td class="t1">成功</td><td>'+pass_total+'</td></tr><tr><td class="t1">失败</td><td style="background: red;">'+fail_total+'</td><td class="t1">跳过</td><td style="background: darkgray;">'+skip_id+'</td></tr></table></ hr></body></html>'
    msg_from = "493305356@qq.com"
    passwd = "vdiuakpsdiaubieh"
    msg_to = "fzyzgongliping@126.com"
    subject = "python 自动化测试报告"

    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = msg_from
    msg['To'] = msg_to

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
    except s.SMTPException:
        print("发送失败")
    finally:
        s.quit()

if __name__ == "__main__":
    send_mail("name", "OG", "122:32", "11", "10", "1", "0");