import smtplib

fromaddr = "ssspure@qq.com"
toaddrs  = "ssspure@gmail.com"
subject  = "ScrapeGoogleGUI Error Message"

# Add the From: To: and Subject: headers at the start!
msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
       % (fromaddr, toaddrs, subject))

msg = msg + "Hello World"


server = smtplib.SMTP_SSL('smtp.qq.com')
# 如果是其他的服务，只需要更改 host 为对应地址，port 对对应端口即可
# server = smtplib.SMTP_SSL(host='smtp.qq.com', port=465)
# server.set_debuglevel(1)    # 开启调试，会打印调试信息#
username = "ssspure@qq.com"
password = "plmokn321."
server.login(username, password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()