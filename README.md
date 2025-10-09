# JISA Dashboard Backend

## install

Linux or MacOS user
``` bash
python -m venv venv
source ./venv/bin/activate

sudo yum install python-devel python3-devel mysql-devel gcc
pip install -r requirements.txt
```

Windows user
``` shell
python -m venv venv
./venv/Scripts/Activate.ps1

pip install -r requirements-win.txt
```

## run

以下のコマンドを実行すると、サーバが起動する。
swaggerはhttp://localhost:8000/docsからアクセス可能。

Linux or MacOSの場合
```
run.sh
```

Windowsの場合
```
run.bat
```


