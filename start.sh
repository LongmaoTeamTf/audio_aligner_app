#!/bin/bash
echo "-----启动音频管理工具环境检测程序-----"
echo "-----本项目需要自行配置nginx，kaldi等工具-----"

echo "step1-检测python环境"

# python 3.6环境检测
#推荐版本V3.6.0
    V1=3
    V2=6
    V3=0
    V4=1
#获取本机python版本号。这里2>&1是必须的，python -V这个是标准错误输出的，需要转换
U_V1=`python3 -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1}'`
U_V2=`python3 -V 2>&1|awk '{print $2}'|awk -F '.' '{print $2}'`
U_V3=`python3 -V 2>&1|awk '{print $2}'|awk -F '.' '{print $3}'`
echo your python version is : $U_V1.$U_V2.$U_V3

if [ $U_V1 -lt $V1 ];then
    echo 'Your python version is not OK!,auto-update-python3.6'
    V4=0
elif [ $U_V1 -eq $V1 ];then
    if [ $U_V2 -lt $V2 ];then
        echo 'Your python version is not OK!,auto-update-python3.6'
        V4=0
    elif [ $U_V2 -eq $V2 ];then
        if [ $U_V3 -lt $V3 ];then
            echo 'Your python version is not OK!,auto-update-python3.6'
            V4=0
        fi        
    fi
fi
# 版本不正确，自动安装正确版本
if [ $V4 -eq 0 ]; then
#安装python3.6
    #yum检测
    N=yum repolist | grep 'repolist'| awk '{print $2}'
    if [ $((N)) -gt 0 ]; then
        echo "YUM源已经安装,继续安装python"
    elif [ $((N)) -eq 0 ];then
        echo "请安装对应系统版本的yum源"
        exit 1 
    fi
    #安装python3
    yum update -y
    yum install -y gcc gcc-c++ autoconf automake
    yum install -y zlib zlib-devel openssl openssl-devel pcre pcre-devel 
    mkdir /usr/local/python
    cd /usr/local/python
    # 编译环境
    yum groupinstall -y "Development tools"
    yum install -y sqlite-devel ncurses-devel ncurses-libs zlib-devel mysql-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel openssl-devel
    wget https://www.moerats.com/usr/shell/Python3/Python-3.6.4.tar.gz && tar zxvf Python-3.6.4.tar.gz && cd Python-3.6.4
    ./configure
    make&& make install
    cd ..
    rm -rf Python-3.6.4 Python-3.6.4.tar.gz
    ln -s /usr/local/python3/bin/python3 /usr/bin/python
    echo "export PATH=$PATH:$HOME/bin:/usr/local/python/bin">>~/.bash_profile
    echo "python3.6.4已安装完成"
else
    echo "python版本正确"    
fi

# 检测python依赖包，requires
echo "step2-安装requirements.txt中相关包"
pip install -r requirements.txt
 
# 检测mongo
echo "step3-配置mongo数据库"

read -p "是否需要自动安装mongo？(y/n，自动下载linux-x86_64-2.6.7):" autoInstallMongo

# 下载目录
downloadsDir=./downloads
# 安装目录
appDir=/usr/local/mongodb

#是否手动下载

if test $autoInstallMongo = 'y' 
    then
    [ ! -d $downloadsDir ] && mkdir -p $downloadsDir
    cd $downloadsDir
    # 下载mongodb
    curl -O http://downloads.mongodb.org/linux/mongodb-linux-x86_64-2.6.7.tgz
    # 解压mongodb
    tar -zxvf mongodb-linux-x86_64-2.6.7.tgz

    rm -rf $appDir
    mkdir -p $appDir

    # 复制mongodb数据库文件到$appDir目录下
    cp -R ./mongodb-linux-x86_64-2.6.7/* $appDir

    mkdir -p $appDir/data/db
    mkdir -p $appDir/log
    mkdir -p $appDir/conf
    mkdir -p $appDir/bin
    chmod -R 777 $appDir

    cd $appDir/conf
    echo "################################ ZHAOXIACE DEFINE ##############################" >> mongod.conf
    echo "port=27017  #指定服务端口号，默认端口27017" >> mongod.conf
    echo "dbpath=data #指定数据库路径" >> mongod.conf
    echo "logpath=log/mongod.log #指定MongoDB日志文件" >> mongod.conf
    echo "auth=false #启用验证" >>mongod.conf
    echo "fork=true #以守护进程的方式运行MongoDB，创建服务器进程" >> mongod.conf
    cd ../

    # 以修复模式启动
    # ./bin/mongod -f conf/mongod.conf --repair

    # 启动mongd服务
    ./bin/mongod -f conf/mongod.conf

    # 连接数据库
    ./bin/mongo
else
    echo "请自行下载安装mongoDB"
fi    
# 检测ES

# 检测ffmpeg
echo "step5-检测本机是否安装FFMPEG"
echo "step4-如有需要，请自行下载elasticsearch"
ffmpegExits=1
ffmpeg -version || ffmpegExits=0
if [ $ffmpegExits -eq 0 ]; then
    echo "检测本机未安装ffmpeg，请自行安装ffmpeg"
fi

# 中英文打点服务是否要检验kaldi
echo "step5-特点功能AI文章打点需要Kaldi环境支持，如需实际测试，需要自行进行kaldi环境的配置"

# 启动服务
echo "启动服务"
python app.py