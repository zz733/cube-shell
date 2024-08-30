## cube-shell

#### 前言
大家好，我是寒暄。有一段时间没有写东西了，也没有进行技术分享。消失的这段时间，主要是在干一件事情，开发`cube-shell`。这是一个`linux`服务器的远程管理工具。功能就是我们平时开发常用到的。特点就是`UI`简洁。没有过多的菜单栏。

#### 介绍
`cube-shell`是`linux` 服务器远程管理工具，可以取代Xshell、XSftp、MobaXterm 等工具对服务器进行管理，`cube-shell` 简洁且强大。市面上大多数ssh客户端工具都是集成了很多没有用的菜单，而且ui设计十分复杂，对于初学者不太友好。

`cube-shell`的设计初衷就是简洁且实用，没有任何多余的菜单干扰我们使用。安装也很简单，解压不需要安装，直接就可以使用。

##### cube-shell有哪些功能？

**1.支持sftp协议对文件的操作**
- 下载文件（支持批量下载）
- 上传文件（支持批量上传）
- 编辑文件
- 创建文件夹
- 创建文件
- 删除文件和文件夹（支持批量删除）

![](https://files.mdnice.com/user/66248/9124f1d4-5462-4eec-884c-1cc5b47dfd79.png)

**2.支持ssh协议远程操作linux系统**
- 可以进行终端操作
- 代码高亮显示
- 命令行补全功能

![](https://files.mdnice.com/user/66248/056a4939-3ec5-40ab-b119-39671efb92a7.png)


**3.主题切换**
- `cube-shell`目前支持两种主题切换，暗主题和亮主题两种，后期会增加更多的主题选择，目前没有对终端窗口的代码高亮进行主题切换，后面也会慢慢加上去。
![](https://files.mdnice.com/user/66248/0d29efc8-97c6-46e3-b105-2ec157510b27.jpg)

![](https://files.mdnice.com/user/66248/35883985-dc06-493d-80c5-c118e264cf3a.jpg)

**4.服务器状态监控**
- CPU 使用率
- 内存使用率
- 磁盘使用率

![](https://files.mdnice.com/user/66248/3d46eab4-35cc-4372-9336-e4cd01c05230.png)


**5.查看服务进程**
- `cube-shell`支持一键查看进程

![](https://files.mdnice.com/user/66248/0005d921-b0f7-446f-8718-05778ac90561.png)

**6.支持shell脚本复制键贴执行**

- 写好的`shell`脚本可以粘进脚本区域，点击初始化就能执行脚本。脚本区域也支持 不同版本linux发行版的差异化命令行执行。

![](https://files.mdnice.com/user/66248/287525a4-3bfe-4029-a4d5-1c808788943d.png)

**7.docker容器管理**
- 停止容器
- 重启容器
- 删除容器

![](https://files.mdnice.com/user/66248/0f142a22-145c-46a0-8964-dd719230a448.png)

    
#### 软件架构
`cube-shell`主要使用`python`语言开发。

主要使用技术：
|   名字  |  版本   |  描述   |
| --- | --- | --- |
|  Python   |  3.11.9   |     |
|  PySide6  |  6.7.2   |  是C++ Qt 的Python语言绑定，支持跨平台   |
|  paramiko   |  3.4.0   |  是python的操作ssh协议和sftp协议的第三方库   |
|  QDarkStyle   |  3.2.3   |  是 支持 Qt的主题库   |
|  Pygments   |   2.18.0  |  是python代码高亮的常用库   |

**图标主要来源以下两个图标库：**

`https://icons8.com/icons/color`

`https://www.iconfont.cn/`

#### 安装教程
可以下载最新版本发行版应用程序，也可以下载源代码自行进行编译。

在编译之前首先要保证机器上要安装`python`环境。

##### 编译windows 程序
1.  安装环境
``` python
pip install pipenv
```
2.  下载依赖
``` python
//切换虚拟环境
pipenv shell
//安装依赖
pipenv install
pipenv install pyinstaller
pipenv install pywin32-ctypes
```
3.  编译打包
```
pkg.bat
```
##### 编译Mac程序
1.  安装环境
``` python
pip install pipenv
```
2.  下载依赖
``` python
//切换虚拟环境
pipenv shell
//安装依赖
pipenv install
pipenv install py2app
```
3.  编译打包
```
python setup.py py2app --strip --optimize=2
```

#### 参与贡献
欢迎各位朋友积极参与代码贡献。

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
