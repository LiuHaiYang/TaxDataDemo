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
def index():
    return render_template('index.html')


@app.route('/api/v1/feishui')
def feishui():
    return render_template('feishui.html')

@app.route('/api/v1/shouhe')
def shouhe():
    return render_template('shouhe.html')

@app.route('/api/v1/data',methods=['GET'])
def shuiwudata():
    time_now = datetime.datetime.now()
    f_date = datetime.datetime.strftime(time_now, '%Y%m%d%H%M')
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
        datefolder = 'uploadfloder' + str(f_date)
        newpath = os.path.join(file_dir, datefolder)
        os.rename(path, newpath)
        return jsonify({'code':500,'message':'读取表数据错误！'})
    try:
        if len(data_kinds) ==2:
            re = pd.merge(data_kinds[0], data_kinds[1], on='纳税人名称', how='outer')
        elif len(data_kinds) > 2:
            re = data_kinds[0]
            for d in range(len(data_kinds)-1):
                re = pd.merge(re,data_kinds[d+1], on='纳税人名称',how='outer')
        else:
            datefolder = 'uploadfloder' + str(f_date)
            newpath = os.path.join(file_dir, datefolder)
            os.rename(path, newpath)
            return jsonify({'code': 500, 'message': '请上传至少两个文件合并！！'})
    except Exception as e:
        print(e)
        datefolder = 'uploadfloder' + str(f_date)
        newpath = os.path.join(file_dir, datefolder)
        os.rename(path, newpath)
        return  jsonify({'code':500,'message':'合并表数据错误！'})
    # newpath
    downfolder = 'downfloder/dowm_'+ str(f_date)+'.xls'
    downpath = os.path.join(file_dir, downfolder)
    re.to_excel(downpath)
    datefolder = 'uploadfloder'+ str(f_date)
    newpath = os.path.join(file_dir, datefolder)
    os.rename(path,newpath)

    try:
        ## 删除上传的文件
        import shutil
        shutil.rmtree('./upload/'+f_date)
    except:
        print("删除文件失败！")

    return jsonify({'code':200,'filename':'dowm_'+f_date})

@app.route("/api/v1/exportdata/", methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    # directory = os.getcwd('upload/downfloder')  # 假设在当前目录


    return send_from_directory('upload/downfloder', str(filename)+'.xls', as_attachment=True)

@app.route("/api/v1/exportcleandata/", methods=['GET'])
def download_cleanfile():
    filename = request.args.get('filename')
    # directory = os.getcwd('upload/downfloder')  # 假设在当前目录
    return send_from_directory('upload/shouhedown', str(filename), as_attachment=True)

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


@app.route('/api/file/uploadshouhe',methods=['POST'])
def fileuploadshouhe():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    datefolder = 'shouhefloder'
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
        if 'jibenyiliao' in fname or 'duizhang' in fname:
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            unix_time = int(time.time())
            # new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
            new_filename = fname # 修改了上传的文件名
            f.save(os.path.join(folder_dir, new_filename))  # 保存文件到upload目录
            return jsonify({"code": 200, "errmsg": "上传成功",})
        else:
            return jsonify({"code":500,"errmsg":"请上传标准文件名文件！"})

@app.route('/api/v1/shouhedata',methods=['GET'])
def shouhedata():
    time_now = datetime.datetime.now()
    f_date = datetime.datetime.strftime(time_now, '%Y%m%d%H%M')
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    datefolder = 'shouhefloder'
    try:
        path = os.path.join(file_dir, datefolder)# 文件夹目录
        files = os.listdir(path)  # 得到文件夹下的所有文件名称
        if files==[]:
            return jsonify({'code':500,'message':'请上传去重数据！'})
    except Exception as e:
        # print(e)
        return jsonify({'code': 500, 'message': '请上传去重数据！'})
    try:
        exitfileyiliao = [ file for file in files if 'yiliao' in file]
        exitfileduizhang = [ file for file in files if 'duizhang' in file]

        if exitfileyiliao[0]:
            data_excel1 = './upload/shouhefloder/'+exitfileyiliao[0]
            e1 = pd.read_excel(data_excel1, skiprows=[0, 1], skipinitialspace=True)
            # e1 = e1.head(10)
            drop_rows = []
            for i, r in e1.iterrows():
                if "职工大额医疗互助保险" in str(r['征收品目']):
                    drop_rows.append(i)
            e3 = e1.drop(drop_rows)
        else:
            return jsonify({'code': 500, 'message': '请上传基本医疗表！'})

        if exitfileduizhang[0]:
            data_excel2 = './upload/shouhefloder/'+exitfileduizhang[0]
            e2 = pd.read_excel(data_excel2)
            # e2 = e2.head()
            drop_rows2 = []
            for i, r in e2.iterrows():
                if "职工基本医疗保险" in str(r['险种类型名称']):
                    pass
                else:
                    drop_rows2.append(i)
            e4 = e2.drop(drop_rows2)
        else:
            return jsonify({'code':500,'message':'请上传对账明细！'})

        excelindex = []
        for i, r in e3.iterrows():
            for j, d in e4.iterrows():
                if str(r['纳税人名称']) == str(d['缴费人名称']):
                    # print(r['纳税人名称'], d['缴费人名称'])
                    if "个人" in r['征收品目'] and float(r["实缴金额"]) != float(d['单位应缴费额个人部分']):
                        # print(r['征收品目'], r["实缴金额"], d['单位应缴费额个人部分'])
                        excelindex.append(str(r['纳税人名称'])+"---单位应缴费额个人")

                    if "单位" in r['征收品目'] and float(r["实缴金额"]) != float(d['单位应缴费额单位部分']):
                        # print(r['征收品目'], r["实缴金额"], d['单位应缴费额单位部分'])
                        excelindex.append(str(r['纳税人名称'])+"---单位应缴费单位")
        # print(excelindex)
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.txt'  # 修改了上传的文件名
        abnormal = './upload/shouhedown/down_'+new_filename
        fileObject = open(abnormal, 'w')
        for name in excelindex:
            fileObject.write(name)
            fileObject.write('\n')
        fileObject.close()
    except Exception as e:
        print(e)

    try:
        ## 删除上传的文件
        import shutil
        shutil.rmtree('./upload/shouhefloder/')
    except:
        print("删除文件失败！")

    return jsonify({'code':200,'filename':'down_'+new_filename})

if __name__ == '__main__':
    app.run(debug=True)
