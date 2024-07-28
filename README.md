# 项目代码直观查看工具 visual-file

## 效果图

默认生成效果

![默认生成效果](docs/show.png)

自定义摆放后

![cannonwar-project](docs/cannonwar-project.jpg)

放大细节

![details](docs/details.jpg)

## 特点

1. 直观的展示项目文件结构，支持多层级目录结构

2. 双击矩形打开文件

3. 无限放大缩小、无边界移动、自由拖拽摆放布局并保存

## 解决痛点

项目太大，文件太多，普通的编辑器左侧列表太长，翻阅文件困难，需要一个工具来快速找到并打开文件。

我们生存在三位空间中，我们的视网膜是二维的，所以二维信息包含了上下左右等相对位置信息。更加丰富。我们可以提前把某个文件摆放在右上角

或者以一定的图案摆放，这样一看到我们自己摆放的图案，想到找某个文件就能立刻根据空间记忆立刻找到，双击即可打开。不需要再在一维的列表中来回上下翻找。

![形状自由摆放](docs/shape.jpg)

如上所示，可以把这五个ts文件根据继承关系摆放成三角形，方便快速找到。

类似 SpaceSniffer，屏幕上铺满了大大小小的嵌套的矩形框，每个矩形框代表一个文件夹或者文件，以二维的方式直观的打开项目工程文件，所有代码文件一览无余的，以二维的方式直观的展现在面前。

双击某个矩形框打开代码文件的原理：

python调用系统默认程序打开文件。直接导致编辑器里实现了打开某个代码的功能。
需要提前将ts文件的默认打开方式设置成对应的编辑器程序，比如vscode。

```
os.startfile(full_path_file)
```

## TODO:

当父矩形框扩张或者收缩的时候，兄弟矩形框应该跟着一起被推动。

为不同的后缀名文件渲染不同的图标。

当缩小到一定程度的时候，文件夹里面的内容不显示，只显示一个大的文件夹名称

手动设置排除文件列表

## 开发相关：

更新assets资源文件指令

```commandline
pyrcc5 -o assets/image.rcc -o assets/assets.py
```

打包指令

```commandline
pyinstaller --onefile --windowed --icon=./assets/favicon.ico main.py -n visual-file
```

## 布局文件格式

```js
{
	"layout": [
        {
            "kind": "directory" | "file",
            "name": "abc",  // 文件夹名字或者文件名，不需要全路径，只需要一个名字即可
            "bodyShape": {
                "width": 500,
                "height": 100,
                "locationLeftTop": [155, 4154]
            },
            "children": [
                // ...继续嵌套
            ]
        }
    ]
}
```