#encoding: utf-8
from flask import Flask,render_template,request,jsonify,send_file,send_from_directory
from werkzeug.utils import secure_filename
import time
import os
from pypinyin import pinyin, lazy_pinyin
import base64
import datetime
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/api/v1/data',methods=['GET'])
def shuiwudata():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    datefolder = 'uploadfloder'
    try:
        path = os.path.join(file_dir, datefolder)# 文件夹目录
        files = os.listdir(path)  # 得到文件夹下的所有文件名称
        if files==[]:
            return jsonify({'code':500,'message':'请上传合并数据！'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'message': '请上传合并数据！'})
    data_kinds = []
    try:
        for file in files:  # 遍历文件夹
            data_before = pd.read_excel(path+'/'+file)
            data_df = pd.DataFrame(data_before)
            shui_name = data_df['征收项目'][0]
            data_import = data_df[['纳税人名称', '实缴金额（求和）']]
            columns = {'实缴金额（求和）': str(shui_name)}
            data_import.rename(columns=columns, inplace=True)
            data_kinds.append(data_import)
    except Exception as e:
        print(e)
        time_now = datetime.datetime.now()
        f_date = datetime.datetime.strftime(time_now, '%Y%m%d%H%M')
        datefolder = 'uploadfloder' + str(f_date)
        newpath = os.path.join(file_dir, datefolder)
        os.rename(path, newpath)
        return jsonify({'code':500,'message':'读取表数据错误！'})
    try:
        re = data_kinds[0]
        for d in range(len(data_kinds)-1):
            re = pd.merge(re,data_kinds[d+1], on='纳税人名称',how='outer')
    except Exception as e:
        print(e)
        time_now = datetime.datetime.now()
        f_date = datetime.datetime.strftime(time_now, '%Y%m%d%H%M')
        datefolder = 'uploadfloder' + str(f_date)
        newpath = os.path.join(file_dir, datefolder)
        os.rename(path, newpath)
        return  jsonify({'code':500,'message':'合并表数据错误！'})
    # newpath
    time_now = datetime.datetime.now()
    f_date = datetime.datetime.strftime(time_now, '%Y%m%d%H%M')
    downfolder = 'downfloder/dowm_'+ str(f_date)+'.xls'
    downpath = os.path.join(file_dir, downfolder)
    re.to_excel(downpath)
    datefolder = 'uploadfloder'+ str(f_date)
    newpath = os.path.join(file_dir, datefolder)
    os.rename(path,newpath)
    return jsonify({'code':200,'filename':'dowm_'+f_date})

@app.route("/api/v1/exportdata/", methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    # directory = os.getcwd('upload/downfloder')  # 假设在当前目录
    return send_from_directory('upload/downfloder', str(filename)+'.xls', as_attachment=True)

@app.route('/api/file/upload',methods=['POST'])
def fileupload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    datefolder = 'uploadfloder'
    folder_dir = os.path.join(file_dir, datefolder)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)
    f = request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        # fname = secure_filename(f.filename)
        fname = "".join(lazy_pinyin(f.filename))
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(folder_dir, new_filename))  # 保存文件到upload目录
        return jsonify({"code": 200, "errmsg": "上传成功",})

if __name__ == '__main__':
    app.run(debug=True)
