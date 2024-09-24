# Database

### 安装依赖

原来的 requirements.txt 应该是你本机的所有 python 依赖，我 pull 代码之后直接安装依赖和我本机已有的第三方包有冲突，没法把项目跑起来。

创建虚拟环境，然后安装依赖，这样不会有版本冲突问题。

``` bash
# 创建虚拟环境, 环境名为 myenv，可随意取, 在项目根目录下可以看到自动新建了一个目录 myenv
$ python3 -m venv myenv
# 激活虚拟环境 myenv, 也就是进入该虚拟环境
$ source myenv/bin/activate
# 在虚拟环境里面安装依赖, 依赖只会安装在当前目录下, 就不会安装到全局目录下避免造成版本冲突
$ pip install -r requirements.txt
# 退出虚拟环境
$ deactivate
```

### 本地运行

``` bash
$ flask --app=api/main run
```

### 修改点

1. 修改 requirements.txt 

原来的 requirements.txt 有很多都是这个项目没有用到的，精简了一下依赖，requirements.txt 只保留该项目用到的依赖。

2. 环境变量文件

将文件 `url.env` 修改为 `.env`

原先的数据库连接信息我看到放在 url.env 文件中，实际运行程序并没有从 url.env 中成功获取数据库连接信息。

可以参阅 [python-dotenv](https://pypi.org/project/python-dotenv/) 文档，环境变量应当放在根目录下的 .env 文件中，实际测试是生效的

> mysql 之前的连接信息为: `mysql+mysqldb://user:pwd@host:port/db_name`
> 
> mysql+ 后面的是驱动名称，之前文件里写的是 mysqldb，我本机启动程序会一直报错。你那边能运行起来，我猜测可能你本地有安装什么其它依赖所以可以。
>
> 我调研了一下如果使用 mysqlclient 驱动，那么连接前缀是 mysql+mysqlconnector:// 这个我本地无法安装 mysqlclient，没法测试。
>
> 如果使用 pymysql 驱动，那么连接前缀是 mysql+pymysql:// 这个我本地成功安装，测试连接也是成功的。

3. 添加 .gitignore 文件

类似环境变量文件 .env (里面有数据库敏感信息)，还有 python 一些缓存文件 (本地运行程序自动生成的)，虚拟环境一些依赖文件是不需要上传到 github 的。

4. 修改 api/main.py 文件

把里面的 DATABASES 变量里面的数据库敏感信息删掉，直接从环境变量中获取。

删除 api/main.py 中的如下代码

``` python
# Flask 的处理函数 (Vercel 部署使用)
def handler(event, context):
    with app.app_context():
        return app(event, context)
```

5. 修改 vercel.json 文件

之前你的 vercel.json 文件只是配置静态资源，在页面上表现就是能看到 index.html 内容，但是里面的 `{{ message }}` 变量没有被值替换。

将下面代码替换 vercel.json 文件，这样部署的就是动态网页了。

``` json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/main" }
  ]
}
```