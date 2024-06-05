- 由于本人希望在多台机子上都能使用这个工具，通过类似`python -m http.server`的方式来启动这个PyQt GUI应用，以下是发布流水账
- ### 注册PyPi账号
	- [Create an account · PyPI](https://pypi.org/account/register/)
- ### 准备发布所需的API tokens
	- [Account settings · PyPI](https://pypi.org/manage/account/)
- ### 整理项目文件结构，并编写setup.py文件
	- 参考这里的做法 [Building and Distributing Packages with Setuptools](https://setuptools.pypa.io/en/latest/userguide/)
- ### 构建发布包
	- ```sh
	  # 在包含setup.py的目录下，运行以下命令来构建包的分发文件
	  python setup.py sdist bdist_wheel
	  ```
- ### 上传发布包
	- ```sh
	  # 安装twine
	  pip install twine -i https://pypi.tuna.tsinghua.edu.cn/simple/
	  
	  # 上传构建的文件
	  twine upload dist/*
	  ```
- ### 参考资料
	- https://www.cnblogs.com/dan-baishucaizi/p/14340712.html
	- https://setuptools.pypa.io/en/latest/userguide/
	- https://setuptools.pypa.io/en/latest/userguide/entry_point.html