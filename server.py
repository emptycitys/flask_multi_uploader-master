#!/usr/bin/env python
# coding=utf-8

import os
from flask import Flask, request, Response, render_template as rt
from flask import json,jsonify
import time
app = Flask(__name__)
#获得当前系统时间的字符串
localtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
print('localtime='+localtime)
#系统当前时间年份
year=time.strftime('%Y',time.localtime(time.time()))
#月份
month=time.strftime('%m',time.localtime(time.time()))
#日期
day=time.strftime('%d',time.localtime(time.time()))
filepath=os.getcwd()+'/upload'
fileMonth=os.getcwd()+'/upload'+'/'+year+month
print(fileMonth)
if not os.path.exists(fileMonth):
    os.mkdir(fileMonth)
    print('创建成功')
else:
    if not os.path.exists(fileMonth):
        os.mkdir(fileMonth)
file_dir = fileMonth
@app.route('/', methods=['GET'])
def index():
    return rt('./index.html')

@app.route('/check',methods=['POST'])   #第一个参数是路由，第二个是请求方法
def check_file():
    recv_data = request.get_data()  #得到前端传送的数据
    file_list = []
    for root, dirs, files in os.walk(filepath):
        file_list.append(files) #当前路径下所有非目录子文件
    return jsonify({'file_list':file_list }) #返回数据

@app.route('/file/upload', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符
    upload_file = request.files['file']
    upload_file.save(file_dir+'/%s' % filename)  # 保存分片到本地
    return rt('./index.html')

@app.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    print(target_filename)
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    print(task)
    chunk = 0  # 分片序号
    with open(file_dir+'/%s' % task+'.format', 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = file_dir+'/%s%d' % (task, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except(IOError):
                break
            chunk += 1
    chunk = 0  # 分片序号
    while True:
        try:
            filename = file_dir+'/%s%d' % (task, chunk)
            os.remove(filename)  # 删除该分片，节约空间
        except(IOError):
            break
        chunk += 1
        with open(file_dir + '/%s' % task+'.summary', 'w') as summary:  # 创建备注文件
            summary.write('IP=""\n'+'Date='+str(localtime)+'\nUid='+'\nMd5='+str(task)+'\nabsPath='+str(file_dir)+'/'+str(task)+'.format'+'\nOriginal_name='+str(target_filename))
    return rt('./index.html')
if __name__ == '__main__':
    app.run(debug=False, threaded=True)